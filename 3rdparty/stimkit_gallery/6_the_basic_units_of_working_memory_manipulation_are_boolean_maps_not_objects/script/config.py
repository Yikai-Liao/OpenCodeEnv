from pydantic import BaseModel, ConfigDict, Field
from enum import StrEnum, IntEnum
from stimkit import CanvasConfig, VisualAngle

class Phase(StrEnum):
    MEMORY = "Memory"
    CUE = "Cue"
    MASK = "Mask"
    TEST = "Test"


class ExperimentType(StrEnum):
    E1 = "E1"
    E2 = "E2"
    E3 = "E3"
    E4 = "E4"


class Exp1Condition(IntEnum):
    """Experiment 1 conditions: binding units"""
    ONE_BINDING_ONE_OBJECT = 1  # 1B1O
    ONE_BINDING_TWO_OBJECTS = 2  # 1B2O
    TWO_BINDINGS_ONE_OBJECT = 3  # 2B1O
    TWO_BINDINGS_TWO_OBJECTS = 4  # 2B2O


class Exp2Condition(IntEnum):
    """Experiment 2 conditions: same as Exp1"""
    ONE_BINDING_ONE_OBJECT = 1  # 1B1O
    ONE_BINDING_TWO_OBJECTS = 2  # 1B2O
    TWO_BINDINGS_ONE_OBJECT = 3  # 2B1O
    TWO_BINDINGS_TWO_OBJECTS = 4  # 2B2O


class Exp1Consistency(IntEnum):
    """Experiment 1/2 consistency types"""
    CONSISTENT = 0
    CUED_CHANGED = 1
    UNCUED_CHANGED = 2


class Exp2Consistency(IntEnum):
    """Experiment 2 consistency types"""
    CONSISTENT = 0
    CUED_CHANGED = 1
    UNCUED_CHANGED = 2
    SOLID_UNCUED_CHANGED = 3
    POSITION_CHANGED = 4


class Exp3ColorOrientationType(IntEnum):
    """Experiment 3 subset types"""
    SINGLE_COLOR_MULTI_ORIENTATION = 1  # SCMO
    MULTI_COLOR_SINGLE_ORIENTATION = 2  # MCSO
    MULTI_COLOR_MULTI_ORIENTATION = 3  # MCMO


class Exp3Direction(IntEnum):
    """Movement direction"""
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Exp3ChangeAttribute(IntEnum):
    """Change attribute for probe"""
    COLOR = 1
    ORIENTATION = 2
    POSITION = 3


class Exp4Condition(IntEnum):
    """Experiment 4 conditions"""
    SINGLE_COLOR_SINGLE_ORIENTATION = 1  # SCSO
    SINGLE_COLOR_MULTI_ORIENTATION = 2  # SCMO
    MULTI_COLOR_SINGLE_ORIENTATION = 3  # MCSO
    MULTI_COLOR_MULTI_ORIENTATION = 4  # MCMO


class Exp4Consistency(IntEnum):
    """Experiment 4 consistency types"""
    CONSISTENT = 0
    CUED_COLORS_DIFFERENT = 1
    CUED_ORIENTATIONS_DIFFERENT = 2
    UNCUED_ORIENTATIONS_DIFFERENT = 3
    UNCUED_COLORS_DIFFERENT = 4


class StrictModel(BaseModel):
    """Base model with strict configuration (forbid extra fields)."""
    model_config = ConfigDict(extra="forbid")


class Exp1TrialData(StrictModel):
    """Trial data for Experiment 1"""
    subject: int
    conditions: Exp1Condition
    orientation: int  # 0=horizontal, 1=vertical
    consis: Exp1Consistency


class Exp2TrialData(StrictModel):
    """Trial data for Experiment 2"""
    subject: int
    conditions: Exp2Condition
    orientation: int  # 0=horizontal, 1=vertical
    consis: Exp2Consistency


class Exp3TrialData(StrictModel):
    """Trial data for Experiment 3"""
    subject: int
    color_orientation_type: Exp3ColorOrientationType
    cue_item_number: int
    manipulate_direction: Exp3Direction
    probe_change: int  # 1=no change, 2=change
    change_attribute: Exp3ChangeAttribute


class Exp4TrialData(StrictModel):
    """Trial data for Experiment 4"""
    subject: int
    number: int
    condition: Exp4Condition
    consis: Exp4Consistency


class RenderConfig(StrictModel):
    seed: int
    output_format: str
    max_trials: int
    phases: list[Phase]


class DisplayConfig(StrictModel):
    palette: list[str]
    bar_colors: list[str]
    bar_orientations: list[float]


class Exp1Config(StrictModel):
    dumbbell_radius: VisualAngle = Field(description="Dumbbell end radius")
    connector_length: VisualAngle = Field(description="Dumbbell connector length")
    connector_width: VisualAngle = Field(description="Dumbbell connector width")
    object_radius: VisualAngle = Field(description="Object radius")
    cue_radius: VisualAngle = Field(description="Cue ring radius")
    cue_line_width: VisualAngle = Field(description="Cue ring line width")
    mask_spacing: VisualAngle = Field(description="Mask grid spacing")
    mask_radius: VisualAngle = Field(description="Mask element radius")


class Exp2Config(StrictModel):
    circle_radius: VisualAngle = Field(description="Circle radius")
    grid_spacing: VisualAngle = Field(description="Grid spacing")
    cue_radius: VisualAngle = Field(description="Cue ring radius")
    cue_line_width: VisualAngle = Field(description="Cue ring line width")
    grid_line_width: VisualAngle = Field(description="Grid line width")
    grid_color: str


class Exp3Config(StrictModel):
    bar_length: VisualAngle = Field(description="Bar length")
    bar_width: VisualAngle = Field(description="Bar width")
    grid_spacing: VisualAngle = Field(description="Grid spacing")
    cue_radius: VisualAngle = Field(description="Cue ring radius")
    cue_line_width: VisualAngle = Field(description="Cue ring line width")
    grid_line_width: VisualAngle = Field(description="Grid line width")
    grid_color: str


class Exp4Config(StrictModel):
    bar_length: VisualAngle = Field(description="Bar length")
    bar_width: VisualAngle = Field(description="Bar width")
    grid_spacing: VisualAngle = Field(description="Grid spacing")
    grid_line_width: VisualAngle = Field(description="Grid line width")
    grid_size: VisualAngle = Field(description="Grid size")
    cue_radius: VisualAngle = Field(description="Cue ring radius")
    bg_color: str
    grid_color: str


class SceneConfig(StrictModel):
    """Base configuration for a scene to render."""
    experiment_type: ExperimentType
    phase: Phase
    seed: int


class Exp1SceneInputs(SceneConfig):
    """Per-render inputs for Experiment 1 (trial/phase specific)."""
    trial_data: Exp1TrialData


class Exp2SceneInputs(SceneConfig):
    """Per-render inputs for Experiment 2 (trial/phase specific)."""
    trial_data: Exp2TrialData


class Exp3SceneInputs(SceneConfig):
    """Per-render inputs for Experiment 3 (trial/phase specific)."""
    trial_data: Exp3TrialData


class Exp4SceneInputs(SceneConfig):
    """Per-render inputs for Experiment 4 (trial/phase specific)."""
    trial_data: Exp4TrialData


class StimuliAppConfig(StrictModel):
    canvas: CanvasConfig
    render: RenderConfig
    display: DisplayConfig
    exp1: Exp1Config
    exp2: Exp2Config
    exp3: Exp3Config
    exp4: Exp4Config
