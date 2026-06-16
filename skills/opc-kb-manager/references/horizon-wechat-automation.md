# Horizon → WeChat 自动化推送设置实录

> 2026-06-04 踩坑记录，供后续维护参考。

## 最终配置

### config.json 精简

```json
{
  "ai": {
    "provider": "deepseek",
    "model": "deepseek-chat",
    "api_key_env": "DEEPSEEK_API_KEY",
    "throttle_sec": 0.3,
    "analysis_concurrency": 5,
    "enrichment_concurrency": 0
  },
  "sources": {
    "github": [
      {"owner":"openai","repo":"codex"},        // keep
      {"owner":"browser-use","repo":"browser-use"}, // keep
      {"owner":"modelcontextprotocol","repo":"servers"}, // keep
      {"owner":"cline","repo":"cline"},          // keep
      {"owner":"continuedev","repo":"continue"}, // keep
      {"owner":"simonw","type":"user_events"},   // keep
      {"owner":"karpathy","type":"user_events"}  // keep
      // vercel/ai, supabase — REMOVED (noise)
    ],
    "hackernews": {"fetch_top_stories": 20, "min_score": 100},
    "rss": [
      "OpenAI News",          // keep
      "Google DeepMind Blog", // keep (URL fixed)
      "Simon Willison",       // keep
      "Latent Space",         // keep
      "Product Hunt"          // keep
      // Anthropic — DISABLED (404)
      // Vercel Changelog, GitHub Blog — REMOVED
    ],
    "ossinsight": {"keywords": ["agent","llm","mcp","automation","rag","developer tools"]}
  },
  "filtering": {"ai_score_threshold": 8.0},
  "webhook": {"enabled": false}
}
```

### 优化效果对比

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 抓取量 | ~64条 | ~30-40条 |
| 精选量 | ~24条 | 5-15条 |
| Token | 68K-114K | ~33K |
| 耗时 | ~5-6分钟 | ~2-3分钟 |
| Enrichment | 运行 (30次API) | 跳过 (0次) |

## 核心优化：跳过 Enrichment

Horizon 的 Enrichment（内容丰富）对每天每条精选文章做：
1. DeepSeek 提取概念 → 1次 API 调用
2. DuckDuckGo 搜索每个概念 → N次网络请求
3. DeepSeek 生成背景 → 1次 API 调用

15 篇文章 = ~30 次 API 调用，耗时 ~90 秒。

**Patch: orchestrator.py** — 当 `enrichment_concurrency=0` 时跳过：

```python
# 6. Search related stories + enrich with background knowledge (2nd AI pass)
# Skip enrichment when concurrency is set to 0 (speed optimization)
if getattr(self.config.ai, "enrichment_concurrency", 1) > 0:
    await self._enrich_important_items(important_items)
else:
    self.console.print("[dim]⏩ Enrichment skipped (enrichment_concurrency=0)[/dim]\n")
```

## Cron Job 踩坑

### DeepSeek 模型名不匹配

Cron job 使用 DeepSeek provider 时，如果不显式指定 model，会失败：

```
Error: The supported API model names are deepseek-v4-pro or deepseek-v4-flash, 
but you passed .
```

**修复：** 创建 cron job 时必须传 `model: {"model":"deepseek-v4-pro"}`。

### 推送格式偏好（已迁移至 v3）

推送格式已升级为 v3，详见 `references/wechat-push-format.md`。

**旧版已废弃的格式**（以下仅为历史记录）：
```
⭐9.0 标题 → 📝 摘要 → 📖 正文 → 🔗 链接 → #标签
```
每条用 `---` 分隔。

**当前 v3 格式要点**：
- 五选一标题类型（一句话总结/数字冲击/趋势判断/痛点型/悬念型）
- 📋 速览 → ━━━━━━ → 🔥💬📖💡 四段式文章结构
- 删除评分、链接、标签
- 每篇 300-500 字深度解读，从技术红利角度展开

## 微信网关

- 协议: Tencent iLink Bot API (ilinkai.weixin.qq.com)
- 登录: 扫码 QR code
- 服务: Windows Scheduled Task `Hermes_Gateway`
- 账号: `D:\soft\hermes\weixin\accounts\<id>.json`
- 主频道: 用户在微信中 `/sethome`

## 知识管家 Profile（当前使用：librarian）

最初创建了 `kb-manager` profile，后续统一合并到 `librarian` profile 下管理所有知识库操作。

```bash
# 当前 profile（实际使用）
hermes profile use librarian

# 原始 profile（历史，可删除）
hermes profile delete kb-manager
```

SOUL.md 已定制为 "知识总管" 人格，专注知识库和推送。定时任务挂在 librarian profile 下，每天 9:00 CST。

## 数据流

```
Horizon (D:\opc-workdown\Horizon-main)
  │ python -m src.main --hours 24
  ▼
data/summaries/horizon-YYYY-MM-DD-zh.md
  │ copy
  ▼
AI-Daily-Reports/raw/YYYY-MM-DD.md
  │ opc-kb-manager digest
  ▼
wiki/concepts/ + wiki/entities/  (合并同主题，分散异主题)
  │ cron job delivery
  ▼
微信 (via Hermes Gateway)
```
