import sys
import tomllib
import argparse
import numpy as np
import random
from pathlib import Path
from typing import Literal

from loguru import logger
from tqdm import tqdm
import matplotlib.patches as patches
import matplotlib.transforms as transforms

# Internal stimkit imports
from stimkit import Canvas, CanvasConfig, OutputConfig, Renderer, VisualAngle, load_excel
from stimkit.collections import circle, square, triangle, hexagon, star
from stimkit.collections.lines import centered_line, cross_line
from stimkit.layouts import radial_positions

# Local imports
from config import (
    Phase, ShapeType, MatchCondition, TrialData, SceneConfig, StimuliAppConfig
)

# Set log level to INFO to avoid excessive debug output
logger.remove()
logger.add(sys.stderr, level="INFO")

SCRIPT_DIR = Path(__file__).parent
DATA_ROOT = SCRIPT_DIR.parent / "data"
OUTPUT_ROOT = SCRIPT_DIR.parent / "output"
CONFIG_PATH = SCRIPT_DIR / "stimuli_config.toml"

# ==============================================================================
# Patch Factory Functions
# ==============================================================================
def shape_patch(shape_idx: int, xy: tuple[float, float], size: float, color: str, 
                transform: transforms.Transform) -> patches.Patch:
    """Create a patch for various shapes based on Paper descriptions (outlines)."""
    r = size / 2
    # Width of the outline
    lw = 3.0
    
    match shape_idx:
        case ShapeType.CIRCLE:
            return circle(xy, r, color, transform, fill=False, linewidth=lw)
        case ShapeType.SQUARE:
            return square(xy, size, color, transform, fill=False, linewidth=lw)
        case ShapeType.STAR:
            return star(xy, r, color, transform, fill=False, linewidth=lw)
        case ShapeType.TRIANGLE:
            return triangle(xy, r, color, transform, fill=False, linewidth=lw)
        case ShapeType.HEXAGON:
            return hexagon(xy, r, color, transform, fill=False, linewidth=lw)
        case _:
            return circle(xy, r, color, transform, fill=False, linewidth=lw)

# ==============================================================================
# Renderer
# ==============================================================================
class UnifiedRenderer(Renderer):
    def __init__(self, canvas_cfg: CanvasConfig, app_cfg: StimuliAppConfig) -> None:
        super().__init__(canvas_cfg)
        self.app_cfg = app_cfg

    def get_color(self, idx: int) -> str:
        # idx is 1-indexed in data
        return self.app_cfg.display.colors[(int(idx) - 1) % self.app_cfg.display.color_count]

    def draw(self, canvas: Canvas, cfg: SceneConfig) -> None:
        match cfg.phase:
            case Phase.FIXATION:
                self._draw_fixation(canvas, cfg)
            case Phase.LOAD:
                self._draw_load(canvas, cfg)
            case Phase.MEMORY:
                self._draw_memory(canvas, cfg)
            case Phase.SEARCH:
                self._draw_search(canvas, cfg)
            case Phase.TEST:
                self._draw_test(canvas, cfg)

    def _draw_fixation(self, canvas: Canvas, cfg: SceneConfig) -> None:
        """Draw central fixation cross."""
        size = self.app_cfg.display.fixation_size.value_in_unit(canvas)
        
        canvas.add_patches(cross_line((0, 0), size, "black", 0, canvas.transData, linewidth=2))

    def _draw_load(self, canvas: Canvas, cfg: SceneConfig) -> None:
        """Draw the two-digit number for Exp 6 (backward counting/rehearsal)."""
        if not cfg.exp_name.startswith("Exp6"):
            return
            
        t = cfg.trial_data
        rng = random.Random(t.Trial + t.Id * 1000 + self.app_cfg.render.seed)
        num = rng.randint(10, 99)
        
        font_size_pts = self.app_cfg.display.load_text_height.value_in_points(canvas)
        
        canvas.add_text(
            (0, 0), str(num), 
            fontsize=font_size_pts, 
            color="black", 
            ha="center", 
            va="center",
            transform=canvas.transData
        )

    def _get_item_features(self, cfg: SceneConfig):
        """Reconstruct memory features deterministically."""
        t = cfg.trial_data
        # Use a seed unique to the trial and the app seed
        rng = random.Random(t.Trial + t.Id * 1000 + self.app_cfg.render.seed)
        
        # Default features
        color_idx = rng.randint(1, self.app_cfg.display.color_count)
        shape_idx = ShapeType.CIRCLE
        size_val = self.app_cfg.experiments.exp1.memory_item_size # Default

        if cfg.exp_name.startswith("Exp1"):
            # Exp 1: color memory, targetshape given (1-5)
            shape_idx = t.targetshape
            # color is random as it's not in the data for Exp 1
            pass
        elif cfg.exp_name.startswith("Exp4") or cfg.exp_name.startswith("Exp6"):
            # Exp 4/6: size memory, targetcolor and targetshape and targetsize given
            color_idx = t.targetcolor
            shape_idx = t.targetshape
            if t.targetsize == 1: # Large
                size_val = self.app_cfg.experiments.exp4.memory_item_size_large
            else: # Small
                size_val = self.app_cfg.experiments.exp4.memory_item_size_small
        elif cfg.exp_name.startswith("Exp5"):
            # Exp 5: color memory, targetcolor and targetshape given
            color_idx = t.targetcolor
            shape_idx = t.targetshape
            size_val = self.app_cfg.experiments.exp5.memory_item_size
        
        return color_idx, shape_idx, size_val

    def _draw_memory(self, canvas: Canvas, cfg: SceneConfig) -> None:
        c_idx, s_idx, size_va = self._get_item_features(cfg)
        size = size_va.value_in_unit(canvas)
        canvas.add_patch(shape_patch(s_idx, (0, 0), size, self.get_color(c_idx), canvas.transData))

    def _draw_search(self, canvas: Canvas, cfg: SceneConfig) -> None:
        if cfg.exp_name.startswith("Exp5"):
            return # Exp 5 has no search phase

        t = cfg.trial_data
        rng = random.Random(t.Trial + t.Id * 1000 + self.app_cfg.render.seed)
        
        mem_color_idx, mem_shape_idx, _ = self._get_item_features(cfg)
        
        # Config 1 or 2
        config_idx = rng.randint(1, 2)
        angles = [30, 120, 210, 300] if config_idx == 1 else [60, 150, 240, 330]
        
        target_pos_idx = rng.randint(0, 3)
        match_pos_idx = (target_pos_idx + rng.randint(1, 3)) % 4
        
        radius = self.app_cfg.search.radius.value_in_unit(canvas)
        item_size = self.app_cfg.search.item_size.value_in_unit(canvas)
        line_len = self.app_cfg.search.line_length.value_in_unit(canvas)
        line_wid = self.app_cfg.search.line_width.value_in_points(canvas, min_points=0.5)
        
        positions = radial_positions(angles, radius)
        for i, (x, y) in enumerate(positions):
            
            if i == match_pos_idx:
                match t.matchcondition:
                    case MatchCondition.COLOR:
                        c_idx, s_idx = mem_color_idx, (mem_shape_idx % self.app_cfg.display.shape_count) + 1
                    case MatchCondition.SHAPE:
                        c_idx, s_idx = (mem_color_idx % self.app_cfg.display.color_count) + 1, mem_shape_idx
                    case MatchCondition.CONJUNCTION:
                        c_idx, s_idx = mem_color_idx, mem_shape_idx
                    case MatchCondition.NEUTRAL:
                        c_idx = (mem_color_idx % self.app_cfg.display.color_count) + 1
                        s_idx = (mem_shape_idx % self.app_cfg.display.shape_count) + 1
                    case _:
                        c_idx = (mem_color_idx % self.app_cfg.display.color_count) + 1
                        s_idx = (mem_shape_idx % self.app_cfg.display.shape_count) + 1
            else:
                # Other distractors (not the matched one)
                c_idx = (mem_color_idx + i + 1) % self.app_cfg.display.color_count + 1
                s_idx = (mem_shape_idx + i) % self.app_cfg.display.shape_count + 1
            
            canvas.add_patch(shape_patch(s_idx, (x, y), item_size, self.get_color(c_idx), canvas.transData))
            
            # Lines
            if i == target_pos_idx:
                tilt_val = t.linecondition if t.linecondition is not None else 1
                tilt = self.app_cfg.search.target_tilt if tilt_val == 2 else -self.app_cfg.search.target_tilt
                angle = 90 + tilt
                l = centered_line((x, y), line_len, self.app_cfg.search.distractor_line_color, angle, canvas.transData, linewidth=line_wid)
            else:
                l = centered_line((x, y), line_len, self.app_cfg.search.distractor_line_color, 90, canvas.transData, linewidth=line_wid)
            canvas.add_patch(l)

    def _draw_test(self, canvas: Canvas, cfg: SceneConfig) -> None:
        t = cfg.trial_data
        mem_color_idx, mem_shape_idx, mem_size_va = self._get_item_features(cfg)
        
        final_color_idx = mem_color_idx
        final_shape_idx = mem_shape_idx
        final_size_va = mem_size_va

        if cfg.exp_name.startswith("Exp1"):
            if t.test == 0: # Different
                final_color_idx = (mem_color_idx % self.app_cfg.display.color_count) + 1
        elif cfg.exp_name.startswith("Exp4") or cfg.exp_name.startswith("Exp6"):
            if t.test == 0: # Different size
                if mem_size_va == self.app_cfg.experiments.exp4.memory_item_size_large:
                    final_size_va = self.app_cfg.experiments.exp4.memory_item_size_small
                else:
                    final_size_va = self.app_cfg.experiments.exp4.memory_item_size_large
        elif cfg.exp_name.startswith("Exp5"):
            # Exp 5: target_change (color) and irre_change (shape)
            if t.target_change == 1:
                final_color_idx = (mem_color_idx % self.app_cfg.display.color_count) + 1
            if t.irre_change == 1:
                final_shape_idx = (mem_shape_idx % self.app_cfg.display.shape_count) + 1
        
        size = final_size_va.value_in_unit(canvas)
        canvas.add_patch(shape_patch(final_shape_idx, (0, 0), size, self.get_color(final_color_idx), canvas.transData))

def load_data_excel(exp_name: str, file_path: Path, sheet: str) -> list[TrialData]:
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return []
    
    df = load_excel(file_path, sheet=sheet)
    
    # RENAME 'testtshape' to 'testshape' if present (Fix for Exp 5)
    if "testtshape" in df.columns:
        df = df.rename(columns={"testtshape": "testshape"})

    trials = []
    # Get the allowed fields from the model
    allowed_fields = set(TrialData.model_fields.keys())
    
    # Convert to dictionary for easier mapping to TrialData
    for row in df.to_dict(orient="records"):
        # Clean data (handle nulls and types and filter extra fields)
        clean_row = {}
        for k, v in row.items():
            if k in allowed_fields and v is not None and not (isinstance(v, float) and np.isnan(v)):
                try:
                    # Excel often reads ints as floats
                    clean_row[k] = int(v) if not isinstance(v, str) else v
                except (ValueError, TypeError):
                    clean_row[k] = v
        
        try:
            trials.append(TrialData(**clean_row))
        except Exception as e:
            # We only log this once to avoid spamming the console
            if len(trials) == 0:
                logger.error(f"Failed to parse trial in {exp_name}: {e}")
            continue
    return trials

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reproduce stimuli for 'More attention with less working memory'.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test with default settings (all experiments, limited trials):
  uv run python script/reproduce_stimuli.py

  # Quick test for a specific experiment:
  uv run python script/reproduce_stimuli.py --exp Exp1a

  # Full generation (all data):
  uv run python script/reproduce_stimuli.py --full
        """
    )
    parser.add_argument(
        "--exp",
        type=str,
        choices=["Exp1a", "Exp1b", "Exp4a", "Exp4b", "Exp5a", "Exp5b", "Exp6a", "Exp6b", "all"],
        default="all",
        help="Which experiment to run (default: all)"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Ignore all limits and process all trials"
    )
    args = parser.parse_args()

    with open(CONFIG_PATH, "rb") as f:
        config_dict = tomllib.load(f)
    app_cfg = StimuliAppConfig(**config_dict)

    if args.full:
        app_cfg.render.max_trials = 0
        logger.info("Running in FULL mode: processing all trials")
    else:
        logger.info(f"Running with limit: max_trials={app_cfg.render.max_trials}")

    def normalize_limit(limit: int) -> int | None:
        return None if limit == 0 else limit

    def coverage_key(exp_label: str, trial: TrialData) -> tuple | None:
        if exp_label.startswith("Exp1"):
            return (trial.matchcondition, trial.linecondition, trial.test)
        if exp_label.startswith("Exp4"):
            return (trial.targetsize, trial.matchcondition, trial.SOA, trial.test)
        if exp_label.startswith("Exp5"):
            return (trial.target_change, trial.irre_change)
        if exp_label.startswith("Exp6"):
            return (trial.targetsize, trial.matchcondition, trial.linecondition, trial.test)
        return None

    renderer = UnifiedRenderer(app_cfg.canvas, app_cfg)

    tasks = [
        ("Exp1a", DATA_ROOT / "Exp.1a&1b/Exp.1a&1b/Exp.1a_original.xlsx", "original data"),
        ("Exp1b", DATA_ROOT / "Exp.1a&1b/Exp.1a&1b/Exp.1b_original.xlsx", "original data"),
        ("Exp4a", DATA_ROOT / "Exp.4a&4b/Exp.4a&4b/Exp.4a_original.xlsx", "original_4a"),
        ("Exp4b", DATA_ROOT / "Exp.4a&4b/Exp.4a&4b/Exp.4b_original.xlsx", "original_4b"),
        ("Exp5a", DATA_ROOT / "Exp.4a&4b/Exp.5a&5b/Exp.5a_original.xlsx", "CD_irre"),
        ("Exp5b", DATA_ROOT / "Exp.4a&4b/Exp.5a&5b/Exp.5b_original.xlsx", "CD_key"),
        ("Exp6a", DATA_ROOT / "Exp.6a&6b/Exp.6a_original.xlsx", "original_3a"),
        ("Exp6b", DATA_ROOT / "Exp.6a&6b/Exp.6b_original.xlsx", "original_3b"),
    ]

    for exp_label, file_path, sheet in tasks:
        if args.exp not in ("all", exp_label):
            continue
        logger.info(f"Loading data for {exp_label} from {file_path.name} [{sheet}]...")
        trials = load_data_excel(exp_label, file_path, sheet)
        if not trials:
            continue

        limit = normalize_limit(app_cfg.render.max_trials)
        render_trials = trials if limit is None else trials[:limit]
        logger.info(f"Rendering {exp_label}: {len(render_trials)} trials selected.")

        all_keys = {coverage_key(exp_label, t) for t in trials if coverage_key(exp_label, t) is not None}
        filtered_keys = {coverage_key(exp_label, t) for t in render_trials if coverage_key(exp_label, t) is not None}
        if all_keys:
            logger.info(f"{exp_label} coverage: {len(filtered_keys)}/{len(all_keys)} condition combos")

        for trial in tqdm(render_trials, desc=f"Experiment {exp_label}", leave=False):
            trial_dir = OUTPUT_ROOT / exp_label / f"Trial_{trial.Trial}"
            trial_dir.mkdir(parents=True, exist_ok=True)

            for phase in app_cfg.render.phases:
                # Exp 1-5 have no load phase
                if phase == Phase.LOAD and not exp_label.startswith("Exp6"):
                    continue
                # Exp 5 has no search phase
                if phase == Phase.SEARCH and exp_label.startswith("Exp5"):
                    continue

                scene = SceneConfig(phase=phase, trial_data=trial, exp_name=exp_label)
                out_path = trial_dir / f"{phase.value}.{app_cfg.render.output_format}"
                renderer.render(scene, OutputConfig(file_path=str(out_path)))

    logger.success("Stimuli generation completed successfully.")
