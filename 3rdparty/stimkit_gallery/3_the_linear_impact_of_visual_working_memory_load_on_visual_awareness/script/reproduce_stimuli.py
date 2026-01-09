import sys
import tomllib
import argparse
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
from pathlib import Path
from collections import Counter
from loguru import logger
from tqdm import tqdm

logger.remove()
logger.add(sys.stderr, level="INFO")

from stimkit import Canvas, CanvasConfig, Renderer
from stimkit.layouts import diamond_positions
from config import (
    StimuliAppConfig, TrialData, SceneConfig,
    ConditionExp1, ConditionExp2, ConditionExp3, Phase
)

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR.parent / "output"
DATA_DIR = SCRIPT_DIR.parent / "data"
CONFIG_PATH = SCRIPT_DIR / "stimuli_config.toml"

# ==============================================================================
# Helpers
# ==============================================================================

def load_txt_data(file_path: Path) -> list[TrialData]:
    """Reads space-separated txt data file."""
    data = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Skip header lines until we find "Trial"
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("Trial"):
            start_idx = i + 1
            break
            
    for line in lines[start_idx:]:
        parts = line.strip().split()
        if len(parts) < 7: continue
        try:
            # Columns: Trial Condition RT1 RT2 RT3 Acc KeyResponse
            # Note: KeyResponse might be missing or weird, but we only need first 7
            record = TrialData(
                Trial=int(parts[0]),
                Condition=int(parts[1]),
                RT1=float(parts[2]),
                RT2=float(parts[3]),
                RT3=float(parts[4]),
                Acc=int(parts[5]),
                KeyResponse=int(parts[6])
            )
            data.append(record)
        except ValueError:
            continue
    return data

def parse_condition_exp1(cond_val: int) -> tuple[int, bool]:
    """Returns (Load, Match)."""
    match cond_val:
        case 1: return (1, True)
        case 2: return (1, False)
        case 3: return (2, True)
        case 4: return (2, False)
        case 5: return (3, True)
        case 6: return (3, False)
        case 7 | 8: return (0, False)
        case _: raise ValueError(f"Unknown condition Exp1: {cond_val}")

def parse_condition_exp2(cond_val: int) -> tuple[int, bool]:
    match cond_val:
        case 1: return (1, True)
        case 2: return (1, False)
        case 3: return (3, True)
        case 4: return (3, False)
        case _: raise ValueError(f"Unknown condition Exp2: {cond_val}")

def parse_condition_exp3(cond_val: int) -> int:
    """Returns Load only."""
    if 1 <= cond_val <= 3:
        return cond_val
    raise ValueError(f"Unknown condition Exp3: {cond_val}")

# ==============================================================================
# Helpers
# ==============================================================================

def generate_random_shape_patch(cx, cy, size, color, seed, transform):
    """Generates a random complex polygon using pre-calculated units."""
    rng = np.random.RandomState(seed)
    num_points = rng.randint(5, 9)
    angles = np.sort(rng.rand(num_points) * 2 * np.pi)
    
    radii = size/2 * (0.5 + 0.5 * rng.rand(num_points))
    
    x = cx + radii * np.cos(angles)
    y = cy + radii * np.sin(angles)
    pts = np.column_stack((x, y))
    
    return patches.Polygon(pts, closed=True, color=color, transform=transform)

def get_memory_positions(eccentricity_unit: float) -> list[tuple[float, float]]:
    positions = diamond_positions(eccentricity_unit)
    return [positions[0], positions[2], positions[3], positions[1]]

# ==============================================================================
# Rendering Logic
# ==============================================================================

def draw_fixation_cross(canvas: Canvas, color: str, size_unit: float, stroke_unit: float):
    """Draws a central fixation cross for Memory/Probe phases."""
    rect1 = patches.Rectangle((-size_unit/2, -stroke_unit/2), size_unit, stroke_unit, color=color, transform=canvas.transData)
    rect2 = patches.Rectangle((-stroke_unit/2, -size_unit/2), stroke_unit, size_unit, color=color, transform=canvas.transData)
    canvas.ax.add_patch(rect1)
    canvas.ax.add_patch(rect2)

def render_memory_phase(canvas: Canvas, cfg: StimuliAppConfig, scene: SceneConfig):
    """Renders the memory prime display."""
    if scene.load > 0:
        rng = random.Random(scene.trial_data.trial_idx + cfg.render.seed)
        selected_pos = rng.sample(scene.diamond_positions_unit, scene.load)
        
        for i, pos in enumerate(selected_pos):
            shape_seed = scene.shapes[i]
            patch = generate_random_shape_patch(
                pos[0], pos[1], scene.item_size_unit, cfg.memory.shape_color, 
                shape_seed, canvas.transData
            )
            canvas.ax.add_patch(patch)
            
    # Fixation: "central fixation cross"
    draw_fixation_cross(canvas, cfg.display.fixation_color, scene.fixation_size_unit, scene.fixation_stroke_unit)

def render_mib_phase(canvas: Canvas, cfg: StimuliAppConfig, scene: SceneConfig):
    """Renders the MIB display."""
    mask_size = scene.mask_size_unit
    cs = scene.cross_size_unit
    w = scene.cross_width_unit
    
    # Correct step calculation: mask_size covers (N-1) intervals between N items
    step = mask_size / (max(cfg.mib.grid_rows, cfg.mib.grid_cols) - 1)
    start_x = - (cfg.mib.grid_cols - 1) * step / 2
    start_y = - (cfg.mib.grid_rows - 1) * step / 2
    
    cross_color = np.array(cfg.mib.cross_color) / 255.0
    
    # Paper: "continuously rotated clockwise at 240 deg/s"
    # To show it's dynamic, randomize grid angle per trial snapshot using trial_idx as seed.
    rng = random.Random(scene.trial_data.trial_idx + cfg.render.seed)
    grid_angle = rng.uniform(0, 360)
    grid_transform = transforms.Affine2D().rotate_deg(grid_angle) + canvas.transData

    for r in range(cfg.mib.grid_rows):
        for c in range(cfg.mib.grid_cols):
            x = start_x + c * step
            y = start_y + r * step
            
            # Cross part 1
            rect1 = patches.Rectangle((x - cs/2, y - w/2), cs, w, color=cross_color, transform=grid_transform)
            # Cross part 2
            rect2 = patches.Rectangle((x - w/2, y - cs/2), w, cs, color=cross_color, transform=grid_transform)
            canvas.ax.add_patch(rect1)
            canvas.ax.add_patch(rect2)

    # 2. Target: Stationary at Upper-Left
    tx, ty = scene.target_pos_unit
    target_r = scene.target_size_unit / 2
    target = patches.Circle((tx, ty), target_r, color=cfg.mib.target_color, transform=canvas.transData)
    canvas.ax.add_patch(target)

    # 3. Fixation: "central white fixation point (circle with stroke)"
    fix_r = scene.fixation_size_unit / 2
    # stroke of 1 pixel = small linewidth, empty center
    fix = patches.Circle((0, 0), fix_r, color=cfg.display.fixation_color,
                         fill=False, linewidth=scene.fixation_stroke_points, transform=canvas.transData)
    canvas.ax.add_patch(fix)

def render_probe_phase(canvas: Canvas, cfg: StimuliAppConfig, scene: SceneConfig):
    """Renders the probe display."""
    if scene.load > 0:
        rng = random.Random(scene.trial_data.trial_idx + cfg.render.seed)
        selected_pos = rng.sample(scene.diamond_positions_unit, scene.load)
        
        shapes_indices = list(scene.shapes)
        if not scene.match:
            change_idx = rng.randint(0, scene.load - 1)
            shapes_indices[change_idx] = scene.probe_shape
            
        for i, pos in enumerate(selected_pos):
            shape_seed = shapes_indices[i]
            patch = generate_random_shape_patch(
                pos[0], pos[1], scene.item_size_unit, cfg.memory.shape_color, 
                shape_seed, canvas.transData
            )
            canvas.ax.add_patch(patch)

    # Fixation: "central fixation cross"
    draw_fixation_cross(canvas, cfg.display.fixation_color, scene.fixation_size_unit, scene.fixation_stroke_unit)

class StimuliRenderer(Renderer):
    def __init__(self, canvas_config: CanvasConfig, app_config: StimuliAppConfig):
        super().__init__(canvas_config)
        self.app_cfg = app_config

    def draw(self, canvas: Canvas, scene: SceneConfig):
        if scene.phase == Phase.MEMORY:
            render_memory_phase(canvas, self.app_cfg, scene)
        elif scene.phase == Phase.MIB:
            render_mib_phase(canvas, self.app_cfg, scene)
        elif scene.phase == Phase.PROBE:
            render_probe_phase(canvas, self.app_cfg, scene)

# ==============================================================================
# Main Loop
# ==============================================================================

def load_config() -> StimuliAppConfig:
    with open(CONFIG_PATH, "rb") as f:
        toml_data = tomllib.load(f)
    return StimuliAppConfig(**toml_data)


def normalize_limit(limit: int) -> int | None:
    if limit == 0:
        return None
    return limit


def log_coverage(exp_name: str, all_trials: list[TrialData], filtered_trials: list[TrialData]) -> None:
    if not all_trials:
        return
    if exp_name == "Exp1":
        expected = len(ConditionExp1)
        counter = Counter(t.condition for t in filtered_trials)
    elif exp_name == "Exp2":
        expected = len(ConditionExp2)
        counter = Counter(t.condition for t in filtered_trials)
    else:
        expected = len(ConditionExp3)
        counter = Counter(t.condition for t in filtered_trials)
    logger.info(f"{exp_name} coverage: {len(counter)}/{expected} condition values")


def main():
    parser = argparse.ArgumentParser(
        description="Reproduce stimuli for visual working memory load experiments.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test with default settings (all experiments, limited trials):
  uv run python script/reproduce_stimuli.py

  # Quick test for a specific experiment:
  uv run python script/reproduce_stimuli.py --exp E1

  # Full generation (all data):
  uv run python script/reproduce_stimuli.py --full
        """
    )
    parser.add_argument(
        "--exp",
        type=str,
        choices=["E1", "E2", "E3", "all"],
        default="all",
        help="Which experiment to run: E1, E2, E3, or all (default: all)"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Ignore all limits and process all trials/files"
    )
    args = parser.parse_args()

    cfg = load_config()
    if args.full:
        cfg.render.max_trials = 0
        cfg.render.max_files_per_exp = 0
        logger.info("Running in FULL mode: processing all trials/files")
    else:
        logger.info(
            f"Running with limits: max_trials={cfg.render.max_trials}, max_files_per_exp={cfg.render.max_files_per_exp}"
        )
    
    # Process each experiment
    experiments = [
        ("E1", "Exp1", cfg.data.exp1_path),
        ("E2", "Exp2", cfg.data.exp2_path),
        ("E3", "Exp3", cfg.data.exp3_path)
    ]
    
    for exp_key, exp_name, rel_path in experiments:
        if args.exp not in ("all", exp_key):
            continue
        logger.info(f"Processing {exp_name}...")
        
        # Find all txt files
        data_path = SCRIPT_DIR.parent / rel_path
        files = sorted(list(data_path.glob("*.txt")))
        
        if not files:
            logger.warning(f"No data files found for {exp_name} in {data_path}")
            continue
            
        file_limit = normalize_limit(cfg.render.max_files_per_exp)
        files_to_process = files if file_limit is None else files[:file_limit]
        logger.info(f"{exp_name}: {len(files_to_process)}/{len(files)} files selected.")

        for file_path in files_to_process:
            logger.info(f"Reading {file_path.name}")
            data = load_txt_data(file_path)
            
            # Select subset
            trial_limit = normalize_limit(cfg.render.max_trials)
            trials = data if trial_limit is None else data[:trial_limit]
            log_coverage(exp_name, data, trials)
            
            for trial in tqdm(trials, desc=f"{exp_name} Trials"):
                # Determine Scene Config
                load = 0
                match = None
                
                try:
                    if exp_name == "Exp1":
                        load, match = parse_condition_exp1(trial.condition)
                    elif exp_name == "Exp2":
                        load, match = parse_condition_exp2(trial.condition)
                    elif exp_name == "Exp3":
                        load = parse_condition_exp3(trial.condition)
                        match = None # Counting task
                except ValueError as e:
                    logger.warning(e)
                    continue

                # Prepare Random Shapes
                # We need 'load' number of shapes.
                # Use a large pool of seeds/IDs for shapes.
                rng = random.Random(trial.trial_idx + cfg.render.seed)
                shape_pool = list(range(100, 200)) # Arbitrary IDs
                current_shapes = rng.sample(shape_pool, max(1, load))
                
                probe_shape = None
                if match is False:
                    # Pick a new shape not in current
                    remaining = [s for s in shape_pool if s not in current_shapes]
                    probe_shape = rng.choice(remaining)
                
                # Prepare Canvas and pre-calculate units
                canvas_cfg = cfg.canvas
                # We use a dummy canvas context only to trigger unit calculation
                # (Physical units depend on Screen resolution and Viewing Distance)
                with Canvas(canvas_cfg) as canvas:
                    # Pre-calculate common units
                    fix_size_u = cfg.display.fixation_size.value_in_unit(canvas)
                    fix_stroke_u = cfg.display.fixation_cross_width.value_in_unit(canvas)
                    fix_stroke_pt = cfg.display.fixation_stroke.value_in_points(canvas)
                    item_size_u = cfg.memory.item_size.value_in_unit(canvas)
                    
                    # Positions
                    diamond_ecc_u = cfg.memory.diamond_eccentricity.value_in_unit(canvas)
                    diamond_u = get_memory_positions(diamond_ecc_u)
                    
                    # MIB Units
                    mask_u = cfg.mib.mask_size.value_in_unit(canvas)
                    c_size_u = cfg.mib.cross_size.value_in_unit(canvas)
                    c_width_u = cfg.mib.cross_width.value_in_unit(canvas)
                    t_size_u = cfg.mib.target_size.value_in_unit(canvas)
                    t_ecc_u = cfg.mib.target_eccentricity.value_in_unit(canvas)
                    
                    # Target position in units
                    tx = -t_ecc_u * np.cos(np.deg2rad(45))
                    ty = t_ecc_u * np.sin(np.deg2rad(45))

                # Render Phases
                for phase in cfg.render.phases:
                    if phase == Phase.PROBE and exp_name == "Exp3":
                        continue # No probe in Exp3
                        
                    scene = SceneConfig(
                        experiment=exp_name,
                        phase=phase,
                        trial_data=trial,
                        load=load,
                        match=match,
                        shapes=current_shapes,
                        probe_shape=probe_shape,
                        # Pass units
                        fixation_size_unit=fix_size_u,
                        fixation_stroke_unit=fix_stroke_u,
                        fixation_stroke_points=fix_stroke_pt,
                        item_size_unit=item_size_u,
                        diamond_positions_unit=diamond_u,
                        mask_size_unit=mask_u,
                        cross_size_unit=c_size_u,
                        cross_width_unit=c_width_u,
                        target_size_unit=t_size_u,
                        target_eccentricity_unit=t_ecc_u,
                        target_pos_unit=(tx, ty)
                    )

                    renderer = StimuliRenderer(cfg.canvas, cfg)
                    
                    # Output Config
                    out_path = OUTPUT_DIR / exp_name / f"Trial_{trial.trial_idx}" / f"{phase.value}.{cfg.render.output_format}"
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    from stimkit import OutputConfig
                    renderer.render(scene, OutputConfig(file_path=str(out_path)))

if __name__ == "__main__":
    main()
