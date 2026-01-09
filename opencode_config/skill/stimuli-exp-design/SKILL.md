---
name: stimuli-exp-design
description: 从心理学/认知科学论文原文、论文中的刺激插图(<workspace>/paper/...)、实验数据与参考代码(<workspace>/data/...)中，抽取复现实验所需的全部实现信息，生成严格可追溯、可核验引用的 exp_design.md；输出必须以 stimkit 为唯一刺激实现框架来表述参数、坐标、形状与渲染逻辑，并包含 Evidence Index、Fact Ledger、trial 流程、条件枚举、随机化/反平衡规则、数据字段↔实现参数映射。
---

# 心理学论文 exp_design.md 生成（stimkit 绑定、可核验引用）

## Overview

**最高纲领**：阅读工作区中的论文原文与论文中图像刺激的插图(<workspace>/paper/...)，以及提供的实验数据与可能的代码(<workspace>/data/...)，提取所有与复现实现有关信息形式化的，无歧义的，有原文引用的设计文档`exp_design.md`。

以下所有原则皆派生自该最高纲领：当规则冲突或缺失时，优先保证“形式化 + 无歧义 + 可核验引用”。

**特别强调**：若 `<workspace>/data/` 中提供源代码/参考实现，则其对**实现逻辑与超参数**具有**最高优先级**（高于论文文字描述）；必须显式引用并在冲突时以代码为准。

## 输出契约（必须满足）

严格按模板输出 `<workspace>/exp_design.md`，章节、表格与字段含义遵循：
- `references/output_contract.md`

## 工作流程（按顺序执行）

1) 建立 Evidence Index
- 扫描 `<workspace>/paper/`（正文 + 刺激插图）与 `<workspace>/data/`（数据说明 + 参考实现/配置）
- 为每个可引用片段分配 Evidence ID，并记录定位方式（文件路径、页码/标题、代码行区间、图号）
- 写入 `exp_design.md` 的 “Evidence Index” 章节（模板见 output_contract）

2) 抽取事实并入账（Fact Ledger）
- 将所有“会影响复现代码”的信息拆成最小事实单元（参数/规则/枚举/流程/判定条件）
- 每条事实必须：唯一表述 + Evidence 引用 + 置信度/来源类型（paper/figure/data/code/derived）
- 事实台账格式见 `references/output_contract.md` 与 `references/evidence_and_conflicts.md`

3) 处理冲突与缺失（禁止拍脑袋补数）
- 当 paper、figure、data、code 的表述不一致：
  - 建立 Conflict Log（见 `references/evidence_and_conflicts.md`）
  - 给出“采用哪个来源作为实现真值”的明确决策，并引用支撑证据  
  - **若 `<workspace>/data/` 中提供了源代码/参考实现：对实现逻辑与超参数，必须以源代码为最高优先级**
- 当关键参数缺失：
  - 记录为 “缺失项（Missing）”，列出需要哪类证据才能补齐
  - 禁止虚构数值、禁止用“通常/一般/大概”替代

4) 写 Per-Experiment Specification
- 对每个实验分别输出：
  - 研究问题与操纵变量（只写与实现相关的那部分）
  - Trial 状态机 / Mermaid 流程图（带时长、输入、输出、分支条件）
  - 每个 Phase 的刺激几何定义（可在脑中复现，不依赖看图）
  - 随机化/反平衡/试次数量/Block 结构
- 如果不同组（如 integrated vs separate）刺激结构不同：明确分叉并分别定义

5) 数据字段 ↔ 实现参数闭环
- 构建 Data Dictionary：每列类型、取值范围、语义
- 构建 Mapping：数据字段 → 派生变量 → stimkit 参数/primitive
- 若参考代码存在：以“可核验引用”的方式记录其实现细节，并**以其作为实现真值优先级最高的来源**
- 细则见 `references/data_mapping.md`

## stimkit 绑定（强制）

- 所有几何/颜色/渲染必须能直接落到 stimkit 的坐标与 primitive 表述
- 坐标系、角度零点、旋转正方向等约定：以 stimkit 源码/文档为实现真值；若找不到，写入缺失项并阻断相关推导
- 细则见 `references/stimkit_binding.md`

## 最小自检（写完后必须过一遍）

- 每个数值参数都出现在 Fact Ledger 或 Parameter Registry，且至少有 1 个 Evidence 引用
- 每条流程分支（条件→呈现→响应→记录）都能在 Mermaid 图中找到对应节点
- 每个 trial-level 随机变量都有：取值空间、约束、随机化单位（trial/block/subject）、是否需要固定 seed
- 每个数据字段都在 Data Dictionary 出现；每个被代码使用的字段都能映射到具体视觉参数或判定逻辑
- `exp_design.md` 中不得出现“等等/类似/大概/通常”这类不可核验表述
