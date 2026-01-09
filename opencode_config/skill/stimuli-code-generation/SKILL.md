---
name: stimuli-code-generation
description: 生成心理学/认知科学论文原始刺激的代码实现。此技能用于将 exp_design.md、数据/参考代码与 stimkit 渲染约定一一落地到 reproduce_stimuli.py、config.py、stimuli_config.toml，确保架构、单位、CLI、随机化都满足可复现要求。
---

# 原始刺激复现：代码生成规范（以 exp_design.md 为主要实现规格）

## 最高原则
- 目标是生成**清晰、鲁棒、可直接运行**且**不易出错**的原始刺激复现代码。
- **exp_design.md 是主要实现规格**：代码生成优先依赖其结构化事实与参数；若信息不足或冲突，**必须调用 `stimuli-exp-design` 技能补全/修正**，不得直接从论文/图/猜测推断实现细节。
- 若 exp_design.md 仍有缺失项：将对应实现标记为 `MISSING` 并显式阻断相关推导；不要臆造数值。
- **若 `<workspace>/data/` 提供源代码/参考实现**：它是实现逻辑与超参数的**最高优先级来源**；需先在 exp_design 中明确记录并引用，然后再生成代码。

## 输入与输出（必须对齐）

### 输入（按优先级）
1) `<workspace>/exp_design.md`（必须）  
2) `<workspace>/data/`（数据字典/参考实现/配置，作为 Evidence 佐证）  
3) `<workspace>/paper/` 仅通过 `stimuli-exp-design` 技能间接使用；本技能不直接引用

### 输出文件（最小集）
- `script/config.py`：Enum + Pydantic 模型（严格类型、无默认值）
- `script/stimuli_config.toml`：参数注册表的**唯一落地**
- `script/reproduce_stimuli.py`：数据加载 + 渲染调度 + Renderer 实现

## 工作流（按顺序执行）

1) **读取 exp_design.md，建立实现映射**
   - Parameter Registry → `stimuli_config.toml` 与 `config.py` 字段
   - Global Conventions → CanvasConfig、坐标与颜色约定
   - Data Dictionary + Mapping → `TrialData` 字段与数据加载规则
   - Per-Experiment Specification → Phase 枚举、render 逻辑、primitive 组合规则
   - 若信息不足或冲突：停止实现，转去运行 `stimuli-exp-design` 技能补全

2) **实现严格模型（config.py）**
   - 所有配置类继承 `StrictModel`（`extra="forbid"`）
   - **所有视觉参数必须是 `VisualAngle`/`Pixel`**；禁止 raw `float`
   - **禁止默认值**；必须在 `stimuli_config.toml` 显式赋值
   - Enum 使用 `StrEnum`/`IntEnum`，禁止 magic number/string
   - `SceneConfig` 仅含 `trial_data + phase + seed + experiment_type` 等最小调度字段

3) **生成 `stimuli_config.toml`（参数注册表落地）**
   - TOML 结构与 Pydantic 模型**一一对应**
   - `[canvas]`、`[render]` 等必选 section 全字段齐全
   - 参数注释写清楚来源与单位；缺失项显式标注 `MISSING`

4) **实现数据加载（reproduce_stimuli.py）**
   - 只保留 exp_design 指定字段（读取阶段裁剪或读取后筛选；优先使用 `stimkit.io`）
   - 清洗：列名去空白、去空行、`NaN -> None`
   - 立即转换为 Pydantic 模型进行验证

5) **实现 Renderer 架构**
   - `render_trial` 只负责调度：构建 SceneInputs + 调用 `renderer.render(...)`
   - `Renderer.draw` 内部完成：单位转换 → 随机化/条件逻辑 → 绘制
   - 使用 `match/case` 处理 Enum 分支
   - 创建的自定义 patch 工厂函数仅返回 Patch，不直接调用 `canvas.add_patch`

6) **随机化与复现性**
   - 随机化规则必须来自 exp_design.md（变量空间、约束、采样单位）
   - `seed` 必须从渲染配置传入并贯穿所有随机分支
   - 不得引入未在 exp_design.md 中声明的随机逻辑

7) **CLI 与 limit 设计（必须纳入代码生成）**
   - CLI 仅支持 `--exp` 与 `--full`（不新增其它参数）
   - `--full` 必须忽略所有 limit
   - 若启用分层 limit：在 `RenderConfig` 中显式建模（strict）
   - 细则见 `references/cli-limits.md`

8) **最小自检**
   - 每个 Phase 在代码中都有对应分支
   - 每个数据字段都参与了明确的渲染或判断逻辑
   - 任何缺失项都显式阻断实现，不得默认为常见值

9) **交付前必须触发 Review**
   - 代码生成完成后，必须调用 `stimuli-reproduction-review` 技能进行审核
   - Review 未通过不得进入扩展或优化阶段

## 强制规则（必须遵守）
- 只在 `Renderer.draw` 内做单位转换；**禁止延迟转换**
- SceneConfig 禁止包含 `float` 或 `VisualAngle`/`Pixel`
- 禁止 `extra="allow"`；禁止 thin wrapper
- 仅使用 `renderer.render(scene_cfg=..., output_cfg=...)` 生成输出
- **优先使用 `stimkit.collections` 的工厂函数**（如 `circle`/`square`/`triangle`/`centered_line` 等）；仅在 stimkit 未覆盖时才直接使用 matplotlib 原生 Patch

## 必读参考（按需加载）
- 架构与职责边界：`references/architecture.md`
- 单位规则与转换时机：`references/unit-rules.md`
- 反模式清单：`references/anti-patterns.md`
- 数据加载规范：`references/data-loading.md`
- TOML 配置规范：`references/config-toml.md`
- CLI 与 limit 设计：`references/cli-limits.md`

## 代码结构建议（保持简洁）
```
script/
  config.py              # Enum + Pydantic 模型（Strict）
  stimuli_config.toml    # 参数注册表
  reproduce_stimuli.py   # 数据加载 + render 调度 + Renderer
```

## 与 exp_design 的耦合边界
- **只能**使用 exp_design 的 Data Mapping 来决定 TrialData 字段与派生变量
- **只能**使用 exp_design 的 Phase/流程图来决定 `Phase` 枚举与渲染分支
- **只能**使用 Parameter Registry 来决定 TOML 字段与单位
