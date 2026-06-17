---
name: daily-learning-system
description: "用户学习时触发：管理每日学习计划、出题考核、插队学习新主题。适配 learning-progress.md 进度文件，支持优先级队列。路径通过 KNOWLEDGE_BASE 环境变量配置。"
version: 3.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [learning, quiz, progress, daily-plan, adhoc]
    related_skills: []
---

# 每日学习系统

## 概述

自适应每日学习系统，支持优先级队列。两种添加学习内容的方式：
1. **预设路线** — `learning-progress.md` 中预定义的文章列表
2. **插队学习** — 用户说"我想学X"，我去搜索/整理资料，排到最高优先级

每天早上 8:00 定时任务推送学习计划到飞书（需自行配置）。用户说"学完了" → 出题考核 → ≥80% 通过，<80% 巩固。

## 前置配置

需要设置环境变量或在 .env 中配置：

| 变量 | 说明 | 示例 |
|------|------|------|
| `KNOWLEDGE_BASE` | 知识库根目录 | `D:/opc-workdown/知识库` |
| `FEISHU_WEBHOOK` | 飞书推送 Webhook URL | `https://open.feishu.cn/open-apis/bot/v2/hook/xxx` |

如果使用定时任务推送学习计划，需在 Hermes 中创建 cron job（参考下方"定时任务"）。

如果未设置 `KNOWLEDGE_BASE`，默认取当前工作目录下的 `知识库/`。

## 进度文件

`$KNOWLEDGE_BASE/learning-progress.md`

分为两个区域：
1. **📌 插队学习** — 临时想学的主题（最高优先级）
2. **📋 学习路线** — 预设文章列表

状态标记：⬜ 未开始 → 📖 学习中 → ✅ 已完成

## 工作流程

### 0. 首次使用（无进度文件）

如果 `$KNOWLEDGE_BASE/learning-progress.md` 不存在，说明是首次使用。
此时应询问用户："你想先学什么？我可以帮你查找资料并制定学习计划。"
根据用户回答走插队学习流程创建初始内容。

### 1. 插队学习（用户说"我想学X"）
1. 搜索"X 学习指南""X 入门教程""X 核心概念"
2. 收集 3-5 个优质资源
3. 整理摘要/指南，提炼核心知识点
4. 保存到 `$KNOWLEDGE_BASE/raw/articles/adhoc/<topic>.md`
5. 插入到 `learning-progress.md` 的 📌插队学习 区最顶部
6. 下次定时任务会把它作为 #1 优先级推送

### 1. 每日计划（可选，需配置 cron job）
- 读取 learning-progress.md
- 找到第一个 ⬜ 未开始的项目（插队区优先于路线区）
- 推送到飞书 Webhook

### 2. 出题考核（用户说"学完了"）
- 出 5 道题：填空题 / 简答题 / 选择题混合
- 答对 ≥80%（4/5）→ 标记 ✅，进入下一章
- 答对 <80% → 指出薄弱点，重新出题

### 3. 进度更新
- 通过 → learning-progress.md 中 ⬜ 改为 ✅
- 未通过 → 告诉用户哪些点需要重新学习

## 定时任务配置

如需每日自动推送，在 Hermes 中创建 cron job：

```bash
hermes cron create \
  --name "每日学习计划" \
  --schedule "0 8 * * *" \
  --prompt "读取 KNOWLEDGE_BASE/learning-progress.md，找到第一个 ⬜ 项目，生成今日学习计划，推送到飞书 Webhook。" \
  --profile default \
  --toolsets file,terminal
```

## 出题风格

题目覆盖四个维度：
1. **概念理解** — "用自己的话解释 X"
2. **对比辨析** — "A 和 B 有什么区别"
3. **应用场景** — "什么时候用 X 而不是 Y"
4. **细节记忆** — 具体知识点

通过线：5 题对 4 题（80%）

## 常见坑

1. **read_file 返回带行号的内容** — 修改文件时用 `builtins.open()` 代替 `read_file()`，或者用 `patch()` 做精准替换
2. **脚本被安全系统拦截（exit 49）** — 不要用 no_agent=True 的脚本模式跑定时任务，用 LLM 驱动的 cron prompt
3. **进度文件格式** — 表格格式 `| | N. 标题 | ⬜ |`，按 `|` 分割取索引 2
4. **插队主题** — 始终插入到 📌插队学习 区的最顶部
5. **环境变量未设置** — 如果 `KNOWLEDGE_BASE` 未配置，Agent 会尝试用当前工作目录下的 `知识库/`

## 快速开始

1. 创建 `$KNOWLEDGE_BASE/learning-progress.md`（参考下方模板）
2. 配置 `FEISHU_WEBHOOK`（如需飞书推送）
3. 创建定时任务（可选）
4. 对 Hermes 说"开始学习"或指定"我想学 XXX"

### learning-progress.md 模板

```markdown
# 学习进度跟踪

## 📌 插队学习

| # | 主题 | 状态 | 加入日期 |
|:-:|------|:----:|:--------:|

## 📋 学习路线

| # | 文章 | 状态 |
|:-:|------|:----:|
| | 1. 你的第一篇文章 | ⬜ 未开始 |
```