from pydantic import BaseModel, ConfigDict, Field
from enum import IntEnum, StrEnum
from stimkit import CanvasConfig, VisualAngle

class Phase(StrEnum):
    FIXATION = "Fixation"
    LOAD = "Load"
    MEMORY = "Memory"
    SEARCH = "Search"
    TEST = "Test"

class ShapeType(IntEnum):
    CIRCLE = 1
    SQUARE = 2
    STAR = 3
    TRIANGLE = 4
    HEXAGON = 5

class MatchCondition(IntEnum):
    COLOR = 1
    SHAPE = 2
    CONJUNCTION = 3
    NEUTRAL = 4

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class RenderConfig(StrictModel):
    max_trials: int
    phases: list[Phase]
    seed: int
    output_format: str

class DisplayConfig(StrictModel):
    colors: list[str]
    color_count: int
    shape_count: int
    fixation_size: VisualAngle = Field(description="Fixation cross size (visual degrees)")
    load_text_height: VisualAngle = Field(description="Two-digit number height (visual degrees)")

class SearchConfig(StrictModel):
    item_size: VisualAngle = Field(description="Search item size (visual degrees)")
    radius: VisualAngle = Field(description="Radius of search array circle (visual degrees)")
    line_width: VisualAngle = Field(description="Search line width (visual degrees, converted to Matplotlib points)")
    line_length: VisualAngle = Field(description="Search line length (visual degrees)")
    target_tilt: float = Field(description="Target line tilt in degrees")
    distractor_line_color: str

class Exp1Config(StrictModel):
    trial_columns: list[str]
    sheet_name: str
    memory_item_size: VisualAngle
    search_item_size: VisualAngle

class Exp4Config(StrictModel):
    trial_columns: list[str]
    sheet_name: str
    memory_item_size_large: VisualAngle
    memory_item_size_small: VisualAngle
    search_item_size: VisualAngle

class Exp5Config(StrictModel):
    trial_columns: list[str]
    sheet_name: str
    memory_item_size: VisualAngle

class Exp6Config(StrictModel):
    trial_columns: list[str]
    sheet_name: str
    memory_item_size_large: VisualAngle
    memory_item_size_small: VisualAngle
    search_item_size: VisualAngle

class ExperimentsConfig(StrictModel):
    exp1: Exp1Config
    exp4: Exp4Config
    exp5: Exp5Config
    exp6: Exp6Config

class StimuliAppConfig(StrictModel):
    canvas: CanvasConfig
    render: RenderConfig
    display: DisplayConfig
    search: SearchConfig
    experiments: ExperimentsConfig

class TrialData(StrictModel):
    Id: int
    Trial: int
    targetshape: int | None = None
    targetcolor: int | None = None
    targetsize: int | None = None
    matchcondition: int | None = None
    linecondition: int | None = None
    target_change: int | None = None
    irre_change: int | None = None
    testcolor: int | None = None
    testshape: int | None = None
    test: int | None = None
    SOA: int | None = None

class SceneConfig(StrictModel):
    phase: Phase
    trial_data: TrialData
    exp_name: str
