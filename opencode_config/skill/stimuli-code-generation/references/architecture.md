# 渲染架构与职责边界（对齐 gallery/1 与 gallery/6）

## 目标
- 明确 `render_trial` 与 `Renderer.draw` 的职责边界
- 确保结构稳定、可读、可扩展
- 只在渲染层执行逻辑与绘制（参见 gallery/1、gallery/6）

## 架构总览（调度 vs 渲染）
```
render_expX_trial (调度层)
  ├─ 构建 SceneInputs(trial_data=..., seed=..., phase=...)
  └─ 调用 renderer.render(scene_cfg=..., output_cfg=...)
       └─ ExpXRenderer.draw (渲染层)
            ├─ 读取 config 中的 VisualAngle/Pixel
            ├─ 转换为 mpl 数值（参见 unit-rules）
            ├─ 执行条件/随机/布局逻辑
            └─ 绘制 patch/text
```

## 职责划分
- `render_trial`：
  - 只负责**调度与 I/O**
  - 构建 `SceneInputs` 并调用 `renderer.render(...)`
  - **不做**条件判断、随机化、布局、单位转换、绘制
- `Renderer.draw`：
  - 只在此处做单位转换、布局与绘制
  - `match/case` 处理 Enum 分支（避免 magic number/string）

## Helper（Patch Factory）规则
- 允许封装**重复的组合/布局/条件逻辑**，以降低 `draw` 内复杂度
- **禁止 thin wrapper**：仅改名/改参顺序/转发调用的 helper 不允许
- helper 返回 `patches.Patch` 或 patch 列表，不直接调用 `canvas.add_patch`
- **优先使用 `stimkit.collections`**；仅当 stimkit 未提供 primitive 时才使用 matplotlib 原生 Patch

## 正例（参考 gallery/1 的组合逻辑）
说明：helper 封装了**位置+条件分支+多 patch 组合**，不是 thin wrapper。
```python
def search_array_patches(
    *,
    radius_unit: float,
    item_size_unit: float,
    colors: list[str],
    target_index: int,
    target_tilt: float,
    marker_ratio: float,
    line_width_pt: float,
    transform: transforms.Transform,
) -> list[patches.Patch]:
    patches_out: list[patches.Patch] = []
    positions = circular_positions(count=8, radius=radius_unit)
    marker_size = item_size_unit * marker_ratio
    item_radius = item_size_unit / 2
    index = 0
    for cx, cy in positions:
        patches_out = patches_out + [circle(xy=(cx, cy), radius=item_radius, color=colors[index], transform=transform)]
        if index == target_index:
            patches_out = patches_out + [
                centered_line(
                    xy=(cx, cy),
                    length=marker_size,
                    color="black",
                    angle=target_tilt,
                    transform=transform,
                    linewidth=line_width_pt,
                )
            ]
        else:
            patches_out = patches_out + [
                *cross_line(
                    xy=(cx, cy),
                    length=marker_size,
                    color="black",
                    angle=45,
                    transform=transform,
                    linewidth=line_width_pt,
                )
            ]
        index = index + 1
    return patches_out

class Exp1Renderer(Renderer):
    def __init__(self, canvas_cfg: CanvasConfig, app_cfg: StimuliAppConfig):
        super().__init__(canvas_cfg)
        self.app_cfg = app_cfg

    def draw(self, canvas: Canvas, scene_cfg: Exp1SceneInputs) -> None:
        cfg = self.app_cfg.search
        radius_unit = cfg.radius.value_in_unit(canvas=canvas)
        item_size_unit = cfg.item_size.value_in_unit(canvas=canvas)
        line_width_pt = cfg.line_width.value_in_points(canvas=canvas, min_points=0.5)
        patches_out = search_array_patches(
            radius_unit=radius_unit,
            item_size_unit=item_size_unit,
            colors=self.app_cfg.display.colors,
            target_index=scene_cfg.trial_data.target_index,
            target_tilt=cfg.tilt_pos,
            marker_ratio=cfg.marker_ratio,
            line_width_pt=line_width_pt,
            transform=canvas.transData,
        )
        canvas.add_patches(patches=patches_out)
```

## 反例（禁止）
说明：调度层做单位转换/绘制，破坏层次结构（与 gallery/1/6 相违背）。
```python
def render_exp1_trial(...):
    radius = cfg.exp1.cue_radius.value_in_unit(canvas=canvas)
    canvas.add_patch(patch=patches.Circle(xy=(0, 0), radius=radius))
```

## Renderer 调用规则
- 必须使用 `renderer.render(scene_cfg=..., output_cfg=...)`
- 禁止手动创建 `Canvas` 并调用 `save`

## 日志与进度管理（tqdm 兼容）
```python
from loguru import logger
from tqdm import tqdm

logger.remove()
logger.add(
    lambda msg: tqdm.write(s=msg, end=""),
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
)
```
