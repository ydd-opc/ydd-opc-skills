# ydd-opc-skills

> 袁兜兜的 Hermes Agent 自定义 Skills  
> 一人公司（Solopreneur）知识库工具链 — AI 赋能个人独立盈利

---

## 📦 Skills

| Skill | 说明 |
|-------|------|
| [opc-kb-manager](./skills/opc-kb-manager/) | OPC 知识库管理器 — 素材入库 → wiki 消化 → 索引维护 → 健康检查，完整的一人公司知识管理流水线 |
| [wechat-link-digest](./skills/wechat-link-digest/) | 微信链接消化 — 从微信接收链接 → 保存 → AI 解析 → 自动生成 wiki 页 → 回复摘要，微信端知识自动入库 |

---

## 🧩 什么是 Hermes Agent Skill？

[Hermes Agent](https://hermes-agent.nousresearch.com) 是一个 AI Agent 框架，Skill 是其可插拔的能力模块。每个 Skill 包含：

- **SKILL.md** — 核心指令，定义 Agent 如何执行特定任务
- **references/** — 背景知识、参考文档
- **scripts/** — 可执行的辅助脚本

安装方式：将 skill 放入 `~/.hermes/skills/<category>/<skill-name>/` 目录即可。

---

## 📄 License

MIT — 随意使用，欢迎 fork 和 PR。
