# Horizon Integration — 一人公司情报管线

> 从每日几十条信息到 2-5 条精华，自动推送到微信。

## 架构

```
Horizon (抓取+AI筛选) → Markdown 日报 → WeChat 网关 → 微信双向对话
       ↑ DeepSeek                    ↑ Hermes Gateway
```

## 关键配置 (data/config.json)

### AI 提供商：DeepSeek (国内可访问)
```json
"ai": {
    "provider": "deepseek",
    "model": "deepseek-chat",
    "api_key_env": "DEEPSEEK_API_KEY",
    "temperature": 0.3,
    "throttle_sec": 0.3,
    "analysis_concurrency": 5,
    "enrichment_concurrency": 0
}
```

### 聚焦输出：从 24 条压到 2-5 条

| 维度 | 配置 | 效果 |
|------|------|------|
| 砍无关 GitHub 源 | 禁用 vercel/ai, supabase | -26 条噪音 |
| 砍无关 RSS | 禁用 Vercel Changelog, GitHub Blog | -4 条无关 |
| HN 收紧 | 20 条 / min_score 100 | -12 条低质 |
| OSS Insight | 关键词: agent, llm, mcp, automation, rag | +精准 |
| AI 阈值 | 8.0 (原 6.5) | 只留高价值 |
| 预估 | ~25 抓取 → 3-6 入选 | 目标内 |

### Webhook 推送
```json
"webhook": {
    "enabled": true,
    "url_env": "HORIZON_WEBHOOK_URL",
    "request_body": "title=Horizon #{date} 一人公司情报简报&desp=#{summary}"
}
```
.env: `HORIZON_WEBHOOK_URL=https://sctapi.ftqq.com/{SENDKEY}.send`

### WeChat 网关 (双向实时通信)
Hermes 原生支持个人微信，通过腾讯 iLink Bot API：
```bash
hermes gateway setup   # 选 12 Weixin/WeChat → 扫码登录
hermes gateway install  # Windows Scheduled Task 开机自启
hermes gateway start    # 启动（setup 后通常自动启动）
```
账号存储：`$HERMES_HOME/weixin/accounts/<id>.json`

## 运行
```bash
# 完整命令（含 venv 隔离 + 中文编码）
PYTHONHOME= PYTHONPATH= PYTHONIOENCODING=utf-8 PYTHONUTF8=1 PYTHONUNBUFFERED=1 \
  VIRTUAL_ENV=D:/opc-workdown/horizon-venv \
  D:/opc-workdown/horizon-venv/Scripts/python.exe -m src.main --hours 24
# 工作目录: D:\opc-workdown\Horizon-main
```

## 故障排查

### 速度优化：跳过 Enrichment

Horizon 的 `enrichment` 阶段每条文章调 2 次 DeepSeek + DuckDuckGo 搜索，占 40%+ 运行时间。
如需加速，在 `src/orchestrator.py` 打补丁：

```python
# 找到这一行：
await self._enrich_important_items(important_items)

# 替换为：
if getattr(self.config.ai, "enrichment_concurrency", 1) > 0:
    await self._enrich_important_items(important_items)
else:
    self.console.print("[dim]⏩ Enrichment skipped (enrichment_concurrency=0)[/dim]\n")
```

然后在 `config.json` 设 `"enrichment_concurrency": 0` 即跳过。省 ~90s + ~35K tokens（50% 节省）。

| 症状 | 原因 | 修复 |
|------|------|------|
| 0 条抓取 | 网络不通 (中国 GFW) | 确认代理/VPN 状态 |
| AI 超时 | OpenAI API 被墙 | 切换到 DeepSeek/阿里/豆包 |
| enrichment 卡住 | concurrency=1 太慢 | 设为 3 或 0（跳过） |
| 速度慢（5min+） | enrichment 占 50% 时间 | enrichment_concurrency=0 跳过，省 90s |
| orchestrator 补丁 | enrichment_concurrency=0 需代码支持 | 见下方补丁 |
| 404 RSS | Anthropic/DeepMind URL 变了 | 禁用或更新 URL |
| venv 不存在 | 路径在 .trash 里 | 移到正确位置 |
