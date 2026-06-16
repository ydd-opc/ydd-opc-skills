# Reading List Template

> Focused reading plan bridging raw/ sources to wiki/ pages.

## Format

```markdown
# 阅读清单 — {知识库名称}

> 目标：{一句话目标}
> 从 {总数} 篇中精选 {N} 篇必读，其余暂缓。
> 建议顺序阅读。

## 🔴 必读：{优先级标签}（{N} 篇）

| # | 文章 | 为什么重要 | 状态 |
|---|------|-----------|------|
| 1 | [[raw/articles/{分类}/{文件名}.md]] | {一句话关联理由} | [ ] |
| 2 | ... | ... | [ ] |

## ⏸️ 暂缓阅读（{N} 篇）

这些当前不紧急，等核心 N 篇消化完再按需补充：

| 板块 | 暂缓文章 |
|------|---------|
| {板块名} | {文件名} |
```

## Pruning Rules

When reducing a large reading list to focus items:

1. **Filter by priority direction** — only keep articles that directly support the current research focus
2. **Cut adjacent-but-not-core** — e.g., for "AI 技术派", cut 自媒体/税务/财务/Linux kernel
3. **Cut foundational-but-familiar** — skip intro material the user already knows
4. **Max 5 core articles** — more than 5 means the focus is too broad; pick the top 5
5. **Move the rest to "暂缓"** — they're not deleted, just deferred

## Reading Rhythm

- 1-2 articles per day max
- 输出驱动输入：每读完一篇 → digest → wiki 概念页
- `digest-next` 操作自动取下一篇并标记 [x]

## [[wikilink]] Format

Use `[[path/relative/to/project/root]]` format:
```
[[raw/articles/ai应用/AIAgent开发架构.md]]
```

This works in Obsidian Graph View and `search_files` across the vault.
