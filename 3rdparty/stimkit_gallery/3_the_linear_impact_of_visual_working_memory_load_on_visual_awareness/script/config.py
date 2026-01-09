from pydantic import BaseModel, ConfigDict, Field
from enum import IntEnum, StrEnum
from stimkit import CanvasConfig, Pixel, VisualAngle

class Phase(StrEnum):
    MEMORY = "Memory"
    MIB = "MIB"
    PROBE = "Probe"

class ConditionExp1(IntEnum):
    LOAD_1_SAME = 1
    LOAD_1_DIFF = 2
    LOAD_2_SAME = 3
    LOAD_2_DIFF = 4
    LOAD_3_SAME = 5
    LOAD_3_DIFF = 6
    LOAD_0_A = 7
    LOAD_0_B = 8

class ConditionExp2(IntEnum):
    LOAD_1_SAME = 1
    LOAD_1_DIFF = 2
    LOAD_3_SAME = 3
    LOAD_3_DIFF = 4

class ConditionExp3(IntEnum):
    LOAD_1 = 1
    LOAD_2 = 2
    LOAD_3 = 3

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

class RenderConfig(StrictModel):
    max_trials: int
    max_files_per_exp: int
    phases: list[Phase]
    seed: int
    output_format: str

class DataConfig(StrictModel):
    exp1_path: str
    exp2_path: str
    exp3_path: str

class DisplayConfig(StrictModel):
    fixation_size: VisualAngle
    fixation_color: str
    fixation_stroke: Pixel
    fixation_cross_width: VisualAngle = Field(description="Fixation cross stroke width (visual degrees)")

class MemoryConfig(StrictModel):
    item_size: VisualAngle
    diamond_eccentricity: VisualAngle
    shape_color: str

class MIBConfig(StrictModel):
    mask_size: VisualAngle
    grid_rows: int
    grid_cols: int
    cross_color: list[int]
    cross_size: VisualAngle = Field(0.8, description="Cross arm length (visual degrees)")
    cross_width: VisualAngle = Field(0.15, description="Cross stroke width (visual degrees)")
    rotation_speed: float
    target_size: VisualAngle
    target_color: str
    target_eccentricity: VisualAngle
    target_quadrant: str

class StimuliAppConfig(StrictModel):
    canvas: CanvasConfig
    render: RenderConfig
    data: DataConfig
    display: DisplayConfig
    memory: MemoryConfig
    mib: MIBConfig

class TrialData(StrictModel):
    trial_idx: int = Field(alias="Trial")
    condition: int = Field(alias="Condition")
    rt1: float = Field(alias="RT1")
    rt2: float = Field(alias="RT2")
    rt3: float = Field(alias="RT3")
    acc: int = Field(alias="Acc")
    key_resp: int = Field(alias="KeyResponse")

class SceneConfig(StrictModel):
    experiment: str
    phase: Phase
    trial_data: TrialData
    load: int
    match: bool | None # None for Exp3 or Load 0
    shapes: list[int] # Indices of shapes used
    probe_shape: int | None # Index of probe shape

    # Units
    fixation_size_unit: float
    fixation_stroke_unit: float
    fixation_stroke_points: float
    item_size_unit: float
    diamond_positions_unit: list[tuple[float, float]]
    mask_size_unit: float
    cross_size_unit: float
    cross_width_unit: float
    target_size_unit: float
    target_eccentricity_unit: float
    target_pos_unit: tuple[float, float]
