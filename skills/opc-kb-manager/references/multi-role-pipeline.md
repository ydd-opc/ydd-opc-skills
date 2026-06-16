# 多角色内容生产线

## 角色体系

| 角色 | Profile | SOUL.md | 专属目录 |
|------|---------|:---:|------|
| PM | project-manager | ✅ | —（只协调不产出文件）|
| 研究员 | researcher | ✅ 五项职责 | research/YYYY-MM-DD/ |
| 编辑 | writer | ✅ 六项职责 | drafts/YYYY-MM-DD/ |
| 设计师 | designer | ✅ 三项职责 | outputs/ |
| 策略师 | strategist | ✅ 四项职责 | strategy/ |
| 知识总管 | librarian | ✅ 五项职责 | 全库维护 |

## 协作流程

```
你 → PM（拆任务）
         │
    ┌────┴────┐
    ▼         ▼
researcher  strategist    ← 可并发
    │
    ▼
  writer
    │
    ▼
 designer
    │
    ▼
   PM 汇总 → 你
```

## 边界规则

- researcher 不写初稿，writer 不做调研
- designer 不改内容，writer 不做封面
- PM 不执行，只协调
- librarian 管库不管写

## SOUL.md 模板

创建新角色时，在 `D:\soft\hermes\profiles\<name>\SOUL.md` 中定义：
1. 你能做什么（3-5条核心职责）
2. 你不能做什么（明确的"不可越界"列表）
3. 输出格式（文件路径+命名规范）
4. 收尾标准（最后一句写什么）

## CLAUDE.md Agent 分工

在项目根 `CLAUDE.md` 第0节定义 Agent 分工，使 Hermes/Claude Code/Codex 各司其职。关键：
- 每个 Agent 分配专属目录，互不写入
- Hermes: wiki/ content/ research/ strategy/ audit/
- Claude Code: code-reviews/
- Codex: products/
