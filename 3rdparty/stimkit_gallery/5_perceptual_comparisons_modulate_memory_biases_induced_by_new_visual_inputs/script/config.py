from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from enum import StrEnum
from stimkit import CanvasConfig, Pixel

class Phase(StrEnum):
    MEMORY = "Memory"
    PROBE = "Probe"
    WHEEL1 = "Wheel1"
    PROMPT = "Prompt"
    WHEEL2 = "Wheel2"


class TaskType(StrEnum):
    COMPARE = "compare"
    IGNORE = "ignore"
    REMEMBER = "remember"


class StimulusType(StrEnum):
    COLOR = "color"
    SHAPE = "shape"


class ExperimentName(StrEnum):
    EXP1A = "Exp1A"
    EXP1B = "Exp1B"
    EXP2A = "Exp2A"
    EXP2B = "Exp2B"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RenderConfig(StrictModel):
    max_trials: int | None = None
    max_files_per_exp: int | None = None
    limits: "RenderLimits | None" = None
    phases: list[Phase]
    seed: int
    output_format: str


class ColorSpaceConfig(StrictModel):
    count: int = Field(360, description="Number of discrete samples around the color wheel")
    l_star: float = Field(description="CIELAB L* (lightness) for the color wheel center")
    a_center: float = Field(description="CIELAB a* center coordinate (green-red axis)")
    b_center: float = Field(description="CIELAB b* center coordinate (blue-yellow axis)")
    radius: float = Field(description="CIELAB radius for the circular color space")
    item_diameter_px: Pixel
    wheel_diameter_px: Pixel
    wheel_ring_width_px: Pixel


class ShapeSpaceConfig(StrictModel):
    count: int = Field(360, description="Number of discrete shapes in the shape wheel")
    item_size_px: Pixel = Field(description="Shape stimulus size (pixels, rendered to canvas units)")
    wheel_diameter_px: Pixel = Field(description="Shape wheel diameter (pixels)")
    wheel_item_size_px: Pixel = Field(description="Shape wheel exemplar size (pixels)")
    exemplar_count: int = Field(description="Number of exemplars rendered on the wheel")
    fill_color: str = Field(description="Fill color for shape patches")
    stroke_color: str = Field(description="Stroke color for shape outlines")
    stroke_width: float = Field(description="Stroke width in points")
    fill_enabled: bool = Field(description="Whether to render filled shapes")


class PromptConfig(StrictModel):
    font_size: int = Field(description="Prompt font size in points")
    color: str = Field(description="Prompt text color")


class MultiprocessingConfig(StrictModel):
    processes: int | None = None
    enabled: bool = True


class RenderLimits(StrictModel):
    max_files_per_exp: int | None = None
    max_trials_per_file: int | None = None
    by_task: dict[str, int] | None = None


class StimuliAppConfig(StrictModel):
    canvas: CanvasConfig
    render: RenderConfig
    color_space: ColorSpaceConfig
    shape_space: ShapeSpaceConfig
    prompt: PromptConfig
    multiprocessing: MultiprocessingConfig = MultiprocessingConfig()


class TrialData(StrictModel):
    block: int
    trial: int
    memory_index: int
    probe_index: int | None
    test: int
    direction: int
    similarity_response: int | None = None


class SceneConfig(StrictModel):
    phase: Phase
    stimulus_type: StimulusType
    task_type: TaskType
    trial: TrialData
    wheel_rotation: int
    experiment: ExperimentName
