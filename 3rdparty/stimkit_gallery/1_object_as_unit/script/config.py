from pydantic import BaseModel, ConfigDict, Field
from enum import IntEnum, StrEnum
from stimkit import CanvasConfig, VisualAngle

class Phase(StrEnum):
    MEMORY = "Memory"
    CUE = "Cue"
    SEARCH = "Search"
    PROBE1 = "Probe1"
    PROBE2 = "Probe2"


class GroupType(StrEnum):
    INTEGRATED = "integrated"
    SEPARATE = "separate"


class ShapeType(IntEnum):
    SQUARE = 1
    TRIANGLE = 2
    DIAMOND = 3
    HEXAGON = 4
    TRAPEZOID = 5
    CIRCLE = 6


class DistractorCondition(IntEnum):
    RELATED_FIRST = 1
    RELATED_SECOND = 2
    UNRELATED = 3
    NO_SINGLETON = 4


class TargetOrientation(IntEnum):
    LEFT = 1
    RIGHT = 2


class CueValue(IntEnum):
    FIRST = 1
    SECOND = 2


class ProbeCondition(IntEnum):
    ONLY_FIRST_SAME = 1
    ONLY_SECOND_SAME = 2
    BOTH_DIFFERENT = 3
    BOTH_SAME = 4


class StrictModel(BaseModel):
    """Base model with strict configuration (forbid extra fields)."""
    model_config = ConfigDict(extra="forbid")


# ==============================================================================
# Config Models
# ==============================================================================
class RenderConfig(StrictModel):
    max_trials: int
    phases: list[Phase]
    seed: int
    output_format: str


class DataConfig(StrictModel):
    groups: list[str]
    integrated_group: str
    separate_group: str


class CueTextConfig(StrictModel):
    exp1_color: str
    exp1_shape: str
    exp2_up: str
    exp2_down: str


class DisplayConfig(StrictModel):
    colors: list[str]
    color_count: int
    shape_count: int
    cue_font_size: int
    cue_text: CueTextConfig


class SearchConfig(StrictModel):
    item_size: VisualAngle = Field(description="Search item diameter (visual degrees)")
    radius: VisualAngle = Field(description="Radius of the search array circle (visual degrees)")
    tilt_pos: float = Field(description="Positive target line tilt in degrees")
    tilt_neg: float = Field(description="Negative target line tilt in degrees")
    marker_ratio: float = Field(description="Line marker length ratio relative to item size")
    line_width: float = Field(description="Marker line width in Matplotlib points (pt)")
    base_color: str


class Exp1Config(StrictModel):
    trial_columns: list[str]
    integrated_item_size: VisualAngle
    separate_item_size: VisualAngle
    separate_offset: VisualAngle
    separate_shape_color: str


class Exp2Config(StrictModel):
    trial_columns: list[str]
    integrated_item_size: VisualAngle
    integrated_x: VisualAngle
    integrated_y: VisualAngle
    separate_item_size: VisualAngle
    separate_left_x: VisualAngle
    separate_left_y: VisualAngle
    separate_right_x: VisualAngle
    separate_right_y: VisualAngle
    separate_left_orientation: str = Field(description="Semicircle orientation: top/bottom/left/right")
    separate_right_orientation: str = Field(description="Semicircle orientation: top/bottom/left/right")


class Exp3Config(StrictModel):
    trial_columns: list[str]
    radius: VisualAngle
    notch_side: VisualAngle
    vertical_offset: VisualAngle
    probe_item_size: VisualAngle
    integrated_top_angle: float
    integrated_bottom_angle: float


class ExperimentsConfig(StrictModel):
    exp1: Exp1Config
    exp2: Exp2Config
    exp3: Exp3Config


class StimuliAppConfig(StrictModel):
    canvas: CanvasConfig
    render: RenderConfig
    data: DataConfig
    display: DisplayConfig
    search: SearchConfig
    experiments: ExperimentsConfig


class TrialData(StrictModel):
    col1: int = Field(description="Exp1: Color Index; Exp2/3: Top/Upper Color Index")
    col2: int = Field(description="Exp1: Shape Index; Exp2/3: Bottom/Lower Color Index")
    dist_cond: DistractorCondition = Field(description="Distractor Condition: 1=Rel 1st Probe, 2=Rel 2nd Probe, 3=Unrelated, 4=No Singleton")
    target_orient: TargetOrientation = Field(description="Target Orientation: 1=Left, 2=Right")
    cue_val: CueValue = Field(description="Cue Value: 1=Col1/Top, 2=Col2/Bot")
    probe_cond: ProbeCondition = Field(description="Probe Condition: 1=1st Match, 2=2nd Match, 3=Neither, 4=Both")


class SceneConfig(StrictModel):
    group_type: GroupType
    phase: Phase
    trial_data: TrialData
