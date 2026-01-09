# exp_design.md 输出契约（章节与表格字段）

> 目标：exp_design.md 是“代码生成的形式化规范”，不是综述文章。

## 1. Evidence Index（必须放在最前面）

用表格列出所有证据条目，作为全文唯一引用入口。

| Evidence ID | Source Type | Path | Locator | What it supports |
|---|---|---|---|---|
| E-P1 | paper | paper/paper.md | #page-2-0 / Methods/... | timing, apparatus, procedure |
| E-F1 | figure | paper/_page_2_Figure_16.jpeg | Fig.1 | stimulus geometry examples |
| E-D1 | data | data/README.md | section “data structure” | column semantics |
| E-C1 | code | data/reproduce_stimuli.py | lines 120-220 | randomization/render logic |
| E-K1 | config | data/stimuli_config.toml | [search], [canvas] | param registry defaults |

- Locator 必须足够精确：页码/小节标题/图号/代码行范围/配置节名。
- exp_design.md 正文引用只能写 Evidence ID（避免到处散落路径）。

## 2. Global Conventions（全局约定）

必须包含：
- 坐标系：原点、轴方向、角度零点、旋转正方向、单位（deg/px）
- 色彩：调色板、RGB/名称映射、灰度定义
- 屏幕与视距：分辨率、刷新率（若影响时序）、视距、屏幕尺寸
- 时间：所有 phase 的时长单位与上限（例如“直到响应或 3000ms”）

每条约定都要引用 Evidence ID。

## 3. Parameter Registry（参数注册表）

用表格列出所有复现所需参数（包括会写进 toml 的、代码中 hardcode 的、以及 derived 的）。

| Param Key | Type | Unit | Value/Range | Used in | Source (Evidence ID) | Notes |
|---|---|---|---|---|---|---|

规则：
- Param Key 使用稳定、可用于代码的命名（snake_case）。
- “Value/Range” 不允许模糊词；若缺失，填 `MISSING` 并在 “Missing Items” 汇总。

## 4. Fact Ledger（事实台账）

每条事实是最小、可实现、可引用的单元。

| Fact ID | Statement (unambiguous) | Source (Evidence ID) | Status | Derivation |
|---|---|---|---|---|
| F-0001 | Search array has N=8 positions equally spaced on a circle of radius R deg. | E-P1, E-F1 | confirmed | none |
| F-0002 | Probe1 displayed until response or 3000ms; Probe2 same. ISI between probes is 180ms. | E-P1 | confirmed | none |

- Status ∈ {confirmed, inferred, missing, conflict}
- inferred 必须写 Derivation（基于哪条证据推导，推导规则是什么）

## 5. Per-Experiment Specification（每个实验）

对每个实验（Experiment 1/2/3…）按同一结构输出：

### 5.x.1 Design Summary
- 该实验与实现相关的操纵变量（within/between）
- 试次数量、block、练习、随机化单位
- 参与者响应（按键/鼠标/时间窗/正确性判定）

### 5.x.2 Trial State Machine（Mermaid 必须）
- 节点：Phase 名称 + 时长/终止条件
- 边：分支条件（例如 dist_cond、probe_cond、group）
- 输出：记录哪些数据字段

### 5.x.3 Phase-by-Phase Stimulus Spec（几何可复现）
为每个 Phase 输出：
- Stimulus primitives 列表（stimkit 可实现）
- 每个 primitive 的几何参数（位置/尺寸/角度/颜色/层级）
- 条件分支（例如 integrated vs separate；match vs mismatch）
- 与数据字段/派生变量的绑定（见 Data Mapping）

### 5.x.4 Randomization & Counterbalancing
必须具体写出：
- 随机变量：取值空间、约束、禁止组合
- 是否需要固定 seed；seed 在哪里传入
- 反平衡：跨 block/跨 participant 的规则

## 6. Data Dictionary（数据字典）

| Column/Field | Type | Range | Meaning | Experiment-specific? | Source (Evidence ID) |
|---|---|---|---|---|---|

## 7. Data ↔ Implementation Mapping（闭环映射）

用两张表：
1) Data → Derived
2) Derived → stimkit primitives/params

每行必须能被追踪回 Evidence。

## 8. Conflict Log（如有）

| Conflict ID | What disagrees | Evidence | Decision | Rationale |
|---|---|---|---|---|

## 9. Missing Items（缺失项清单）

| Missing Item | Why needed | Blocks which section | How to resolve (required evidence) |
|---|---|---|---|
