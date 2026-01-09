# 单位与布局规则（stimkit 对齐）

## 关键结论
- `config.py` 中的几何/尺寸/线宽等字段必须是 `VisualAngle`/`Pixel`
- `stimuli_config.toml` 解析后即变成单位对象
- **只有 `Renderer.draw` 可以转换为 mpl 数值**
- `stimkit.layouts` 仅接受 **mpl 数值空间**，必须先转换

## 单位转换规则
- `VisualAngle.value_in_unit(canvas=...)` → mpl data units
- `VisualAngle.value_in_points(canvas=..., min_points=...)` → pt（线宽/字体）
- `Pixel.value_in_unit(canvas=...)` → mpl data units
- `Pixel.value_in_points(canvas=..., min_points=...)` → pt

## 命名约定
- data units 使用 `_unit` 后缀（如 `radius_unit`）
- points 使用 `_pt` 后缀（如 `line_width_pt`）

## 正例（推荐）
说明：先在 `draw` 内转换，再做布局与绘制。
```python
def draw(self, canvas: Canvas, scene_cfg: Exp1SceneInputs) -> None:
    cfg = self.app_cfg.search
    radius_unit = cfg.radius.value_in_unit(canvas=canvas)
    item_size_unit = cfg.item_size.value_in_unit(canvas=canvas)
    line_width_pt = cfg.line_width.value_in_points(canvas=canvas, min_points=0.5)
    positions = circular_positions(count=8, radius=radius_unit)
    for cx, cy in positions:
        canvas.add_patch(patch=circle(xy=(cx, cy), radius=item_size_unit / 2, color="black", transform=canvas.transData))
```

## 反例（禁止）
```python
# ❌ 非渲染层转换
radius = cfg.search.radius.value_in_unit(canvas=canvas)

# ❌ 单位对象参与运算/布局
diameter = cfg.search.item_size * 2
positions = circular_positions(count=8, radius=cfg.search.radius)
```
