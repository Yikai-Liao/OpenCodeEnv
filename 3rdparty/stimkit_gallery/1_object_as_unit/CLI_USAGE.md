# 命令行参数使用说明

本文档说明 `reproduce_stimuli.py` 的命令行参数配置。

## 命令行接口

根据 `skills/stimuli-code-generation/SKILL.md` 的规范，脚本支持以下参数：

### 可选参数

- `--exp {E1,E2,E3,all}`: 指定要运行的实验（**默认值: `all`**）
  - `E1`: 仅运行实验 1 (Color-Shape binding)
  - `E2`: 仅运行实验 2 (Semicircle color binding)
  - `E3`: 仅运行实验 3 (Notched circles with gestalt closure)
  - `all`: 运行所有三个实验

- `--full`: 忽略所有限制，处理所有试次
  - 不指定此参数时，使用 `stimuli_config.toml` 中配置的 `render.max_trials` 值
  - 指定此参数时，`max_trials` 被设为 0（无限制）


## 使用示例

### 快速测试（默认，1-2分钟）

```bash
# 运行所有实验（默认行为，使用配置文件中的 max_trials 限制）
uv run python script/reproduce_stimuli.py

# 运行单个实验（使用配置文件中的 max_trials 限制）
uv run python script/reproduce_stimuli.py --exp E1

# 运行所有实验（显式指定，等同于无参数）
uv run python script/reproduce_stimuli.py --exp all
```

### 完整生成（处理所有数据）

```bash
# 运行单个实验（处理所有试次）
uv run python script/reproduce_stimuli.py --exp E1 --full

# 运行所有实验（处理所有试次）
uv run python script/reproduce_stimuli.py --exp all --full
```

## 限制策略

- **默认限制**: `stimuli_config.toml` 中的 `render.max_trials` 设为 **5**
  - 这意味着每个被试文件（.mat）最多处理 5 个 trial
  - 确保快速测试在 1-2 分钟内完成
  
- **完整运行**: 使用 `--full` 标志时
  - `max_trials` 被动态设为 0
  - 处理所有试次，无任何限制

## 覆盖度分析

当前配置使用简单的 trial 级限制：
- `max_trials = 5`: 每个被试最多处理 5 个试次
- `max_trials = 0`: 处理所有试次

这个设置能够覆盖关键条件组合（通过前 5 个 trial），同时保持快速测试时间。

## 输出目录结构

```
output/
├── Exp1/
│   ├── Integrated_group/
│   │   └── subject_name/
│   │       ├── Trial_1_1_Memory.svg
│   │       ├── Trial_1_2_Cue.svg
│   │       ├── Trial_1_3_Search.svg
│   │       ├── Trial_1_4_Probe1.svg
│   │       └── Trial_1_5_Probe2.svg
│   └── Separate_group/
│       └── ...
├── Exp2/
│   └── ...
└── Exp3/
    └── ...
```

## 验证步骤

### 5.1.1 自动检查
- 使用默认配置快速运行脚本
- 检查生成的文件数量和结构

### 5.2 人工审查
- 随机抽取 3-5 张生成的图片
- 与 `exp_design.md` 和论文原文进行双盲比对

### 5.3 代码与文档审查
- 重新审核 `exp_design.md` 是否与论文原文一致
- 检查配置文件是否遗漏字段或存在不一致
- 确认代码遵守所有规范（无延迟转换、使用 Enum、逻辑分离等）

### 5.4 清理
- 删除生成的临时文件
- 保留 `inspect_*.py` 文件
- 确保 `output/` 目录结构清晰
