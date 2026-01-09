"""
Reproduce stimuli for "Perceptual comparisons modulate memory biases induced by new visual inputs".

This script reads per-trial MATLAB .mat data and renders the key visual stimuli
for each trial (memory item, probe, and response wheels) using stimkit.
"""
from __future__ import annotations

import sys
import tomllib
import argparse
import random
from pathlib import Path
from typing import Iterable
import multiprocessing as mp
import os

import numpy as np
import scipy.io as sio
import matplotlib.patches as patches
import matplotlib.transforms as transforms
from tqdm import tqdm

from loguru import logger

from stimkit import Canvas, CanvasConfig, OutputConfig, Renderer, Pixel
from config import (
    StimuliAppConfig,
    TrialData,
    SceneConfig,
    StimulusType,
    TaskType,
    Phase,
    ExperimentName,
)

logger.remove()
logger.add(sys.stderr, level="INFO")

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"
CONFIG_PATH = SCRIPT_DIR / "stimuli_config.toml"


# ==============================================================================
# Color + Shape Utilities
# ==============================================================================
D65_WHITE = (0.95047, 1.0, 1.08883)


def _lab_to_xyz(l_star: float, a_star: float, b_star: float) -> tuple[float, float, float]:
    fy = (l_star + 16.0) / 116.0
    fx = fy + (a_star / 500.0)
    fz = fy - (b_star / 200.0)

    delta = 6.0 / 29.0

    def f_inv(t: float) -> float:
        if t > delta:
            return t ** 3
        return 3 * (delta ** 2) * (t - 4.0 / 29.0)

    x = D65_WHITE[0] * f_inv(fx)
    y = D65_WHITE[1] * f_inv(fy)
    z = D65_WHITE[2] * f_inv(fz)
    return x, y, z


def _xyz_to_srgb(x: float, y: float, z: float) -> tuple[float, float, float]:
    r_lin = 3.2406 * x - 1.5372 * y - 0.4986 * z
    g_lin = -0.9689 * x + 1.8758 * y + 0.0415 * z
    b_lin = 0.0557 * x - 0.2040 * y + 1.0570 * z

    def gamma(u: float) -> float:
        if u <= 0.0031308:
            return 12.92 * u
        return 1.055 * (u ** (1.0 / 2.4)) - 0.055

    r = gamma(max(0.0, r_lin))
    g = gamma(max(0.0, g_lin))
    b = gamma(max(0.0, b_lin))
    return (min(1.0, max(0.0, r)), min(1.0, max(0.0, g)), min(1.0, max(0.0, b)))


def lab_to_srgb(l_star: float, a_star: float, b_star: float) -> tuple[float, float, float]:
    x, y, z = _lab_to_xyz(l_star, a_star, b_star)
    return _xyz_to_srgb(x, y, z)


def build_color_wheel(cfg: StimuliAppConfig) -> list[tuple[float, float, float]]:
    colors: list[tuple[float, float, float]] = []
    for idx in range(cfg.color_space.count):
        theta = 2 * np.pi * (idx / cfg.color_space.count)
        a_star = cfg.color_space.a_center + cfg.color_space.radius * np.cos(theta)
        b_star = cfg.color_space.b_center + cfg.color_space.radius * np.sin(theta)
        colors.append(lab_to_srgb(cfg.color_space.l_star, a_star, b_star))
    return colors


def generate_shape_points(index: int, point_count: int = 220) -> np.ndarray:
    """
    Approximate a continuous shape space by morphing radial-frequency shapes.

    This is an approximation because the Li et al. (2020) shape set is not
    included in the dataset. Shapes are generated deterministically from index.
    """
    phi = 2 * np.pi * ((index - 1) % 360) / 360.0
    thetas = np.linspace(0, 2 * np.pi, point_count, endpoint=False)

    freqs = np.array([2, 3, 5, 7], dtype=float)
    base_cos = np.array([0.18, 0.12, 0.10, 0.08])
    base_sin = np.array([0.12, -0.10, 0.09, -0.07])

    cos_coeff = base_cos * np.cos(phi)
    sin_coeff = base_sin * np.sin(phi)

    r = np.ones_like(thetas)
    for freq, c_coef, s_coef in zip(freqs, cos_coeff, sin_coeff):
        r += c_coef * np.cos(freq * thetas) + s_coef * np.sin(freq * thetas)

    r = np.clip(r, 0.35, None)
    x = r * np.cos(thetas)
    y = r * np.sin(thetas)
    return np.column_stack([x, y])


def precompute_shape_templates(count: int) -> list[np.ndarray]:
    return [generate_shape_points(i + 1) for i in range(count)]


# ==============================================================================
# Data Loading
# ==============================================================================

def _flatten_field(value: np.ndarray) -> np.ndarray:
    return np.asarray(value).reshape(-1)


def infer_task_type(file_name: str) -> TaskType:
    if "ignore" in file_name:
        return TaskType.IGNORE
    if "recog" in file_name:
        return TaskType.COMPARE
    if "recall" in file_name:
        return TaskType.REMEMBER
    raise ValueError(f"Unrecognized task type in filename: {file_name}")


def infer_stimulus_type(file_name: str) -> StimulusType:
    if "color" in file_name:
        return StimulusType.COLOR
    if "shape" in file_name:
        return StimulusType.SHAPE
    raise ValueError(f"Unrecognized stimulus type in filename: {file_name}")


def load_trials(file_path: Path) -> list[TrialData]:
    mat = sio.loadmat(str(file_path), squeeze_me=False, struct_as_record=False)
    keys = [k for k in mat.keys() if not k.startswith("__")]
    if len(keys) != 1:
        raise ValueError(f"{file_path}: expected 1 variable, found {keys}")

    payload = mat[keys[0]]
    if payload.dtype != object or payload.size != 1:
        raise ValueError(f"{file_path}: unexpected mat structure for {keys[0]}")

    struct = payload[0, 0]
    fields = struct._fieldnames
    values = {name: _flatten_field(getattr(struct, name)) for name in fields}

    lengths = {name: arr.shape[0] for name, arr in values.items()}
    if len(set(lengths.values())) != 1:
        raise ValueError(f"{file_path}: inconsistent field lengths {lengths}")

    n_trials = next(iter(lengths.values()))
    test_vals = values.get("test")
    if test_vals is None:
        raise ValueError(f"{file_path}: missing 'test' field")

    test_min = int(np.min(test_vals))
    baseline_value = 0 if test_min == 0 else 1

    valid_mask = np.isfinite(values["block"]) & np.isfinite(values["trial"]) & np.isfinite(values["target1_stim_index"])
    if not valid_mask.any():
        raise ValueError(f"{file_path}: no valid trials after filtering NaNs.")

    trials: list[TrialData] = []
    for idx in range(n_trials):
        if not valid_mask[idx]:
            continue
        test_val = int(values["test"][idx])
        probe_value = values["target2_stim_index"][idx]
        probe_index: int | None
        if np.isnan(probe_value):
            probe_index = None
        else:
            probe_raw = int(probe_value)
            if test_val == baseline_value or probe_raw < 0:
                probe_index = None
            else:
                probe_index = probe_raw

        similarity_response = None
        if "recog_resp" in values:
            recog_val = int(values["recog_resp"][idx])
            if recog_val > 0:
                similarity_response = recog_val

        trials.append(
            TrialData(
                block=int(values["block"][idx]),
                trial=int(values["trial"][idx]),
                memory_index=int(values["target1_stim_index"][idx]),
                probe_index=probe_index,
                test=test_val,
                direction=int(values["current_dir"][idx]),
                similarity_response=similarity_response,
            )
        )
    return trials


# ==============================================================================
# Rendering
# ==============================================================================
class StimuliRenderer(Renderer):
    def __init__(self, canvas_cfg: CanvasConfig, app_cfg: StimuliAppConfig):
        super().__init__(canvas_cfg)
        self.app_cfg = app_cfg
        self.colors = build_color_wheel(app_cfg)
        self.shape_templates = precompute_shape_templates(app_cfg.shape_space.count)

    def _color_from_index(self, index: int) -> tuple[float, float, float]:
        idx = (index - 1) % len(self.colors)
        return self.colors[idx]

    def _shape_from_index(self, canvas: Canvas, index: int, size_px: Pixel) -> patches.Polygon:
        template = self.shape_templates[(index - 1) % len(self.shape_templates)]
        size = size_px.value_in_unit(canvas)
        scaled = template * (size / 2.0)
        return patches.Polygon(scaled, closed=True)

    def _draw_memory_item(self, canvas: Canvas, stimulus_type: StimulusType, index: int) -> None:
        if stimulus_type == StimulusType.COLOR:
            diameter = self.app_cfg.color_space.item_diameter_px.value_in_unit(canvas)
            radius = diameter / 2
            canvas.add_patch(patches.Circle((0, 0), radius=radius, color=self._color_from_index(index)))
            return

        shape_patch = self._shape_from_index(canvas, index, self.app_cfg.shape_space.item_size_px)
        fill_color = self.app_cfg.shape_space.fill_color if self.app_cfg.shape_space.fill_enabled else "none"
        shape_patch.set_facecolor(fill_color)
        shape_patch.set_edgecolor(self.app_cfg.shape_space.stroke_color)
        shape_patch.set_linewidth(self.app_cfg.shape_space.stroke_width)
        shape_patch.set_transform(canvas.transData)
        canvas.add_patch(shape_patch)

    def _draw_probe_item(self, canvas: Canvas, stimulus_type: StimulusType, index: int) -> None:
        self._draw_memory_item(canvas, stimulus_type, index)

    def _draw_color_wheel(self, canvas: Canvas, rotation_deg: int) -> None:
        diameter = self.app_cfg.color_space.wheel_diameter_px.value_in_unit(canvas)
        radius = diameter / 2
        ring_width = self.app_cfg.color_space.wheel_ring_width_px.value_in_unit(canvas)

        for i, color in enumerate(self.colors):
            start = i + rotation_deg
            end = start + 1
            wedge = patches.Wedge((0, 0), radius, start, end, width=ring_width,
                                  facecolor=color, edgecolor=color, linewidth=0)
            canvas.add_patch(wedge)

    def _draw_shape_wheel(self, canvas: Canvas, rotation_deg: int) -> None:
        diameter = self.app_cfg.shape_space.wheel_diameter_px.value_in_unit(canvas)
        radius = diameter / 2
        step = 360 / self.app_cfg.shape_space.exemplar_count
        for idx in range(self.app_cfg.shape_space.exemplar_count):
            angle = np.deg2rad(rotation_deg + step * idx)
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            shape_index = int((rotation_deg + step * idx) % 360) + 1
            shape_patch = self._shape_from_index(canvas, shape_index, self.app_cfg.shape_space.wheel_item_size_px)
            fill_color = self.app_cfg.shape_space.fill_color if self.app_cfg.shape_space.fill_enabled else "none"
            shape_patch.set_facecolor(fill_color)
            shape_patch.set_edgecolor(self.app_cfg.shape_space.stroke_color)
            shape_patch.set_linewidth(self.app_cfg.shape_space.stroke_width)
            shape_patch.set_transform(transforms.Affine2D().translate(x, y) + canvas.transData)
            canvas.add_patch(shape_patch)

    def _draw_wheel(self, canvas: Canvas, stimulus_type: StimulusType, rotation_deg: int) -> None:
        if stimulus_type == StimulusType.COLOR:
            self._draw_color_wheel(canvas, rotation_deg)
        else:
            self._draw_shape_wheel(canvas, rotation_deg)

    def _draw_prompt(self, canvas: Canvas, text: str) -> None:
        canvas.add_text(
            (0, 0),
            text,
            fontsize=self.app_cfg.prompt.font_size,
            color=self.app_cfg.prompt.color,
            ha="center",
            va="center",
            transform=canvas.transData,
        )

    def draw(self, canvas: Canvas, scene_cfg: SceneConfig) -> None:
        trial = scene_cfg.trial

        if scene_cfg.phase == Phase.MEMORY:
            self._draw_memory_item(canvas, scene_cfg.stimulus_type, trial.memory_index)
            return

        if scene_cfg.phase == Phase.PROBE:
            if trial.probe_index is not None:
                self._draw_probe_item(canvas, scene_cfg.stimulus_type, trial.probe_index)
            return

        if scene_cfg.phase == Phase.WHEEL1:
            self._draw_wheel(canvas, scene_cfg.stimulus_type, scene_cfg.wheel_rotation)
            if scene_cfg.experiment in {ExperimentName.EXP2A, ExperimentName.EXP2B}:
                self._draw_prompt(canvas, "1")
            return

        if scene_cfg.phase == Phase.PROMPT:
            if trial.probe_index is None:
                return
            if scene_cfg.task_type == TaskType.COMPARE:
                self._draw_prompt(canvas, "2")
            elif scene_cfg.task_type == TaskType.REMEMBER and scene_cfg.experiment not in {ExperimentName.EXP2A, ExperimentName.EXP2B}:
                self._draw_prompt(canvas, "2")
            return

        if scene_cfg.phase == Phase.WHEEL2:
            if scene_cfg.task_type == TaskType.REMEMBER and trial.probe_index is not None:
                self._draw_wheel(canvas, scene_cfg.stimulus_type, scene_cfg.wheel_rotation)
                if scene_cfg.experiment in {ExperimentName.EXP2A, ExperimentName.EXP2B}:
                    self._draw_prompt(canvas, "2")
            return


# ==============================================================================
# Entry Point
# ==============================================================================

def load_config(path: Path) -> StimuliAppConfig:
    with path.open("rb") as f:
        data = tomllib.load(f)
    return StimuliAppConfig(**data)


def normalize_limit(limit: int | None) -> int | None:
    if limit is None:
        return None
    if limit == 0:
        return None
    return limit


def resolve_limits(app_cfg: StimuliAppConfig) -> tuple[int | None, int | None, dict[str, int] | None]:
    if app_cfg.render.limits is not None:
        return (
            normalize_limit(app_cfg.render.limits.max_files_per_exp),
            normalize_limit(app_cfg.render.limits.max_trials_per_file),
            app_cfg.render.limits.by_task,
        )
    return (
        normalize_limit(app_cfg.render.max_files_per_exp),
        normalize_limit(app_cfg.render.max_trials),
        None,
    )


def iter_data_files(app_cfg: StimuliAppConfig, exp_filter: set[str]) -> Iterable[Path]:
    file_limit, _, _ = resolve_limits(app_cfg)
    exp_dirs = [d for d in sorted(DATA_DIR.iterdir()) if d.is_dir() and d.name in exp_filter]
    
    for exp_dir in exp_dirs:
        count = 0
        mat_files = sorted(exp_dir.glob("*.mat"))
        for mat_file in mat_files:
            yield mat_file
            count += 1
            if file_limit is not None and count >= file_limit:
                break


def render_file(renderer: StimuliRenderer, app_cfg: StimuliAppConfig, file_path: Path) -> None:
    file_name = file_path.stem
    task_type = infer_task_type(file_name)
    stimulus_type = infer_stimulus_type(file_name)
    experiment = ExperimentName(file_path.parent.name)
    trials = load_trials(file_path)

    out_dir = OUTPUT_DIR / experiment.value / task_type.value / file_name
    out_dir.mkdir(parents=True, exist_ok=True)

    _, max_trials_per_file, by_task = resolve_limits(app_cfg)
    phases = app_cfg.render.phases
    
    task_limit = None
    if by_task is not None:
        task_limit = normalize_limit(by_task.get(task_type.value))
    trial_limit = task_limit if task_limit is not None else max_trials_per_file

    trials_to_process = trials if trial_limit is None else trials[:trial_limit]
    logger.info(
        f"{experiment.value}/{task_type.value}/{stimulus_type.value}: trials selected {len(trials_to_process)}/{len(trials)} (limit={trial_limit})"
    )
    if trials:
        all_keys = {(t.test, t.probe_index is not None) for t in trials}
        filtered_keys = {(t.test, t.probe_index is not None) for t in trials_to_process}
        logger.info(
            f"{experiment.value}/{task_type.value}/{stimulus_type.value} coverage: {len(filtered_keys)}/{len(all_keys)} condition combos"
        )

    for idx, trial in enumerate(trials_to_process):
        wheel_rotation = random.randint(0, 359)
        for phase_idx, phase in enumerate(phases):
            scene_cfg = SceneConfig(
                phase=phase,
                stimulus_type=stimulus_type,
                task_type=task_type,
                trial=trial,
                wheel_rotation=wheel_rotation,
                experiment=experiment,
            )
            if not should_render_phase(scene_cfg):
                logger.debug(f"Skipping phase {phase} for trial {idx + 1} (probe_index={trial.probe_index})")
                continue
            output_path = out_dir / f"Trial_{idx + 1}_{phase_idx + 1}_{phase.value}.{app_cfg.render.output_format}"
            logger.info(f"Rendering {output_path}")
            renderer.render(scene_cfg, OutputConfig(file_path=str(output_path)))
            logger.info(f"Completed rendering {output_path}")


def render_file_worker(args: tuple[Path, dict]) -> None:
    """Worker function for multiprocessing"""
    file_path, config_dict = args
    # Reconstruct config from dict
    app_cfg = StimuliAppConfig(**config_dict)
    
    # Initialize renderer in this process
    renderer = StimuliRenderer(app_cfg.canvas, app_cfg)
    
    # Set random seed for this process
    process_id = os.getpid()
    random.seed(app_cfg.render.seed + process_id)
    np.random.seed(app_cfg.render.seed + process_id)
    
    # Render the file
    try:
        logger.info(f"Process {process_id} rendering {file_path}")
        render_file(renderer, app_cfg, file_path)
        logger.info(f"Process {process_id} completed {file_path}")
    except Exception as e:
        logger.error(f"Process {process_id} failed to render {file_path}: {e}")
        raise


def should_render_phase(scene_cfg: SceneConfig) -> bool:
    trial = scene_cfg.trial
    if scene_cfg.phase == Phase.PROBE:
        return trial.probe_index is not None
    if scene_cfg.phase == Phase.PROMPT:
        if trial.probe_index is None:
            return False
        if scene_cfg.task_type == TaskType.COMPARE:
            return True
        if scene_cfg.task_type == TaskType.REMEMBER and scene_cfg.experiment not in {ExperimentName.EXP2A, ExperimentName.EXP2B}:
            return True
        return False
    if scene_cfg.phase == Phase.WHEEL2:
        return scene_cfg.task_type == TaskType.REMEMBER and trial.probe_index is not None
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reproduce stimuli for perceptual comparison and memory bias experiments.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test with default settings (all experiments, limited trials):
  uv run python script/reproduce_stimuli.py

  # Quick test for a specific experiment:
  uv run python script/reproduce_stimuli.py --exp Exp1A

  # Full generation (all data):
  uv run python script/reproduce_stimuli.py --full
        """
    )
    parser.add_argument(
        "--exp",
        type=str,
        choices=[e.value for e in ExperimentName] + ["all"],
        default="all",
        help="Which experiment to run (default: all)"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Ignore all limits and process all trials/files"
    )
    args = parser.parse_args()

    config = load_config(CONFIG_PATH)
    if args.full:
        if config.render.limits is not None:
            config.render.limits.max_trials_per_file = 0
            config.render.limits.max_files_per_exp = 0
            if config.render.limits.by_task is not None:
                for key in list(config.render.limits.by_task.keys()):
                    config.render.limits.by_task[key] = 0
        else:
            config.render.max_trials = 0
            config.render.max_files_per_exp = 0
        logger.info("Running in FULL mode: processing all trials/files")
    else:
        file_limit, trial_limit, by_task = resolve_limits(config)
        logger.info(
            f"Running with limits: max_files_per_exp={file_limit}, max_trials_per_file={trial_limit}, by_task={by_task}"
        )
    
    selected_exps = {e.value for e in ExperimentName} if args.exp == "all" else {args.exp}
    
    # Get all files first for progress bar
    all_files = list(iter_data_files(config, selected_exps))
    
    # Check if multiprocessing is enabled and we have files to process
    if config.multiprocessing.enabled and len(all_files) > 1:
        # Determine number of processes to use
        if config.multiprocessing.processes is not None and config.multiprocessing.processes > 0:
            num_processes = min(config.multiprocessing.processes, len(all_files))
        else:
            # Use all available CPU cores, but don't exceed number of files
            num_processes = min(mp.cpu_count(), len(all_files))
        
        logger.info(f"Using multiprocessing with {num_processes} processes")
        
        # Prepare arguments for worker processes
        # Convert config to dict for pickling
        config_dict = config.model_dump()
        args_list = [(file_path, config_dict) for file_path in all_files]
        
        # Create process pool
        with mp.Pool(processes=num_processes) as pool:
            # Use tqdm to show progress
            list(tqdm(pool.imap(render_file_worker, args_list),
                     total=len(all_files),
                     desc="Processing files"))
    else:
        # Single process execution
        logger.info("Using single process execution")
        random.seed(config.render.seed)
        np.random.seed(config.render.seed)
        
        renderer = StimuliRenderer(config.canvas, config)
        
        for mat_file in tqdm(all_files, desc="Processing files"):
            logger.info(f"Rendering {mat_file}")
            render_file(renderer, config, mat_file)
