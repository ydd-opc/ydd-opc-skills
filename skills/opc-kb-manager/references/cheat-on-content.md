# Cheat on Content — AI 内容评分与复盘系统

## 概述

开源项目（https://github.com/XBuilderLAB/cheat-on-content），一个 Claude Code Skill，3.8K Star。把每次内容发布变成可校准的实验。

## 核心循环

```
📊 发布前评分 → 🎯 盲预测 → 🚀 发布 → 📈 T+3天复盘 → 🧬 进化评分标准
```

## 15 个子 Skill

| Skill | 功能 | Hermes 可复刻 |
|-------|------|:-------------:|
| cheat-score | 发布前评分（6 维） | ✅ content-scorer skill |
| cheat-score-blind | 不看数据先猜 | ✅ 手动 |
| cheat-predict | 预测数据区间 | ✅ 手动 |
| cheat-retro | T+3 复盘对账 | ✅ 手动 |
| cheat-status | 状态看板 | ⚠️ 部分 |
| cheat-seed | AI 聊选题 | ⚠️ 部分 |
| cheat-trends | 抓今日热点 | ❌ 网络受限 |
| cheat-persona | 受众画像（从评论反推） | ❌ 需数据源 |
| cheat-learn-from | 拆解对标账号 | ❌ 需数据源 |
| cheat-recommend | 推荐选题 | ❌ 依赖前序 |
| cheat-bump | 自动升级评分公式 | ❌ 依赖复盘数据 |
| cheat-publish/shoot | 登记发布 | ❌ 纯元数据管理 |

## Hermes 替代方案

已封装为 `content-scorer` skill，装在 strategist 角色上。覆盖评分→预测→复盘核心流程。

## 参考

- GitHub: https://github.com/XBuilderLAB/cheat-on-content
- 中文 README: https://github.com/XBuilderLAB/cheat-on-content/blob/main/docs/README_CN.md