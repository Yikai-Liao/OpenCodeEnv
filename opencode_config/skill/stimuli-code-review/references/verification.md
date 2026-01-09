# Review 检查清单

## 1) 代码规范性（必须逐项核对）

### 1.1 规范与结构
- `exp_design.md` 的 Parameter Registry 与 `stimuli_config.toml` **完全对应**。
- `config.py` 使用 `StrictModel`，字段类型与 TOML 对齐；无未建模字段。
- `SceneConfig` 仅含调度字段；视觉参数仅存在于配置模型中。
- `render_trial` 只做调度；所有单位转换与条件逻辑只在 `Renderer.draw` 内。
- **不使用位置参数**，所有函数调用使用 `xxx=yyy`。

### 1.2 依赖与 API 使用
- 视觉图形优先使用 `stimkit.collections` 工厂函数；仅在缺失时使用 matplotlib Patch。
- 禁止 thin wrapper（仅改名/改参/重排的 helper）。
- 数据加载优先 `stimkit.io` 提供的函数，且仅保留 exp_design 指定字段。

### 1.3 随机化与可复现性
- 随机化仅来自 exp_design 规定；`seed` 贯穿所有分支。
- 不存在隐式随机或未声明的随机化逻辑。

## 2) 输出图像审查（必须目视）

### 2.1 覆盖抽样策略
- 至少覆盖每个实验/组别各 1 例；若条件分支较多，补充关键边界条件。
- 若 `<workspace>/data/` 提供参考输出或源代码生成图，优先与其对比。

### 2.2 视觉一致性
- 结构与布局与参考图一致：位置、间距、对齐关系、对称性。
- 颜色、线宽、形状、大小与条件对应一致。
- 不同阶段（Phase）的差异与 exp_design 的描述一致。

### 2.3 边界与裁剪检查
- 画布边界内无越界绘制、无裁剪痕迹。
- 边缘元素不应被边框或裁剪截断。
- 若存在边界相关规则（如留白/安全边距），必须符合。

## 3) 结论输出格式
- **问题清单**：文件名、条件、期望、观察、影响。
- **建议修复点**：对应 `config.py`、`stimuli_config.toml`、`reproduce_stimuli.py` 或 exp_design 的具体位置。
