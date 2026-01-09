"""
Reproduce stimuli for: "The Basic Units of Working Memory Manipulation Are Boolean Maps, Not Objects".

This implementation uses trial-level condition fields from ManipulationUnit-Data-All.xlsx
and generates deterministic, condition-consistent stimuli using stimkit. Because the
raw data do not include per-trial item-level parameters, stimuli are synthesized with a
fixed RNG seed while preserving the critical experimental constraints (conditions and
consistency flags) described in the paper.
"""
from __future__ import annotations

import argparse
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from tqdm import tqdm

import matplotlib.patches as patches
import matplotlib.transforms as transforms
from loguru import logger

# Configure loguru to use tqdm.write to avoid breaking progress bars.
logger.remove()
logger.add(
    lambda msg: tqdm.write(msg, end=""),
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    backtrace=True,
    diagnose=True,
    enqueue=True,
    colorize=True,
)

from stimkit import Canvas, CanvasConfig, OutputConfig, Renderer, VisualAngle
from stimkit.collections import circle, semicircle
from stimkit.collections.lines import centered_line
from stimkit.layouts import grid_positions

from config import (
    StimuliAppConfig,
    SceneConfig,
    Exp1SceneInputs,
    Exp2SceneInputs,
    Exp3SceneInputs,
    Exp4SceneInputs,
    ExperimentType,
    Phase,
    Exp1Condition,
    Exp1Consistency,
    Exp1TrialData,
    Exp2Condition,
    Exp2Consistency,
    Exp2TrialData,
    Exp3ColorOrientationType,
    Exp3Direction,
    Exp3ChangeAttribute,
    Exp3TrialData,
    Exp4Condition,
    Exp4Consistency,
    Exp4TrialData,
)

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_DIR = SCRIPT_DIR.parent / "output"
CONFIG_PATH = SCRIPT_DIR / "stimuli_config.toml"

XLSX_PATH = DATA_DIR / "ManipulationUnit-Data-All.xlsx"


# =============================
# XSLX Reader (polars -> pandas)
# =============================


def load_sheet_records(
    path: Path,
    sheet_name: str,
    columns: list[str] | None = None,
) -> list[dict[str, Any]]:
    import pandas as pd
    df = pd.read_excel(path, sheet_name=sheet_name, usecols=columns)
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
    df = df.dropna(how="all")
    df = df.where(df.notna(), None)
    return df.to_dict(orient="records")


def coerce_int_fields(records: list[dict[str, Any]], fields: list[str]) -> None:
    for record in records:
        for field in fields:
            if field not in record:
                continue
            value = record[field]
            if value is None:
                continue
            try:
                record[field] = int(float(value))
            except (ValueError, TypeError):
                pass




# =============================
# Rendering helpers
# =============================

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def sample_grid_window_indices(
    rows: int,
    cols: int,
    window_rows: int,
    window_cols: int,
    *,
    row_starts: list[int],
    col_starts: list[int],
    rng: random.Random,
    shuffle: bool = False,
) -> list[int]:
    if rows <= 0 or cols <= 0 or window_rows <= 0 or window_cols <= 0:
        return []
    if not row_starts or not col_starts:
        return []

    row_start = rng.choice(row_starts)
    col_start = rng.choice(col_starts)
    if row_start + window_rows > rows or col_start + window_cols > cols:
        return []

    indices = []
    for r in range(row_start, row_start + window_rows):
        for c in range(col_start, col_start + window_cols):
            indices.append(r * cols + c)
    if shuffle and indices:
        rng.shuffle(indices)
    return indices


def ring_patch(
    xy: tuple[float, float], radius: float, line_width: float, color: str, transform: transforms.Transform
) -> patches.Patch:
    return circle(xy, radius, color, transform, fill=False, linewidth=line_width)


def arrow_patch(
    start: tuple[float, float],
    end: tuple[float, float],
    color: str,
    line_width: float,
    transform: transforms.Transform,
) -> patches.Patch:
    return patches.FancyArrowPatch(
        posA=start,
        posB=end,
        arrowstyle="-|>",
        mutation_scale=max(line_width * 4.0, 6.0),
        color=color,
        linewidth=line_width,
        transform=transform,
    )


def arrow_for_direction(
    center: tuple[float, float],
    direction: str,
    length: float,
) -> tuple[tuple[float, float], tuple[float, float]]:
    cx, cy = center
    half = length / 2
    if direction == "up":
        return (cx, cy - half), (cx, cy + half)
    if direction == "down":
        return (cx, cy + half), (cx, cy - half)
    if direction == "left":
        return (cx + half, cy), (cx - half, cy)
    return (cx - half, cy), (cx + half, cy)


def mask_patches(
    canvas: Canvas,
    palette: list[str],
    spacing_unit: float,
    radius_unit: float,
    mode: str = "circle",
) -> None:
    positions = grid_positions(4, 4, spacing_unit, center=(0.0, 0.0), order="row-major")
    for cx, cy in positions:
        if mode == "circle":
            num_colors = len(palette)
            angle_step = 360 / num_colors
            for i, color in enumerate(palette):
                canvas.add_patch(
                    patches.Wedge(
                        (cx, cy),
                        radius_unit,
                        i * angle_step,
                        (i + 1) * angle_step,
                        color=color,
                        transform=canvas.transData,
                    )
                )
        elif mode == "cross":
            width_pt = VisualAngle(value=0.1).value_in_points(canvas, min_points=0.5)
            length_unit = radius_unit * 2
            for ang in [0, 45, 90, 135]:
                for color in palette:
                    canvas.add_patch(
                        centered_line((cx, cy), length_unit, color, ang, canvas.transData, linewidth=width_pt)
                    )


def connector_patch(
    xy: tuple[float, float], length: float, width: float, color: str, angle: float, transform: transforms.Transform
) -> patches.Patch:
    rect = patches.Rectangle(
        xy=(xy[0] - length / 2, xy[1] - width / 2),
        width=length,
        height=width,
        color=color,
        transform=(
            transforms.Affine2D().rotate_deg_around(x=xy[0], y=xy[1], degrees=angle) + transform
        ),
    )
    return rect


def dumbbell_patches(
    center: tuple[float, float],
    orientation: str,
    radius: float,
    connector_length: float,
    connector_width: float,
    colors: tuple[str, str],
    transform: transforms.Transform,
) -> tuple[list[patches.Patch], dict[int, tuple[float, float]]]:
    cx, cy = center
    half = connector_length / 2
    if orientation == "horizontal":
        end_positions = {0: (cx - half, cy), 1: (cx + half, cy)}
        angle = 0
    else:
        end_positions = {0: (cx, cy + half), 1: (cx, cy - half)}
        angle = 90

    left = patches.Circle(end_positions[0], radius=radius, color=colors[0], transform=transform)
    right = patches.Circle(end_positions[1], radius=radius, color=colors[1], transform=transform)
    connector = connector_patch((cx, cy), connector_length, connector_width, "gray", angle, transform)
    return [connector, left, right], end_positions


def semicircle_patches(
    center: tuple[float, float],
    radius: float,
    color_a: str,
    color_b: str,
    orientation: str,
    transform: transforms.Transform,
) -> list[patches.Patch]:
    if orientation == "horizontal":
        return [
            semicircle(center, radius, color_a, transform, orientation="left"),
            semicircle(center, radius, color_b, transform, orientation="right"),
        ]
    return [
        semicircle(center, radius, color_a, transform, orientation="top"),
        semicircle(center, radius, color_b, transform, orientation="bottom"),
    ]


def draw_grid(
    canvas: Canvas,
    spacing_unit: float,
    line_width_pt: float,
    size_unit: float,
    color: str,
) -> None:
    half = size_unit / 2
    count = int(round(size_unit / spacing_unit))
    coords = [(-half + i * spacing_unit) for i in range(count + 1)]
    for coord in coords:
        canvas.add_patch(centered_line((coord, 0), size_unit, color, 90, canvas.transData, linewidth=line_width_pt))
        canvas.add_patch(centered_line((0, coord), size_unit, color, 0, canvas.transData, linewidth=line_width_pt))





def move_positions_direction(
    positions: list[tuple[float, float]],
    indices: list[int],
    direction: str,
    spacing: float,
    coords: list[float],
) -> list[tuple[float, float]]:
    dir_map = {
        "up": (0, spacing),
        "down": (0, -spacing),
        "left": (-spacing, 0),
        "right": (spacing, 0),
    }
    dx, dy = dir_map[direction]
    new_positions = list(positions)
    occupied = {pos: idx for idx, pos in enumerate(positions)}

    coord_min = min(coords)
    coord_max = max(coords)

    def wrap(value: float) -> float:
        if value < coord_min:
            return coord_max
        if value > coord_max:
            return coord_min
        return value

    for idx in sorted(indices):
        x, y = new_positions[idx]
        target = (wrap(x + dx), wrap(y + dy))
        if target in occupied:
            other_idx = occupied[target]
            new_positions[other_idx] = (x, y)
            occupied[(x, y)] = other_idx
        new_positions[idx] = target
        occupied[target] = idx
    return new_positions




# =============================
# StimuliRenderer Class
# =============================

class StimuliRenderer(Renderer):
    """Renderer for Boolean map manipulation experiments."""
    
    def __init__(self, canvas_cfg: CanvasConfig, app_cfg: StimuliAppConfig):
        super().__init__(canvas_cfg)
        self.app_cfg = app_cfg
    
    def draw(self, canvas: Canvas, scene_cfg: SceneConfig) -> None:
        """Main draw method that delegates to experiment-specific renderers."""
        match scene_cfg.experiment_type:
            case ExperimentType.E1:
                self._draw_exp1(canvas, scene_cfg, scene_cfg.phase)
            case ExperimentType.E2:
                self._draw_exp2(canvas, scene_cfg, scene_cfg.phase)
            case ExperimentType.E3:
                self._draw_exp3(canvas, scene_cfg, scene_cfg.phase)
            case ExperimentType.E4:
                self._draw_exp4(canvas, scene_cfg, scene_cfg.phase)
    
    def _draw_exp1(self, canvas: Canvas, scene_cfg: Exp1SceneInputs, phase: Phase) -> None:
        """Draw Experiment 1 stimuli."""
        cfg = self.app_cfg
        rng = random.Random(scene_cfg.seed)
        palette = cfg.display.palette
        obj_colors, cued, dye_colors = self._exp1_assign_colors(scene_cfg.trial_data.conditions, palette, rng)
        manipulated_colors = self._exp1_apply_dye(obj_colors, cued, dye_colors)
        test_colors = self._exp1_apply_consistency(
            manipulated_colors, cued, palette, rng, scene_cfg.trial_data.consis
        )
        orientation = "horizontal" if scene_cfg.trial_data.orientation == 0 else "vertical"
        match phase:
            case Phase.MASK:
                mask_palette = list(set([c for pair in obj_colors for c in pair] + dye_colors))
                spacing_unit = cfg.exp1.mask_spacing.value_in_unit(canvas)
                radius_unit = cfg.exp1.mask_radius.value_in_unit(canvas)
                mask_patches(canvas, mask_palette, spacing_unit=spacing_unit, radius_unit=radius_unit, mode="circle")
                return
            case Phase.MEMORY | Phase.TEST:
                colors = test_colors if phase == Phase.TEST else obj_colors
                obj_radius_unit = cfg.exp1.object_radius.value_in_unit(canvas)
                centers_unit = [(-obj_radius_unit, 0.0), (obj_radius_unit, 0.0)]
                
                radius_unit = cfg.exp1.dumbbell_radius.value_in_unit(canvas)
                conn_len_unit = cfg.exp1.connector_length.value_in_unit(canvas)
                conn_width_unit = cfg.exp1.connector_width.value_in_unit(canvas)

                for obj_idx, (cx, cy) in enumerate(centers_unit):
                    patches_obj, _ = dumbbell_patches(
                        (cx, cy), orientation, radius_unit, conn_len_unit, 
                        conn_width_unit, colors[obj_idx], canvas.transData
                    )
                    for patch in patches_obj:
                        canvas.add_patch(patch)
            case Phase.CUE:
                obj_radius_unit = cfg.exp1.object_radius.value_in_unit(canvas)
                centers_unit = [(-obj_radius_unit, 0.0), (obj_radius_unit, 0.0)]
                radius_unit = cfg.exp1.dumbbell_radius.value_in_unit(canvas)
                conn_len_unit = cfg.exp1.connector_length.value_in_unit(canvas)
                conn_width_unit = cfg.exp1.connector_width.value_in_unit(canvas)

                cue_positions: list[tuple[float, float, str]] = []
                for obj_idx, (cx, cy) in enumerate(centers_unit):
                    _, end_positions = dumbbell_patches(
                        (cx, cy), orientation, radius_unit, conn_len_unit, 
                        conn_width_unit, [("black", "black"), ("black", "black")][obj_idx], canvas.transData
                    )
                    for (cue_obj, end_idx), dye in zip(cued, dye_colors):
                        if cue_obj == obj_idx:
                            pos = end_positions[end_idx]
                            cue_positions.append((pos[0], pos[1], dye))

                cue_radius_unit = cfg.exp1.cue_radius.value_in_unit(canvas)
                cue_width_pt = cfg.exp1.cue_line_width.value_in_points(canvas, min_points=0.5)
                for x, y, cue_color in cue_positions:
                    canvas.add_patch(ring_patch((x, y), cue_radius_unit, cue_width_pt, cue_color, canvas.transData))

    def _exp1_assign_colors(
        self,
        condition: int,
        palette: list[str],
        rng: random.Random,
    ) -> tuple[list[tuple[str, str]], list[tuple[int, int]], list[str]]:
        object_colors: list[tuple[str, str]] = [("black", "black"), ("black", "black")]

        match condition:
            case Exp1Condition.ONE_BINDING_ONE_OBJECT:
                cue_obj = rng.choice([0, 1])
                base = self._pick_color(palette, rng)
                object_colors[cue_obj] = (base, base)
                other = 1 - cue_obj
                other_colors = (
                    self._pick_color(palette, rng, {base}),
                    self._pick_color(palette, rng, {base}),
                )
                object_colors[other] = other_colors
                cued = [(cue_obj, 0), (cue_obj, 1)]
                dye = self._pick_color(palette, rng, {base})
                dye_colors = [dye, dye]
            case Exp1Condition.ONE_BINDING_TWO_OBJECTS:
                shared = self._pick_color(palette, rng)
                object_colors[0] = (shared, self._pick_color(palette, rng, {shared}))
                object_colors[1] = (shared, self._pick_color(palette, rng, {shared}))
                cued = [(0, 0), (1, 0)]
                dye = self._pick_color(palette, rng, {shared})
                dye_colors = [dye, dye]
            case Exp1Condition.TWO_BINDINGS_ONE_OBJECT:
                cue_obj = rng.choice([0, 1])
                color_a = self._pick_color(palette, rng)
                color_b = self._pick_color(palette, rng, {color_a})
                object_colors[cue_obj] = (color_a, color_b)
                other = 1 - cue_obj
                object_colors[other] = (
                    self._pick_color(palette, rng, {color_a, color_b}),
                    self._pick_color(palette, rng, {color_a, color_b}),
                )
                cued = [(cue_obj, 0), (cue_obj, 1)]
                dye_a, dye_b = self._pick_distinct_pair(palette, rng, {color_a, color_b})
                dye_colors = [dye_a, dye_b]
            case Exp1Condition.TWO_BINDINGS_TWO_OBJECTS:
                color_a = self._pick_color(palette, rng)
                color_b = self._pick_color(palette, rng, {color_a})
                object_colors[0] = (color_a, self._pick_color(palette, rng, {color_a, color_b}))
                object_colors[1] = (color_b, self._pick_color(palette, rng, {color_a, color_b}))
                cued = [(0, 0), (1, 0)]
                dye_a, dye_b = self._pick_distinct_pair(palette, rng, {color_a, color_b})
                dye_colors = [dye_a, dye_b]

        return object_colors, cued, dye_colors

    def _exp1_apply_dye(
        self,
        colors: list[tuple[str, str]],
        cued: list[tuple[int, int]],
        dye_colors: list[str],
    ) -> list[tuple[str, str]]:
        dyed_colors = [list(pair) for pair in colors]
        for (obj_idx, end_idx), dye in zip(cued, dye_colors):
            dyed_colors[obj_idx][end_idx] = dye
        return [tuple(pair) for pair in dyed_colors]

    def _exp1_apply_consistency(
        self,
        colors: list[tuple[str, str]],
        cued: list[tuple[int, int]],
        palette: list[str],
        rng: random.Random,
        consis: int,
    ) -> list[tuple[str, str]]:
        new_colors = [tuple(pair) for pair in colors]

        def swap_color(color: str) -> str:
            choices = [c for c in palette if c != color]
            return rng.choice(choices) if choices else color

        match consis:
            case Exp1Consistency.CONSISTENT:
                return new_colors
            case Exp1Consistency.CUED_CHANGED:
                for obj_idx, end_idx in cued:
                    pair = list(new_colors[obj_idx])
                    pair[end_idx] = swap_color(pair[end_idx])
                    new_colors[obj_idx] = tuple(pair)
            case Exp1Consistency.UNCUED_CHANGED:
                uncued = {(i, j) for i in range(2) for j in range(2)} - set(cued)
                for obj_idx, end_idx in uncued:
                    pair = list(new_colors[obj_idx])
                    pair[end_idx] = swap_color(pair[end_idx])
                    new_colors[obj_idx] = tuple(pair)
        return new_colors

    def _pick_color(
        self,
        palette: list[str],
        rng: random.Random,
        avoid: set[str] | None = None,
    ) -> str:
        avoid = avoid or set()
        choices = [c for c in palette if c not in avoid]
        if not choices:
            return rng.choice(palette)
        return rng.choice(choices)

    def _pick_distinct_pair(
        self,
        palette: list[str],
        rng: random.Random,
        avoid: set[str] | None = None,
    ) -> tuple[str, str]:
        avoid = avoid or set()
        choices = [c for c in palette if c not in avoid]
        if len(choices) >= 2:
            return tuple(rng.sample(choices, 2))
        if len(choices) == 1:
            return (choices[0], choices[0])
        first = rng.choice(palette)
        second_choices = [c for c in palette if c != first]
        second = rng.choice(second_choices) if second_choices else first
        return (first, second)
    
    def _draw_exp2(self, canvas: Canvas, scene_cfg: Exp2SceneInputs, phase: Phase) -> None:
        """Draw Experiment 2 stimuli."""
        cfg = self.app_cfg
        rng = random.Random(scene_cfg.seed)
        spacing_unit = cfg.exp2.grid_spacing.value_in_unit(canvas)
        radius_unit = cfg.exp2.circle_radius.value_in_unit(canvas)
        positions_unit = grid_positions(2, 2, spacing_unit, center=(0.0, 0.0))
        coords_unit = sorted({x for x, _ in grid_positions(4, 4, spacing_unit, center=(0.0, 0.0))})
        palette = cfg.display.palette
        color_a, color_b = rng.sample(palette[:5], 2) if len(palette) >= 2 else ("red", "green")
        solid_indices = [0, 3]
        bicolor_indices = [1, 2]
        match scene_cfg.trial_data.conditions:
            case Exp2Condition.ONE_BINDING_ONE_OBJECT:
                cued_indices = [solid_indices[0]]
            case Exp2Condition.ONE_BINDING_TWO_OBJECTS:
                cued_indices = solid_indices
            case Exp2Condition.TWO_BINDINGS_ONE_OBJECT:
                cued_indices = [bicolor_indices[0]]
            case Exp2Condition.TWO_BINDINGS_TWO_OBJECTS:
                cued_indices = [solid_indices[0], bicolor_indices[0]]
        item_colors: list[list[str]] = []
        for idx in range(len(positions_unit)):
            if idx in solid_indices:
                item_colors.append([color_a, color_a])
            else:
                item_colors.append([color_a, color_b])
        direction = rng.choice(["up", "down", "left", "right"])
        orientation = "horizontal" if scene_cfg.trial_data.orientation == 0 else "vertical"

        match phase:
            case Phase.MASK:
                mask_palette = list(set([c for pair in item_colors for c in pair]))
                mask_patches(canvas, mask_palette, spacing_unit=spacing_unit, radius_unit=radius_unit, mode="circle")
                return
            case Phase.MEMORY | Phase.TEST:
                line_width_pt = cfg.exp2.grid_line_width.value_in_points(canvas, min_points=0.5)
                draw_grid(
                    canvas, spacing_unit=spacing_unit, line_width_pt=line_width_pt, 
                    size_unit=spacing_unit * 4, color=cfg.exp2.grid_color
                )
                
                draw_positions_unit = positions_unit
                if phase == Phase.TEST and scene_cfg.trial_data.consis != Exp2Consistency.POSITION_CHANGED:
                    draw_positions_unit = move_positions_direction(
                        positions_unit, cued_indices, direction, spacing_unit, coords_unit
                    )
                draw_colors = [list(c) for c in item_colors]
                if phase == Phase.TEST:
                    match scene_cfg.trial_data.consis:
                        case Exp2Consistency.CUED_CHANGED:
                            for idx in cued_indices:
                                if idx in solid_indices:
                                    alt = [c for c in palette if c != draw_colors[idx][0]]
                                    draw_colors[idx][0] = alt[0] if alt else draw_colors[idx][0]
                                    draw_colors[idx][1] = draw_colors[idx][0]
                                else:
                                    draw_colors[idx][0], draw_colors[idx][1] = (
                                        draw_colors[idx][1],
                                        draw_colors[idx][0],
                                    )
                        case Exp2Consistency.UNCUED_CHANGED:
                            for idx in range(len(draw_colors)):
                                if idx not in cued_indices:
                                    alt = [c for c in palette if c != draw_colors[idx][0]]
                                    draw_colors[idx][0] = alt[0] if alt else draw_colors[idx][0]
                                    draw_colors[idx][1] = (
                                        draw_colors[idx][0] if idx in solid_indices else draw_colors[idx][1]
                                    )
                                    break
                        case Exp2Consistency.SOLID_UNCUED_CHANGED:
                            for idx in solid_indices:
                                if idx not in cued_indices:
                                    alt = [c for c in palette if c != draw_colors[idx][0]]
                                    draw_colors[idx][0] = alt[0] if alt else draw_colors[idx][0]
                                    draw_colors[idx][1] = draw_colors[idx][0]
                                    break
                for idx, (cx, cy) in enumerate(draw_positions_unit):
                    if draw_colors[idx][0] == draw_colors[idx][1]:
                        canvas.add_patch(
                            patches.Circle((cx, cy), radius=radius_unit, color=draw_colors[idx][0], transform=canvas.transData)
                        )
                    else:
                        for patch in semicircle_patches(
                            (cx, cy), radius_unit, draw_colors[idx][0], draw_colors[idx][1], orientation, canvas.transData
                        ):
                            canvas.add_patch(patch)
            case Phase.CUE:
                line_width_pt = cfg.exp2.grid_line_width.value_in_points(canvas, min_points=0.5)
                draw_grid(
                    canvas, spacing_unit=spacing_unit, line_width_pt=line_width_pt, 
                    size_unit=spacing_unit * 4, color=cfg.exp2.grid_color
                )
                
                arrow_width_pt = cfg.exp2.cue_line_width.value_in_points(canvas, min_points=0.5)
                arrow_len_unit = spacing_unit * 0.8
                for idx in cued_indices:
                    cx, cy = positions_unit[idx]
                    start_unit, end_unit = arrow_for_direction((cx, cy), direction, arrow_len_unit)
                    canvas.add_patch(
                        arrow_patch(start_unit, end_unit, "black", arrow_width_pt, canvas.transData)
                    )
    
    def _draw_exp3(self, canvas: Canvas, scene_cfg: Exp3SceneInputs, phase: Phase) -> None:
        """Draw Experiment 3 stimuli."""
        cfg = self.app_cfg
        rng = random.Random(scene_cfg.seed)
        
        spacing_unit = cfg.exp3.grid_spacing.value_in_unit(canvas)
        bar_len_unit = cfg.exp3.bar_length.value_in_unit(canvas)
        bar_width_pt = cfg.exp3.bar_width.value_in_points(canvas, min_points=0.5)
        line_width_pt = cfg.exp3.grid_line_width.value_in_points(canvas, min_points=0.5)
        all_coords_unit = grid_positions(4, 4, spacing_unit, center=(0.0, 0.0))
        coords_unit = sorted({x for x, _ in all_coords_unit})
        subset_type = scene_cfg.trial_data.color_orientation_type
        item_count_map = {1: 2, 2: 3, 3: 4}
        cue_count = item_count_map.get(scene_cfg.trial_data.cue_item_number, 2)
        dir_map = {1: "up", 2: "down", 3: "left", 4: "right"}
        direction = dir_map.get(scene_cfg.trial_data.manipulate_direction, "up")
        position_indices = sample_grid_window_indices(
            4,
            4,
            3,
            2,
            row_starts=[0, 1],
            col_starts=[1],
            rng=rng,
            shuffle=True,
        )
        cued_indices = rng.sample(range(len(position_indices)), k=cue_count)
        positions_unit = [all_coords_unit[idx] for idx in position_indices]
        bar_colors = cfg.display.bar_colors
        orientations = cfg.display.bar_orientations
        colors: list[str] = []
        angles: list[float] = []
        for idx in range(len(position_indices)):
            if idx in cued_indices:
                match subset_type:
                    case Exp3ColorOrientationType.SINGLE_COLOR_MULTI_ORIENTATION:
                        color = bar_colors[0]
                        angle = orientations[idx % len(orientations)]
                    case Exp3ColorOrientationType.MULTI_COLOR_SINGLE_ORIENTATION:
                        color = bar_colors[idx % len(bar_colors)]
                        angle = orientations[0]
                    case Exp3ColorOrientationType.MULTI_COLOR_MULTI_ORIENTATION:
                        color = bar_colors[idx % len(bar_colors)]
                        angle = orientations[idx % len(orientations)]
            else:
                color = rng.choice(bar_colors)
                angle = rng.choice(orientations)
            colors.append(color)
            angles.append(angle)
        probe_change = scene_cfg.trial_data.probe_change
        change_attr = scene_cfg.trial_data.change_attribute
        test_colors = list(colors)
        test_angles = list(angles)
        if probe_change == 2:
            target_idx = cued_indices[0]
            match change_attr:
                case Exp3ChangeAttribute.COLOR:
                    options = [c for c in bar_colors if c != test_colors[target_idx]]
                    test_colors[target_idx] = options[0] if options else test_colors[target_idx]
                case Exp3ChangeAttribute.ORIENTATION:
                    test_angles[target_idx] = (
                        orientations[1] if test_angles[target_idx] == orientations[0] else orientations[0]
                    )
                case Exp3ChangeAttribute.POSITION:
                    pass

        match phase:
            case Phase.MASK:
                mask_palette = list(set(colors))
                mask_patches(canvas, mask_palette, spacing_unit=spacing_unit, radius_unit=bar_len_unit * 0.5, mode="cross")
                return
            case Phase.MEMORY | Phase.TEST:
                draw_grid(
                    canvas, spacing_unit=spacing_unit, line_width_pt=line_width_pt, 
                    size_unit=spacing_unit * 4, color=cfg.exp3.grid_color
                )
                draw_positions = positions_unit
                if phase == Phase.TEST:
                    draw_positions = move_positions_direction(
                        positions_unit, cued_indices, direction, spacing_unit, coords_unit
                    )
                    if probe_change == 2 and change_attr == Exp3ChangeAttribute.POSITION:
                        target_idx = cued_indices[0]
                        draw_positions = move_positions_direction(
                            draw_positions, [target_idx], direction, spacing_unit, coords_unit
                        )
                    draw_colors = test_colors
                    draw_angles = test_angles
                else:
                    draw_colors = colors
                    draw_angles = angles
                for (cx, cy), color, ang in zip(
                    draw_positions, draw_colors, draw_angles
                ):
                    canvas.add_patch(
                        centered_line(
                            (cx, cy),
                            bar_len_unit,
                            color,
                            ang,
                            canvas.transData,
                            linewidth=bar_width_pt,
                        )
                    )
            case Phase.CUE:
                draw_grid(
                    canvas, spacing_unit=spacing_unit, line_width_pt=line_width_pt, 
                    size_unit=spacing_unit * 4, color=cfg.exp3.grid_color
                )
                cue_positions_unit = [positions_unit[idx] for idx in cued_indices]

                cue_radius_unit = cfg.exp3.cue_radius.value_in_unit(canvas)
                cue_width_pt = cfg.exp3.cue_line_width.value_in_points(canvas, min_points=0.5)
                for cx, cy in cue_positions_unit:
                    canvas.add_patch(ring_patch((cx, cy), cue_radius_unit, cue_width_pt, "black", canvas.transData))
                
                # Text label
                text_y_unit = spacing_unit * 2.4
                canvas.add_text(
                    (0, text_y_unit),
                    direction.upper(),
                    fontsize=14,
                    color="black",
                    ha="center",
                    va="bottom",
                    transform=canvas.transData,
                )
    
    def _draw_exp4(self, canvas: Canvas, scene_cfg: Exp4SceneInputs, phase: Phase) -> None:
        """Draw Experiment 4 stimuli."""
        cfg = self.app_cfg
        rng = random.Random(scene_cfg.seed)
        
        spacing_unit = cfg.exp4.grid_spacing.value_in_unit(canvas)
        bar_len_unit = cfg.exp4.bar_length.value_in_unit(canvas)

        bar_width_pt = cfg.exp4.bar_width.value_in_points(canvas, min_points=0.5)
        line_width_pt = cfg.exp4.grid_line_width.value_in_points(canvas, min_points=0.5)
        grid_size_unit = cfg.exp4.grid_size.value_in_unit(canvas)
        all_coords_unit = grid_positions(4, 4, spacing_unit, center=(0.0, 0.0))
        position_indices = sample_grid_window_indices(
            4,
            4,
            3,
            2,
            row_starts=[0, 1],
            col_starts=[1],
            rng=rng,
            shuffle=True,
        )
        positions_unit = [all_coords_unit[idx] for idx in position_indices]
        cued_indices = rng.sample(range(len(position_indices)), k=scene_cfg.trial_data.number)
        bar_colors = cfg.display.bar_colors
        orientations = cfg.display.bar_orientations
        base_colors: list[str] = ["black"] * len(position_indices)
        angles: list[float] = [rng.choice(orientations) for _ in position_indices]
        if scene_cfg.trial_data.condition in (1, 3):
            fixed_orientation = rng.choice(orientations)
            for idx in cued_indices:
                angles[idx] = fixed_orientation
        else:
            for offset, idx in enumerate(cued_indices):
                angles[idx] = orientations[offset % len(orientations)]
        if scene_cfg.trial_data.condition in (1, 2):
            dye_color = rng.choice(bar_colors)
            dye_colors = [dye_color for _ in cued_indices]
        else:
            dye_colors = [bar_colors[i % len(bar_colors)] for i in range(len(cued_indices))]
        manipulated_colors = list(base_colors)
        for idx, dye in zip(cued_indices, dye_colors):
            manipulated_colors[idx] = dye
        test_colors, test_angles = self._exp4_apply_consistency(
            manipulated_colors,
            angles,
            bar_colors,
            orientations,
            cued_indices,
            position_indices,
            scene_cfg.trial_data.consis,
            rng,
        )

        match phase:
            case Phase.MASK:
                mask_palette = list(set(manipulated_colors))
                mask_patches(canvas, mask_palette, spacing_unit=spacing_unit, radius_unit=bar_len_unit * 0.5, mode="cross")
                return
            case Phase.MEMORY | Phase.TEST:
                draw_grid(
                    canvas, spacing_unit=spacing_unit, line_width_pt=line_width_pt, 
                    size_unit=grid_size_unit, color=cfg.exp4.grid_color
                )
                draw_colors = base_colors if phase != Phase.TEST else test_colors
                draw_angles = angles if phase != Phase.TEST else test_angles
                for (cx, cy), color, ang in zip(
                    positions_unit, draw_colors, draw_angles
                ):
                    canvas.add_patch(
                        centered_line((cx, cy), bar_len_unit, color, ang, canvas.transData, linewidth=bar_width_pt)
                    )
            case Phase.CUE:
                draw_grid(
                    canvas, spacing_unit=spacing_unit, line_width_pt=line_width_pt, 
                    size_unit=grid_size_unit, color=cfg.exp4.grid_color
                )
                cue_positions_unit: list[tuple[float, float, str]] = []
                for idx in cued_indices:
                    cx, cy = positions_unit[idx]
                    cue_positions_unit.append((cx, cy, manipulated_colors[idx]))

                cue_radius_unit = cfg.exp4.cue_radius.value_in_unit(canvas)
                cue_width_pt = cfg.exp4.grid_line_width.value_in_points(canvas, min_points=0.5)
                for cx, cy, cue_color in cue_positions_unit:
                    canvas.add_patch(ring_patch((cx, cy), cue_radius_unit, cue_width_pt, cue_color, canvas.transData))

    def _exp4_apply_consistency(
        self,
        colors_in: list[str],
        angles_in: list[float],
        bar_colors: list[str],
        orientations: list[float],
        cued_indices: list[int],
        position_indices: list[int],
        consis: Exp4Consistency,
        rng: random.Random,
    ) -> tuple[list[str], list[float]]:
        colors_out = list(colors_in)
        angles_out = list(angles_in)
        match consis:
            case Exp4Consistency.CONSISTENT:
                return colors_out, angles_out
            case Exp4Consistency.CUED_COLORS_DIFFERENT:
                idx = cued_indices[0]
                options = [c for c in bar_colors if c != colors_out[idx]]
                colors_out[idx] = options[0] if options else colors_out[idx]
            case Exp4Consistency.CUED_ORIENTATIONS_DIFFERENT:
                idx = cued_indices[0]
                angles_out[idx] = orientations[1] if angles_out[idx] == orientations[0] else orientations[0]
            case Exp4Consistency.UNCUED_ORIENTATIONS_DIFFERENT:
                uncued = [i for i in range(len(position_indices)) if i not in cued_indices]
                if uncued:
                    idx = uncued[0]
                    angles_out[idx] = orientations[1] if angles_out[idx] == orientations[0] else orientations[0]
            case Exp4Consistency.UNCUED_COLORS_DIFFERENT:
                uncued = [i for i in range(len(position_indices)) if i not in cued_indices]
                if uncued:
                    idx = uncued[0]
                    colors_out[idx] = rng.choice(bar_colors)
        return colors_out, angles_out


# =============================
# Experiment 1
# =============================

def render_exp1_trial(
    trial: Exp1TrialData,
    cfg: StimuliAppConfig,
    renderer: StimuliRenderer,
    output_dir: Path,
    trial_index: int,
    seed: int,
) -> None:
    phases = cfg.render.phases
    for phase in phases:
        scene_cfg = Exp1SceneInputs(
            experiment_type=ExperimentType.E1,
            phase=phase,
            trial_data=trial,
            seed=seed,
        )
        output_path = output_dir / f"Trial_{trial_index:04d}_{phase.value}.{cfg.render.output_format}"
        renderer.render(scene_cfg, OutputConfig(file_path=str(output_path)))


# =============================
# Experiment 2
# =============================

def render_exp2_trial(
    trial: Exp2TrialData,
    cfg: StimuliAppConfig,
    renderer: StimuliRenderer,
    output_dir: Path,
    trial_index: int,
    seed: int,
) -> None:
    phases = cfg.render.phases
    for phase in phases:
        scene_cfg = Exp2SceneInputs(
            experiment_type=ExperimentType.E2,
            phase=phase,
            trial_data=trial,
            seed=seed,
        )
        output_path = output_dir / f"Trial_{trial_index:04d}_{phase.value}.{cfg.render.output_format}"
        renderer.render(scene_cfg, OutputConfig(file_path=str(output_path)))


# =============================
# Experiment 3
# =============================

def render_exp3_trial(
    trial: Exp3TrialData,
    cfg: StimuliAppConfig,
    renderer: StimuliRenderer,
    output_dir: Path,
    trial_index: int,
    seed: int,
) -> None:
    phases = cfg.render.phases
    for phase in phases:
        scene_cfg = Exp3SceneInputs(
            experiment_type=ExperimentType.E3,
            phase=phase,
            trial_data=trial,
            seed=seed,
        )
        output_path = output_dir / f"Trial_{trial_index:04d}_{phase.value}.{cfg.render.output_format}"
        renderer.render(scene_cfg, OutputConfig(file_path=str(output_path)))


# =============================
# Experiment 4
# =============================

def render_exp4_trial(
    trial: Exp4TrialData,
    cfg: StimuliAppConfig,
    renderer: StimuliRenderer,
    output_dir: Path,
    trial_index: int,
    seed: int,
) -> None:
    # Create custom renderer for exp4 with different background color
    exp4_canvas_cfg = CanvasConfig(
        bg_color=cfg.exp4.bg_color,
        screen_distance=renderer.canvas_cfg.screen_distance,
        screen_size=renderer.canvas_cfg.screen_size,
        screen_resolution=renderer.canvas_cfg.screen_resolution,
    )
    exp4_renderer = StimuliRenderer(exp4_canvas_cfg, cfg)

    phases = cfg.render.phases
    for phase in phases:
        scene_cfg = Exp4SceneInputs(
            experiment_type=ExperimentType.E4,
            phase=phase,
            trial_data=trial,
            seed=seed,
        )
        output_path = output_dir / f"Trial_{trial_index:04d}_{phase.value}.{cfg.render.output_format}"
        exp4_renderer.render(scene_cfg, OutputConfig(file_path=str(output_path)))


# =============================
# Main
# =============================

def load_config() -> StimuliAppConfig:
    import tomllib

    with CONFIG_PATH.open("rb") as f:
        data = tomllib.load(f)
    logger.info(f"Configuration loaded from {CONFIG_PATH}")
    return StimuliAppConfig(**data)


def make_trial_seed(base_seed: int, exp_id: int, subject: int, trial_index: int) -> int:
    return base_seed + exp_id * 1_000_000 + subject * 10_000 + trial_index


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reproduce stimuli for Boolean map manipulation experiments.",
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
    parser.add_argument("--exp", default="all", choices=["E1", "E2", "E3", "E4", "all"], help="Experiment to render")
    parser.add_argument("--full", action="store_true", help="Ignore render limits and process all trials")
    args = parser.parse_args()

    cfg = load_config()
    renderer = StimuliRenderer(cfg.canvas, cfg)
    max_trials = None if args.full else cfg.render.max_trials
    if max_trials == 0:
        max_trials = None
    if args.full:
        logger.info("Running in FULL mode: processing all trials")
    else:
        logger.info(f"Running with limit: max_trials_per_subject={max_trials}")

    # Load trials
    logger.info(f"Loading trial data from {XLSX_PATH}")
    exp1 = load_sheet_records(XLSX_PATH, "E1", list(Exp1TrialData.model_fields.keys()))
    exp2 = load_sheet_records(XLSX_PATH, "E2", list(Exp2TrialData.model_fields.keys()))
    exp3 = load_sheet_records(XLSX_PATH, "E3", list(Exp3TrialData.model_fields.keys()))
    exp4 = load_sheet_records(XLSX_PATH, "E4", list(Exp4TrialData.model_fields.keys()))

    coerce_int_fields(exp1, ["subject", "conditions", "orientation", "consis"])
    coerce_int_fields(exp2, ["subject", "conditions", "orientation", "consis"])
    coerce_int_fields(exp3, ["subject", "color_orientation_type", "cue_item_number", "manipulate_direction", "probe_change", "change_attribute"])
    coerce_int_fields(exp4, ["subject", "number", "consis", "condition"])

    # Convert to Pydantic models for type safety
    exp1_trials = [Exp1TrialData(**record) for record in exp1]
    exp2_trials = [Exp2TrialData(**record) for record in exp2]
    exp3_trials = [Exp3TrialData(**record) for record in exp3]
    exp4_trials = [Exp4TrialData(**record) for record in exp4]

    exp_map = {
        "E1": (exp1_trials, 1, render_exp1_trial),
        "E2": (exp2_trials, 2, render_exp2_trial),
        "E3": (exp3_trials, 3, render_exp3_trial),
        "E4": (exp4_trials, 4, render_exp4_trial),
    }

    for exp_key, (trials, exp_id, render_fn) in exp_map.items():
        if args.exp not in ("all", exp_key):
            continue
        
        logger.info(f"Rendering stimuli for experiment: {exp_key}")
        trial_counts: dict[int, int] = defaultdict(int)
        
        # Filter trials if max_trials is set
        filtered_trials = []
        for trial in trials:
            trial_counts[trial.subject] += 1
            if max_trials is not None and trial_counts[trial.subject] > max_trials:
                continue
            filtered_trials.append((trial, trial.subject, trial_counts[trial.subject]))

        if exp_key == "E1":
            expected = len(Exp1Condition) * len(Exp1Consistency)
            counter = Counter((t.conditions, t.consis) for t, _, _ in filtered_trials)
        elif exp_key == "E2":
            expected = len(Exp2Condition) * len(Exp2Consistency)
            counter = Counter((t.conditions, t.consis) for t, _, _ in filtered_trials)
        elif exp_key == "E3":
            expected = len(Exp3ColorOrientationType) * len(Exp3ChangeAttribute)
            counter = Counter((t.color_orientation_type, t.change_attribute) for t, _, _ in filtered_trials)
        else:
            expected = len(Exp4Condition) * len(Exp4Consistency)
            counter = Counter((t.condition, t.consis) for t, _, _ in filtered_trials)
        logger.info(f"{exp_key} coverage: {len(counter)}/{expected} condition combos")

        for trial, subject, trial_index in tqdm(filtered_trials, desc=f"Experiment {exp_key}"):
            seed = make_trial_seed(cfg.render.seed, exp_id, subject, trial_index)
            output_dir = OUTPUT_DIR / exp_key / f"subject_{subject:02d}"
            ensure_dir(output_dir)
            render_fn(trial, cfg, renderer, output_dir, trial_index, seed)


if __name__ == "__main__":
    main()
