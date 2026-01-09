---
name: data-preview
description: 当需要查看/预览各种数据尤其是非纯文本数据时使用此技能。例如：txt,xlsx,docx,pptx,pdf,mat,zip,rar。
---


## 纯文本数据查看

请直接调用内置工具读取文本文件，注意请不要一次性全部读取占用上下文，请限制行数，例如先只读前20行。

## 非纯文本数据查看

#### xlsx,docx,pptx,pdf

系统已经安装了`markitdown`命令行工具，用于预览xlsx,docx,pptx,pdf等数据，请务必将结果添加md后缀保存，方便以后再次阅读。
例如：
```bash
markitdown data.xlsx -o data.xlsx.md
```
转换后，使用文件读取工具查看`data.xlsx.md`。

## 压缩包

**禁止**使用markitdown直接处理zip等压缩文件，这回导致缓慢的处理速度。任何压缩包**请解**压缩后处理。

## mat

系统已经安装了`mat_preview`命令行工具，用于预览mat文件（该工具及其生成结果仅用于可复现性检验阶段），生成的结果是有截断的。
例如：
```bash
mat_preview ./data.mat --max-entries 10 --sample-k 20 -o ./data.mat.preview.json
``
