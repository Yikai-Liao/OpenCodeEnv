"""
Reproduce stimuli from the 'Object as Unit' experiment.

This script reads trial data from .mat files and renders experimental stimuli
for three experiments (Exp1, Exp2, Exp3), each with integrated and separate
group conditions across multiple phases (Memory, Cue, Search, Probe1, Probe2).
"""
import sys
import tomllib
import numpy as np
import random
import matplotlib.transforms as transforms
import matplotlib.patches as patches

from loguru import logger
from tqdm import tqdm
from pathlib import Path
from typing import Literal


logger.remove()
logger.add(sys.stderr, level="INFO")


from stimkit import Canvas, CanvasConfig, OutputConfig, Renderer, VisualAngle, load_mat_matrix, MatFormatError
from stimkit.collections.notched_circle import notched_circle
from stimkit.collections.lines import centered_line, cross_line
from stimkit.collections import circle, square, triangle, diamond, hexagon, semicircle
from stimkit.layouts import circular_positions

from config import (
    Phase, GroupType, ShapeType, 
    DistractorCondition, ProbeCondition, TargetOrientation, CueValue,
    TrialData, SceneConfig, StimuliAppConfig,
    Exp1Config, Exp2Config, Exp3Config
)

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR.parent / "output"
DATA_DIR = SCRIPT_DIR.parent / "data"
CONFIG_PATH = SCRIPT_DIR / "stimuli_config.toml"

# ==============================================================================
# Patch Factory Functions (decoupled from config/canvas)
# ==============================================================================
def shape_patch(
    shape_idx: int,
    xy: tuple[float, float],
    size: float,
    color: str,
    rotation: float,
    transform: transforms.Transform,
) -> patches.Patch:
    """
    Create a patch for various shapes.
    
    Parameters
    ----------
    shape_idx : int
        Shape type: 1=Square, 2=Triangle, 3=Diamond, 4=Hexagon, 5=Trapezoid, 6=Circle
    xy : tuple[float, float]
        Center position (x, y).
    size : float
        Size of the shape (side length or diameter).
    color : str
        Fill color.
    rotation : float
        Rotation angle in degrees.
    transform : Transform
        Matplotlib transform to apply.
    """
    x, y = xy
    r = size / 2
    match shape_idx:
        case ShapeType.SQUARE:
            return square(xy, size, color, transform, rotation=rotation)
        case ShapeType.TRIANGLE:
            return triangle(xy, r, color, transform, rotation=rotation - 90)
        case ShapeType.DIAMOND:
            return diamond(xy, r * 1.414, color, transform, rotation=rotation - 45)
        case ShapeType.HEXAGON:
            return hexagon(xy, r, color, transform, rotation=rotation)
        case ShapeType.TRAPEZOID:
            hw, hh = r, r
            pts = [(x - hw * 0.5, y + hh), (x + hw * 0.5, y + hh), (x + hw, y - hh), (x - hw, y - hh)]
            return patches.Polygon(pts, color=color, transform=transform)
        case ShapeType.CIRCLE:
            return circle(xy, r, color, transform)
        case _:
            raise ValueError(f"Unknown shape_idx: {shape_idx}. Valid values are 1-6.")


def search_array_patches(
    radius: float, item_size: float, colors: list[str], target_index: int,
    target_tilt: float, marker_ratio: float, line_width: float, transform: transforms.Transform,
    singleton_index: int | None = None, singleton_shape_idx: int | None = None
) -> list[patches.Patch]:
    """
    Create patches for a visual search array with 8 items (usually circles, optionally one shape singleton).
    
    Parameters
    ----------
    radius : float
        Radius of the circular arrangement.
    item_size : float
        Diameter/Size of each search item.
    colors : list[str]
        List of 8 colors for each item.
    target_index : int
        Index of the target item (gets tilted line, others get X).
    target_tilt : float
        Tilt angle for the target's line marker.
    marker_ratio : float
        Size ratio of markers relative to item_size.
    line_width : float
        Width of marker lines.
    transform : Transform
        Matplotlib transform.
    singleton_index : int | None
        Index of the singleton item in the array.
    singleton_shape_idx : int | None
        Shape index for the singleton item (if different from circle).
    """
    result = []
    item_radius = item_size / 2
    marker_size = item_size * marker_ratio
    
    positions = circular_positions(8, radius)
    for i, (cx, cy) in enumerate(positions):
        color = colors[i]
        
        # Determine shape: use specific shape if this is the singleton and a shape is specified;
        # otherwise use default Circle.
        if i == singleton_index and singleton_shape_idx is not None:
            # Use the shape factory
            result.append(shape_patch(singleton_shape_idx, (cx, cy), item_size, color, 0, transform))
        else:
            result.append(patches.Circle((cx, cy), radius=item_radius, color=color, transform=transform))
            
        if i == target_index:
            result.append(centered_line((cx, cy), marker_size, "black", target_tilt, transform, linewidth=line_width))
        else:
            result.extend(cross_line((cx, cy), marker_size, "black", 45, transform, linewidth=line_width))
    return result


# ==============================================================================
# Renderers
# ==============================================================================
class BaseStimuliRenderer(Renderer):
    """Base renderer with shared utilities for all experiments."""

    def __init__(self, canvas_cfg: CanvasConfig, app_cfg: StimuliAppConfig) -> None:
        super().__init__(canvas_cfg)
        self.app_cfg = app_cfg

    def get_color(self, idx: int) -> str:
        """Return color from palette by 1-based index."""
        palette = self.app_cfg.display.colors
        if not 1 <= idx <= len(palette):
            raise ValueError(f"Color index {idx} out of range (1..{len(palette)}).")
        return palette[idx - 1]

    def _get_unrelated_color(self, used_indices: list[int]) -> str:
        """Pick a random color from palette that is NOT in the used indices."""
        count = self.app_cfg.display.color_count
        candidates = [i for i in range(1, count + 1) if i not in used_indices]
        if not candidates:
            raise ValueError(f"No available colors for unrelated distractor. Used: {used_indices}, Total: {count}")
        return self.get_color(random.choice(candidates))

    def _is_probe_match(self, probe_idx: CueValue, probe_cond: ProbeCondition) -> bool:
        """
        Check if current probe should match the memory item.
        probe_cond: ONLY_FIRST_SAME, ONLY_SECOND_SAME, BOTH_DIFFERENT, BOTH_SAME
        """
        match probe_idx:
            case CueValue.FIRST:
                return probe_cond in [ProbeCondition.ONLY_FIRST_SAME, ProbeCondition.BOTH_SAME]
            case CueValue.SECOND:
                return probe_cond in [ProbeCondition.ONLY_SECOND_SAME, ProbeCondition.BOTH_SAME]
            case _:
                return False

    def add_shape(self, canvas: Canvas, shape_idx: int, color: str,
                  x: float, y: float, size: float, rotation: float = 0) -> None:
        """Add a shape at the given position in canvas units."""
        canvas.add_patch(shape_patch(shape_idx, (x, y), size, color, rotation, canvas.transData))

    def add_semicircle(self, canvas: Canvas, color: str, x: float,
                       y: float, size: float,
                       orientation: Literal["top", "bottom", "left", "right"]) -> None:
        """Add a semicircle at the given position in canvas units."""
        canvas.add_patch(semicircle((x, y), size / 2, color, canvas.transData, orientation=orientation))

    def add_search_array(self, canvas: Canvas, trial: TrialData, 
                         singleton_color: str | None,
                         singleton_shape: int | None = None) -> None:
        """
        Add the visual search array to canvas with randomized target and singleton positions.
        
        Parameters
        ----------
        canvas : Canvas
            Target canvas.
        trial : TrialData
            Trial data.
        singleton_color : str | None
            Color of the singleton item. If None, assumes no singleton (all gray).
        singleton_shape : int | None
            Shape index of the singleton item. If None or not applicable, defaults to Circle logic
            (handled by search_array_patches).
        """
        scfg = self.app_cfg.search
        rv = scfg.radius.value_in_unit(canvas)
        iv = scfg.item_size.value_in_unit(canvas)
        
        # Randomize target and singleton positions (ensure they differ)
        target_index = random.randint(0, 7)
        singleton_index = random.choice([i for i in range(8) if i != target_index])
        
        colors = []
        for i in range(8):
            if i == singleton_index and singleton_color is not None:
                colors.append(singleton_color)
            else:
                colors.append(scfg.base_color)
        tilt = scfg.tilt_pos if trial.target_orient == TargetOrientation.RIGHT else scfg.tilt_neg
        
        canvas.add_patches(
            search_array_patches(
                rv, iv, colors, target_index, tilt, scfg.marker_ratio, scfg.line_width, canvas.transData,
                singleton_index=singleton_index,
                singleton_shape_idx=singleton_shape
            )
        )

    def add_color_probe(self, canvas: Canvas, trial: TrialData, idx: CueValue, size_unit: float) -> None:
        """Add a color probe stimulus."""
        # Determine reference color
        # If cue_val == idx (both 1 or both 2), we probe col1 (Top/Color).
        # Otherwise, we probe col2 (Bottom/Shape).
        is_probing_col1 = (trial.cue_val == idx)
        ref_color_idx = trial.col1 if is_probing_col1 else trial.col2

        should_match = self._is_probe_match(idx, trial.probe_cond)
        
        # Calculate final color index
        if should_match:
            final_color_idx = ref_color_idx
        else:
            # Deterministic mismatch: next color in cycle
            final_color_idx = (ref_color_idx % self.app_cfg.display.color_count) + 1
            
        self.add_shape(canvas, ShapeType.CIRCLE, self.get_color(final_color_idx), 0.0, 0.0, size_unit)


class Exp1Renderer(BaseStimuliRenderer):
    """Renderer for Experiment 1: Color-Shape binding."""

    def __init__(self, canvas_cfg: CanvasConfig, app_cfg: StimuliAppConfig, exp_cfg: Exp1Config) -> None:
        super().__init__(canvas_cfg, app_cfg)
        self.exp_cfg = exp_cfg

    def _get_singleton_spec(self, t: TrialData) -> tuple[str | None, int | None]:
        """
        Resolve singleton (color, shape) based on dist_cond for Exp1.
        
        Per data/README.md:
        - dist_cond=1 OR dist_cond=2: "color of distractor match the color in memory display"
          (both are EQUIVALENT, representing color match)
        - dist_cond=3: unrelated
        - dist_cond=4: no singleton
        
        Note: The distinction between "related first" vs "related second" is determined
        by combining dist_cond with cue_val during ANALYSIS, but for RENDERING,
        dist_cond=1 and dist_cond=2 both produce the same color singleton.
        
        Returns
        -------
        (color, shape_idx)
            color: str or None (if no singleton)
            shape_idx: int or None (always Circle for color singleton, or specific shape for future extension)
        """
        match t.dist_cond:
            case DistractorCondition.NO_SINGLETON:
                return None, None
            case DistractorCondition.RELATED_FIRST | DistractorCondition.RELATED_SECOND:
                # Color singleton: Color from col1 + Standard Circle
                # README: "value 1 and 2 represent the color of the distractor match the color in the memory display"
                return self.get_color(t.col1), ShapeType.CIRCLE
            case DistractorCondition.UNRELATED:
                # Unrelated: Random new color + Standard Circle
                return self._get_unrelated_color([t.col1]), ShapeType.CIRCLE
            case _:
                return None, None

    def draw(self, canvas: Canvas, cfg: SceneConfig) -> None:
        match cfg.phase:
            case Phase.MEMORY:
                self._draw_memory(canvas, cfg)
            case Phase.CUE:
                self._draw_cue(canvas, cfg)
            case Phase.SEARCH:
                c, s = self._get_singleton_spec(cfg.trial_data)
                self.add_search_array(canvas, cfg.trial_data, c, singleton_shape=s)
            case Phase.PROBE1:
                self._draw_probe(canvas, cfg, CueValue.FIRST)
            case Phase.PROBE2:
                self._draw_probe(canvas, cfg, CueValue.SECOND)

    def _draw_memory(self, canvas: Canvas, cfg: SceneConfig) -> None:
        t, c = cfg.trial_data, self.get_color(cfg.trial_data.col1)
        match cfg.group_type:
            case GroupType.INTEGRATED:
                size_u = self.exp_cfg.integrated_item_size.value_in_unit(canvas)
                self.add_shape(canvas, t.col2, c, 0.0, 0.0, size_u)
            case GroupType.SEPARATE:
                d = self.exp_cfg.separate_offset.value_in_unit(canvas)
                size_u = self.exp_cfg.separate_item_size.value_in_unit(canvas)
                self.add_shape(canvas, t.col2, self.exp_cfg.separate_shape_color, -d, d, size_u)
                self.add_shape(canvas, ShapeType.CIRCLE, c, d, -d, size_u)

    def _draw_cue(self, canvas: Canvas, cfg: SceneConfig) -> None:
        txt = self.app_cfg.display.cue_text
        match cfg.trial_data.cue_val:
            case CueValue.FIRST:
                cue = txt.exp1_color
            case CueValue.SECOND:
                cue = txt.exp1_shape
            case _:
                cue = ""
        canvas.add_text((0, 0), cue, fontsize=self.app_cfg.display.cue_font_size, ha="center", va="center")

    def _draw_probe(self, canvas: Canvas, cfg: SceneConfig, idx: CueValue) -> None:
        t, disp = cfg.trial_data, self.app_cfg.display
        should_match = self._is_probe_match(idx, t.probe_cond)
        
        # Determine if we are probing Color or Shape based on Cue and Probe Order.
        # Paper (Exp 1): "one of the memory features (shape or color) was cued... indicating which feature would be probed first."
        # Logic: 
        #   If Cue == 1 (Color): Probe 1 is Color, Probe 2 is Shape.
        #   If Cue == 2 (Shape): Probe 1 is Shape, Probe 2 is Color.
        # This simplifies to: is_color if (Cue=1 and Probe=1) OR (Cue=2 and Probe=2).
        is_color_feature = (t.cue_val == CueValue.FIRST and idx == CueValue.FIRST) or (t.cue_val == CueValue.SECOND and idx == CueValue.SECOND)
        
        size = self.exp_cfg.integrated_item_size if cfg.group_type == GroupType.INTEGRATED else self.exp_cfg.separate_item_size
        size_u = size.value_in_unit(canvas)

        if is_color_feature:
            c_idx = t.col1 if should_match else (t.col1 % disp.color_count) + 1
            self.add_shape(canvas, ShapeType.CIRCLE, self.get_color(c_idx), 0.0, 0.0, size_u)
        else:
            s_idx = t.col2 if should_match else (t.col2 % disp.shape_count) + 1
            self.add_shape(canvas, s_idx, self.exp_cfg.separate_shape_color, 0.0, 0.0, size_u)


class Exp2Renderer(BaseStimuliRenderer):
    """Renderer for Experiment 2: Semicircle color binding."""

    def __init__(self, canvas_cfg: CanvasConfig, app_cfg: StimuliAppConfig, exp_cfg: Exp2Config) -> None:
        super().__init__(canvas_cfg, app_cfg)
        self.exp_cfg = exp_cfg

    def _get_singleton_color(self, t: TrialData) -> str | None:
        """
        Resolve singleton color for Exp2 based on dist_cond and cue_val.
        
        Per data/README.md:
        - dist_cond=1: related FIRST probe
        - dist_cond=2: related SECOND probe
        - dist_cond=3: unrelated
        - dist_cond=4: no singleton
        
        To map "first/second probe" to actual colors (col1/col2), we need cue_val:
        - cue_val=1: Upper (col1) tested first
          - dist_cond=1 (first) => match col1
          - dist_cond=2 (second) => match col2
        - cue_val=2: Lower (col2) tested first
          - dist_cond=1 (first) => match col2
          - dist_cond=2 (second) => match col1
        """
        match t.dist_cond:
            case DistractorCondition.NO_SINGLETON:
                return None
            case DistractorCondition.UNRELATED:
                return self._get_unrelated_color([t.col1, t.col2])
            case DistractorCondition.RELATED_FIRST:
                target_idx = t.col1 if t.cue_val == CueValue.FIRST else t.col2
                return self.get_color(target_idx)
            case DistractorCondition.RELATED_SECOND:
                target_idx = t.col2 if t.cue_val == CueValue.FIRST else t.col1
                return self.get_color(target_idx)
            case _:
                return None

    def draw(self, canvas: Canvas, cfg: SceneConfig) -> None:
        match cfg.phase:
            case Phase.MEMORY:
                self._draw_memory(canvas, cfg)
            case Phase.CUE:
                self._draw_cue(canvas, cfg)
            case Phase.SEARCH:
                self.add_search_array(canvas, cfg.trial_data, self._get_singleton_color(cfg.trial_data))
            case Phase.PROBE1 | Phase.PROBE2:
                idx = CueValue.FIRST if cfg.phase == Phase.PROBE1 else CueValue.SECOND
                size = self.exp_cfg.integrated_item_size if cfg.group_type == GroupType.INTEGRATED else self.exp_cfg.separate_item_size
                size_u = size.value_in_unit(canvas)
                self.add_color_probe(canvas, cfg.trial_data, idx, size_u)

    def _draw_memory(self, canvas: Canvas, cfg: SceneConfig) -> None:
        c1, c2 = self.get_color(cfg.trial_data.col1), self.get_color(cfg.trial_data.col2)
        e = self.exp_cfg
        match cfg.group_type:
            case GroupType.INTEGRATED:
                x = e.integrated_x.value_in_unit(canvas)
                y = e.integrated_y.value_in_unit(canvas)
                size = e.integrated_item_size.value_in_unit(canvas)
                self.add_semicircle(canvas, c1, x, y, size, "top")
                self.add_semicircle(canvas, c2, x, y, size, "bottom")
            case GroupType.SEPARATE:
                left_x = e.separate_left_x.value_in_unit(canvas)
                left_y = e.separate_left_y.value_in_unit(canvas)
                right_x = e.separate_right_x.value_in_unit(canvas)
                right_y = e.separate_right_y.value_in_unit(canvas)
                size = e.separate_item_size.value_in_unit(canvas)
                self.add_semicircle(canvas, c1, left_x, left_y, size, e.separate_left_orientation)
                self.add_semicircle(canvas, c2, right_x, right_y, size, e.separate_right_orientation)

    def _draw_cue(self, canvas: Canvas, cfg: SceneConfig) -> None:
        txt = self.app_cfg.display.cue_text
        match cfg.trial_data.cue_val:
            case CueValue.FIRST:
                cue = txt.exp2_up
            case CueValue.SECOND:
                cue = txt.exp2_down
            case _:
                cue = ""
        canvas.add_text((0, 0), cue, fontsize=self.app_cfg.display.cue_font_size, ha="center", va="center")


class Exp3Renderer(BaseStimuliRenderer):
    """Renderer for Experiment 3: Notched circles with gestalt closure."""

    def __init__(self, canvas_cfg: CanvasConfig, app_cfg: StimuliAppConfig, exp_cfg: Exp3Config) -> None:
        super().__init__(canvas_cfg, app_cfg)
        self.exp_cfg = exp_cfg

    def _get_singleton_color(self, t: TrialData) -> str | None:
        """
        Resolve singleton color for Exp3 based on dist_cond and cue_val.
        
        Per data/README.md (identical to Exp2):
        - dist_cond=1: related FIRST probe
        - dist_cond=2: related SECOND probe
        - dist_cond=3: unrelated
        - dist_cond=4: no singleton
        
        To map "first/second probe" to actual colors (col1/col2), we need cue_val:
        - cue_val=1: Upper (col1) tested first
          - dist_cond=1 (first) => match col1
          - dist_cond=2 (second) => match col2
        - cue_val=2: Lower (col2) tested first
          - dist_cond=1 (first) => match col2
          - dist_cond=2 (second) => match col1
        """
        match t.dist_cond:
            case DistractorCondition.NO_SINGLETON:
                return None
            case DistractorCondition.UNRELATED:
                return self._get_unrelated_color([t.col1, t.col2])
            case DistractorCondition.RELATED_FIRST:
                target_idx = t.col1 if t.cue_val == CueValue.FIRST else t.col2
                return self.get_color(target_idx)
            case DistractorCondition.RELATED_SECOND:
                target_idx = t.col2 if t.cue_val == CueValue.FIRST else t.col1
                return self.get_color(target_idx)
            case _:
                return None

    def draw(self, canvas: Canvas, cfg: SceneConfig) -> None:
        match cfg.phase:
            case Phase.MEMORY:
                self._draw_memory(canvas, cfg)
            case Phase.CUE:
                self._draw_cue(canvas, cfg)
            case Phase.SEARCH:
                self.add_search_array(canvas, cfg.trial_data, self._get_singleton_color(cfg.trial_data))
            case Phase.PROBE1 | Phase.PROBE2:
                size_u = self.exp_cfg.probe_item_size.value_in_unit(canvas)
                idx = CueValue.FIRST if cfg.phase == Phase.PROBE1 else CueValue.SECOND
                self.add_color_probe(canvas, cfg.trial_data, idx, size_u)

    def _draw_memory(self, canvas: Canvas, cfg: SceneConfig) -> None:
        c1, c2 = self.get_color(cfg.trial_data.col1), self.get_color(cfg.trial_data.col2)
        e = self.exp_cfg
        radius_u = e.radius.value_in_unit(canvas)
        notch_u = e.notch_side.value_in_unit(canvas)
        y_u = e.vertical_offset.value_in_unit(canvas)
        bg = self.app_cfg.canvas.bg_color
        top_angle = e.integrated_top_angle
        bot_angle = e.integrated_bottom_angle
        if cfg.group_type == GroupType.SEPARATE:
            # Randomly rotate ONE component by ±90° from integrated angles to break closure (per paper).
            rotate_top = random.choice([True, False])
            delta = random.choice([-90, 90])
            if rotate_top:
                top_angle = (top_angle + delta) % 360
            else:
                bot_angle = (bot_angle + delta) % 360
        canvas.add_patches(notched_circle((0, y_u), radius_u, notch_u, c1, bg, top_angle, canvas.transData))
        canvas.add_patches(notched_circle((0, -y_u), radius_u, notch_u, c2, bg, bot_angle, canvas.transData))

    def _draw_cue(self, canvas: Canvas, cfg: SceneConfig) -> None:
        txt = self.app_cfg.display.cue_text
        match cfg.trial_data.cue_val:
            case CueValue.FIRST:
                cue = txt.exp2_up
            case CueValue.SECOND:
                cue = txt.exp2_down
            case _:
                cue = ""
        canvas.add_text((0, 0), cue, fontsize=self.app_cfg.display.cue_font_size, ha="center", va="center")


# ==============================================================================
# Data Loading
# ==============================================================================
def load_config(path: Path) -> StimuliAppConfig:
    """Load and parse the TOML configuration file."""
    with path.open("rb") as f:
        return StimuliAppConfig(**tomllib.load(f))





def load_trials(file_path: Path, columns: list[str], *, allow_extra_cols: bool = True) -> list[TrialData]:
    """
    Strict trial data loader from .mat files.
    
    This function validates:
    - Column names match expected trial data fields
    - Matrix has sufficient columns
    - Factor columns contain integer-like values (MATLAB often saves as float)
    - No NaN/Inf values are present
    
    Parameters
    ----------
    file_path : Path
        Path to the .mat file containing trial data.
    columns : list[str]
        Expected column names in order.
    allow_extra_cols : bool, default True
        If True, allows additional columns beyond those specified.
        If False, raises an error if matrix has more columns than expected.
    
    Returns
    -------
    list[TrialData]
        List of validated trial data objects.
    
    Raises
    ------
    ValueError
        If column names don't match expected set.
    MatFormatError
        If matrix format is invalid or data validation fails.
    """
    expected = {"col1", "col2", "dist_cond", "target_orient", "cue_val", "probe_cond"}
    if set(columns) != expected:
        raise ValueError(f"Trial columns mismatch. Expected {sorted(expected)}, got {columns}.")

    data = load_mat_matrix(file_path, var_name="results")

    k = len(columns)
    if data.shape[1] < k:
        raise MatFormatError(
            f"{file_path}: matrix has {data.shape[1]} cols, but need at least {k}."
        )

    if (not allow_extra_cols) and data.shape[1] != k:
        raise MatFormatError(
            f"{file_path}: matrix has {data.shape[1]} cols, expected exactly {k}."
        )

    # Extract factor columns (first k columns)
    factor = data[:, :k]

    # Validate that factor columns contain integer-like values
    # MATLAB often saves integers as floats, so we check if they're close to integers
    if not np.all(np.isclose(factor, np.round(factor))):
        bad_rows = ~np.isclose(factor, np.round(factor))
        bad_values = factor[bad_rows.any(axis=1)]
        raise MatFormatError(
            f"{file_path}: non-integer-like values in factor columns. "
            f"Examples: {bad_values[:3].tolist()}"
        )

    # Convert to integer
    factor = np.round(factor).astype(np.int64)

    # Build TrialData objects
    trials: list[TrialData] = []
    for row in factor:
        payload = {name: int(row[i]) for i, name in enumerate(columns)}
        trials.append(TrialData(**payload))

    return trials


# ==============================================================================
# Rendering Pipeline
# ==============================================================================
def group_type_from_name(app_cfg: StimuliAppConfig, group_name: str) -> GroupType:
    """Convert group folder name to GroupType literal."""
    if group_name == app_cfg.data.integrated_group:
        return GroupType.INTEGRATED
    if group_name == app_cfg.data.separate_group:
        return GroupType.SEPARATE
    raise ValueError(f"Unknown group name: {group_name}")


def render_experiment(exp_name: str, renderer: BaseStimuliRenderer,
                      trial_columns: list[str], app_cfg: StimuliAppConfig) -> None:
    """Render all trials for an experiment across all groups and phases."""
    for group in app_cfg.data.groups:
        group_type = group_type_from_name(app_cfg, group)
        for file_path in tqdm(sorted((DATA_DIR / exp_name / group).glob("*.mat")), desc=f"{exp_name} {group}"):
            trials = load_trials(file_path, trial_columns)
            out_dir = OUTPUT_DIR / exp_name / group / file_path.stem
            out_dir.mkdir(parents=True, exist_ok=True)
            for i, trial in enumerate(trials[: app_cfg.render.max_trials]):
                for idx, phase in enumerate(app_cfg.render.phases):
                    cfg = SceneConfig(group_type=group_type, phase=phase, trial_data=trial)
                    output_path = out_dir / f"Trial_{i+1}_{idx+1}_{phase.value}.{app_cfg.render.output_format}"
                    renderer.render(cfg, OutputConfig(file_path=str(output_path)))


def make_canvas_cfg(app_cfg: StimuliAppConfig) -> CanvasConfig:
    """Extract CanvasConfig from app configuration."""
    return app_cfg.canvas


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Reproduce stimuli from the 'Object as Unit' experiment.",
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
        help="Ignore all limits and process all trials"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(CONFIG_PATH)
    
    # Apply --full flag: set max_trials to 0 (no limit)
    if args.full:
        config.render.max_trials = 0
        logger.info("Running in FULL mode: processing all trials")
    else:
        logger.info(f"Running with limit: max_trials={config.render.max_trials}")
    
    # Set random seeds
    random.seed(config.render.seed)
    np.random.seed(config.render.seed)
    
    canvas_cfg = make_canvas_cfg(config)
    exps = config.experiments
    
    # Determine which experiments to run
    experiments_to_run = {
        "E1": ("Exp1", Exp1Renderer(canvas_cfg, config, exps.exp1), exps.exp1.trial_columns),
        "E2": ("Exp2", Exp2Renderer(canvas_cfg, config, exps.exp2), exps.exp2.trial_columns),
        "E3": ("Exp3", Exp3Renderer(canvas_cfg, config, exps.exp3), exps.exp3.trial_columns),
    }
    
    if args.exp == "all":
        selected = experiments_to_run.values()
    else:
        selected = [experiments_to_run[args.exp]]
    
    # Run selected experiments
    for exp_name, renderer, trial_cols in selected:
        logger.info(f"Processing {exp_name}...")
        render_experiment(exp_name, renderer, trial_cols, config)
