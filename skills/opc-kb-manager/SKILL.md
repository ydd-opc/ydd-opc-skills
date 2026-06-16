---
name: opc-kb-manager
description: "Manage the opc-workdown solopreneur knowledge base — ingest raw sources into wiki pages, query existing knowledge, lint for health issues, and maintain navigation."
version: 1.4.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [wiki, knowledge-base, solopreneur, chinese, markdown]
    category: research
    related_skills: [wechat-link-digest]
---

# OPC Knowledge Base Manager

Manage 袁兜兜's "一人公司" (Solopreneur) knowledge base at `D:\opc-workdown\`.

This is a CLAUDE.md-driven variant of Karpathy's llm-wiki pattern. The root
`CLAUDE.md` serves as the project meta-document (schema, conventions, stats,
and TODOs) instead of `wiki/SCHEMA.md`.

## Project Structure

```
D:\opc-workdown\
├── CLAUDE.md              ← Project meta: domain, conventions, stats, TODOs
├── wiki/                  ← Agent-maintained wiki pages
│   ├── index.md           ← Content catalog with [[wikilinks]]
│   ├── concepts/          ← 六大板块 (ai应用/, 商业基础/, 等)
│   ├── entities/          ← People, orgs, products, models
│   ├── horizon/           ← Horizon daily digests (YYYY-MM-DD/)
│   └── summaries/         ← Query results and reports
├── raw/                   ← Immutable source materials
├── reading-list.md        ← Priority-ordered reading plan
├── log/                   ← Chronological action logs
├── outputs/               ← Generated images + reports
├── audit/                 ← Lint reports + link archives
│   ├── links/             ← Pending links (wechat-link-digest)
│   ├── resolved/          ← Completed links
│   └── failed/            ← Failed extractions
```

## Domain & Priority — Updated 2026-06-14

**Domain:** 一人公司 (Solopreneur) — building an independent AI business.
**Priority direction:** AI技能教程 — 面向所有人, 程序员能用, 普通人也能用.
**Primary topics:** AI skills for everyone (Prompt Engineering, AI automation, AI content creation), AI news weekly, solopreneur tools.
**What we DON'T do:** Pure technical tutorials (Python APIs, model deployment), narrow audience content (Java-only), content requiring code to follow.

### Content Positioning (Customer-Facing)

```
不是「程序员教你怎么用AI」
而是「一个每天都在用AI干活的人, 教你怎么也让AI帮你干活」
```

- **No "8 years Java backend" or "Java developer" framing in public-facing content** — user explicitly rejected this 3 times. It narrows the audience.
- **"Knowledge base building" is a metaphor, not the actual topic.** The real angle is AI skills tutorials — how to use AI to solve everyday problems.
- **Target audience is BOTH programmers AND non-programmers.** Every tutorial must pass: "Can someone who can't code follow this?"
- **Cold-start score must be ≥ 7** for priority topics.

### Learning Path — Java 后端转 AI 应用开发（五层递进 — Internal reference only）

Old raw articles (19 generic summaries from June 1) were archived to `raw/archive/2026-06-01/`. The current `raw/articles/` contains 15 in-depth articles organized as a 5-level learning path for Java developers transitioning to AI application development:

## Horizon Daily Pipeline (CRITICAL)

A daily cron job (`Horizon每日流水线`, job_id varies) runs at 9:00 CST:

```
Step 1: Run Horizon → save to AI-Daily-Reports/raw/YYYY-MM-DD.md
Step 2: Digest top 4-7 articles into wiki/horizon/YYYY-MM-DD/
Step 3: Push integrated articles to WeChat (new 📰 format)
Step 4: Generate cover image via siliconflow_gen.py → WeChat
```

If Horizon returns 0 items: skip Steps 2-4, push a failure notification.

### Step 1 — Run Horizon (exact command)

```bash
# MUST set PYTHONHOME= and PYTHONPATH= to prevent hermes-agent's venv from
# contaminating horizon-venv's pydantic/pydantic_core. Without this, you get:
#   ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'
# PYTHONIOENCODING + PYTHONUTF8 ensure proper Chinese character handling in output.
PYTHONHOME= PYTHONPATH= PYTHONIOENCODING=utf-8 PYTHONUTF8=1 PYTHONUNBUFFERED=1 \
  VIRTUAL_ENV=D:/opc-workdown/horizon-venv \
  D:/opc-workdown/horizon-venv/Scripts/python.exe -m src.main --hours 24
```

Working directory: `D:\opc-workdown\Horizon-main`

After Horizon completes, copy the latest summary from `data\summaries\horizon-YYYY-MM-DD-zh.md`
to `D:\opc-workdown\AI-Daily-Reports\raw\YYYY-MM-DD.md`. Use the ZH (Chinese) summary, not EN.

**If Horizon returns 0 items**: skip Steps 2-4, push a failure notification.
**If the pydantic error still appears**: the PYTHONHOME/PYTHONPATH env vars may already be set
elsewhere (e.g., in system env or shell profile). Use `env -u PYTHONHOME -u PYTHONPATH`
on MSYS2 or explicitly unset them first.

### Step 2 — Digest Rules

- **首次运行** 先确保目录存在：`mkdir -p D:/opc-workdown/wiki/horizon`
- **Wiki path:** `wiki/horizon/YYYY-MM-DD/` — one subdirectory per day, one file per article
- **Frontmatter:** mark `sources: [horizon]` and add `source_url:` pointing to the original article
- **Content:** 300-500 word interpretation from 技术红利 (tech dividend) perspective — what this means for developers/solopreneurs, not just a summary
- **Cross-references:** link to ≥2 other wiki pages (same-day articles + existing concept pages)
- Focus on AI/tech articles; skip purely financial/non-tech stories
- Horizon produces 4-7 articles per day at threshold 8.0; work with whatever it returns

### Step 3 — WeChat Format

Push format: see `references/wechat-push-format.md` for the complete template with a real example.

Key rules: 📰 今日AI看点 format, 3-7 articles/day, no scores/links/hashtags, Chinese only, AI/tech only.

### Step 4 — Cover Image

Generate a daily cover image via SiliconFlow. See `references/cover-image-generation.md` for the exact command, prompt guidelines, and delivery instructions.

## Weekly Digest (Monday Only)

On Mondays, after completing Steps 1-4 above, execute the weekly special:

### Step 5 — Collect Last Week's Data

Read the last 7 days of raw summaries from `AI-Daily-Reports/raw/YYYY-MM-DD.md`
(Mon-Sun of the previous week). Select the top 6 most important articles by
score and AI/tech relevance. Generate a weekly-style digest article saved to
`wiki/summaries/`.

### Step 6 — Generate Images

Generate 2 images via SiliconFlow:
- **Cover image** (`--ratio cover_wechat`, 1024x512)
- **Body image** (`--ratio landscape_16_9`, 1024x576)

Both saved to `outputs/`.

### Step 7 — Push to Feishu

Push the weekly digest to the user's Feishu bot webhook using an interactive card
(`msg_type: interactive`). See `references/feishu-push.md` for the exact format,
image upload flow, and troubleshooting.

**Critical:** Feishu bot webhooks do NOT support `msg_type: post` — they return
`{"code": 10208, "msg": "'post' field required"}`. Always use `interactive` (card).

### Horizon Optimization

The user's Horizon is configured for speed:
- `enrichment_concurrency: 0` — enrichment SKIPPED (saves ~90s and ~35K tokens)
- `analysis_concurrency: 5` — parallel AI scoring
- AI provider: `deepseek` / `deepseek-v4-pro`
- AI threshold: 8.0 (targets 5-15 articles/day)
- The orchestrator was patched to skip enrichment when concurrency=0:
  ```python
  if getattr(self.config.ai, "enrichment_concurrency", 1) > 0:
      await self._enrich_important_items(important_items)
  ```

### Horizon Config Reference

Path: `D:\opc-workdown\Horizon-main\data\config.json`
- Sources trimmed: 5 RSS + 7 GitHub (removed vercel/ai, supabase, Vercel Changelog, GitHub Blog)
- Hacker News: top 20 stories, min score 100
- OSS Insight keywords: agent, llm, mcp, automation, rag, developer tools
- Server酱 webhook: DISABLED (replaced by WeChat gateway)
- .env: DEEPSEEK_API_KEY set, HORIZON_WEBHOOK_URL removed

## WeChat Gateway

Hermes gateway connected to user's personal WeChat via Tencent iLink Bot API:
- Gateway runs as Windows Scheduled Task: `Hermes_Gateway`
- Account stored at: `D:\\soft\\hermes\\weixin\\accounts\\`
- User set WeChat as home channel (`/sethome`)
- Cron jobs with `deliver: all` route to WeChat automatically
- CLI commands: `hermes gateway status|start|stop|restart`

## Multi-Profile Collaboration

User has 6 Hermes profiles for different roles:

| Profile | Role | How it works |
|---------|------|-------------|
| `default` | 总指挥 | User interacts directly via WeChat/CLI |
| `kb-manager` | 情报员 | Cron job 417c4a327f52 runs daily 9:00 |
| `researcher` | 研究员 | Link digestion, deep research, wiki creation |
| `writer` | 编辑 | Article polishing, headline selection, formatting |
| `designer` | 设计师 | Cover images (siliconflow_gen.py), layout, visual design |
| `strategist` | 策略师 | Topic planning, publish calendar, headline optimization |

Collaboration flows:

**创业故事线 (周更):**
```
你 → strategist(选题) → researcher(调研) → writer(初稿) → designer(排版封面) → 发布
```

**每日推文线 (日更·自动化):**
```
kb-manager(9:00 Horizon) → writer(格式化) → designer(封面) → 微信推送
```

## Orientation (do every session)

Before any operation, orient yourself:

```
① Read CLAUDE.md — domain, conventions, current stats, open TODOs
② Read wiki/index.md — what wiki pages exist today
③ Check reading-list.md — what's been read vs pending
```

## Operation 1: Digest (ingest)

Trigger: "消化这篇文章" / "digest"

Flow:
```
Read raw source → Extract entities & concepts → 
Check existing wiki pages → Create/update wiki pages → 
Update wiki/index.md → Append to log/ → Update CLAUDE.md stats
```

Rules:
- **Create a wiki page** when an entity/concept appears in 2+ sources OR is central to one source
- **Update existing page** when material augments what's already covered
- **Don't create** for passing mentions or content outside the domain
- **Every page** gets YAML frontmatter: `title`, `created`, `updated`, `type`, `tags`, `sources`
- **Tags** from CLAUDE.md's six 板块: `ai应用`, `商业基础`, `自媒体学习`, `ai商业化`, `产品与增长`, `效率与自动化`
- **Every page** must link to ≥2 other wiki pages via `[[wikilinks]]`
- **Provenance:** append `^[raw/articles/source-file.md]` when synthesizing claims from a specific source

### Frontmatter Template

```yaml
---
title: 页面标题
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: concept | entity | comparison | summary | horizon
tags: [from CLAUDE.md taxonomy]
sources: [raw/articles/source-name.md]
source: horizon | wechat-link | manual
---
```

### Wiki Page Types

- **concept/** — Definition, current knowledge, open questions, related concepts
- **entity/** — What it is, key facts, relationships, source references
- **comparison/** — Side-by-side analysis (when applicable)
- **summary/** — Filed answers to substantive queries
- **horizon/** — 每日 Horizon 自动生成的资讯解读（来源: `source: horizon`）

Pages should be scannable in 30 seconds. Split when >200 lines.

## Operation 2: Digest Next

Trigger: "消化下一篇" / "digest next"

```
① Read reading-list.md → find first unchecked [ ] item
② Execute Digest on that article
③ Mark it [x] in reading-list.md
④ Update CLAUDE.md stats
```

## Operation 3: Query

Trigger: "查一下XXX" / "query XXX"

```
① Read wiki/index.md → identify relevant pages by section
② search_files for key terms across wiki/ for any missed pages
③ Read the relevant pages → synthesize answer citing [[wikilinks]]
④ If the answer is substantial (comparison, deep dive, novel synthesis):
   - Create a page in wiki/concepts/ or wiki/comparisons/
   - Add to wiki/index.md
   - Append to log/
⑤ Otherwise just return the answer
```

## Operation 4: Lint

Trigger: "检查知识库健康" / "lint"

Scan for:

① **Orphan pages** — wiki pages with zero inbound [[wikilinks]]
② **Broken wikilinks** — [[links]] pointing to non-existent pages
③ **Index completeness** — every wiki page appears in index.md
④ **Stale content** — pages not updated in >90 days when related raw sources exist
⑤ **Page size** — pages >200 lines (candidates for splitting)
⑥ **Tag audit** — tags not in CLAUDE.md taxonomy
⑦ **Frontmatter** — missing required fields
⑧ **Empty stubs** — wiki pages with ≤5 bytes of content (zero-byte or frontmatter-only files that were created as placeholders but never filled). Flag for either filling or removing.

Output a report to `audit/YYYYMMDD-HHMMSS-lint.md` with specific file paths and suggested actions.
Log all finds: `## [YYYY-MM-DD] lint | N issues found`

## Operation 5: Status

Trigger: "知识库状态" / "status"

```
① Count wiki pages by type → update CLAUDE.md "已有 wiki 页面"
② Count raw articles → update CLAUDE.md "已有原始素材"
③ Count reading-list progress (checked vs total)
④ Report: pages, sources, reading progress, last activity
```

## Operation 7: Topic Selection (选题策略)

Trigger: "帮我选选题" / "下一个选题写什么" / "选题"

The `strategy/` directory at `D:\\opc-workdown\\strategy\\` is the strategist's workspace.
It contains three files maintained by this agent:

| File | Purpose |
|------|---------|
| `选题管线.md` | Priority queue: P0(下期可写) → P1(本周待排) → P2(先放着) → 已发布 |
| `选题策略.md` | Methodology: content mix, cold-start checklist, headline formula |
| `内容矩阵.md` | Four-quadrant: 实用价值 vs 人设加成 |

### Rules

- **P0 items are the default recommendation** — always check P0 first
- **Override P0 → go to P1** only when: user explicitly rejected it, cold-start score is too low, or a timely event makes a P1 item more urgent
- **After publishing**: move item to ✅ 已发布 with date
- **New idea surface**: add to the pipeline immediately (classify P0/P1/P2)

### Automated Push (topic_picker_v2.py)

`strategy/topic_picker_v2.py` reads 选题管线.md and pushes an interactive card to Feishu.
Set up as cron job: `0 9 * * 1` (weekly Monday), profile: librarian.

```python
cd D:\\opc-workdown && python strategy/topic_picker_v2.py
```

The script parses P0/P1/P2/已发布 sections, applies the priority rule (P0 first), checks for 3+ consecutive news articles, and sends an interactive card via FEISHU_WEBHOOK.

### Feishu Bitable Plugin (多维表格插件)

A Vue 3 + Element Plus table view extension exists at `C:\\Users\\yuanjiafeng\\my-app\\table-view\\`.
Uses `@lark-opdev/block-bitable-api` SDK for reading/writing bitable data.
Features: kanban view by status field, weekly plan generation, Feishu webhook notification.
Dev: `npm run start` (opens bitable with debugPort=8081).
Build: `npm run build`. Upload: `npm run upload` (needs opdev login first).

Trigger: "批量消化" / "batch digest"

When processing multiple sources:
1. Read all raw sources first
2. Extract ALL entities/concepts across all sources in one pass
3. Check existing wiki pages for ALL of them (one search_files call)
4. Create/update pages in one batch
5. Update index.md once at the end
6. Write a single log entry covering the batch

## Conventions

- **Filenames:** Chinese native names (e.g., `AIAgent开发架构.md`, not `ai-agent-kai-fa.md`)
- **wikilinks:** Use `[[path/relative/to/wiki/页面名]]` format
- **Tags:** Only use tags from CLAUDE.md's six 板块
- **CLAUDE.md sync:** Update stats immediately when counts change
- **Log format:** `## [YYYY-MM-DD] action | subject` — append-only
- **Reading list:** `[ ]` unchecked, `[x]` completed, each entry is a wikilink

## Wake Timer (Sleep → Auto-Wake)

To ensure the 9:00 AM cron job runs even when the computer is sleeping:

- A Windows scheduled task `Hermes_WakeUp` runs daily at 8:55 AM with `WakeToRun=True`
- This wakes the computer from S3 sleep, Gateway resumes, cron fires at 9:00
- Verify: `powershell -NoProfile -File D:\soft\hermes\scripts\check-wake.ps1`
- Setup: `powershell -NoProfile -File D:\soft\hermes\scripts\enable-wake.ps1` (needs admin)

**Huawei MateBook lid close:** Huawei PC Manager (MateBookService/MSPCManagerService) overrides Windows power settings. Setting lid close to "Do nothing" via `powercfg` does NOT work on Huawei laptops. Keep lid open for uninterrupted service, or configure lid behavior in Huawei PC Manager.

## Digesting External Links

**Delegated to `wechat-link-digest` skill.** When a link is shared via WeChat, the
wechat-link-digest skill handles the full pipeline: extraction → classification →
wiki page creation → index update → audit archival. Do NOT duplicate extraction
logic here — load the wechat-link-digest skill when processing shared links.

Quick reference for Douyin: `extract_douyin_full.py` handles metadata extraction.
Video transcripts are NOT available from Douyin's public API. See
`references/douyin-extraction.md` for details.

## Pitfalls

- **CRITICAL: User corrected content positioning 3 times — embed this early.** Do NOT lead with "8年Java" or "Java后端" in public-facing content. The positioning is: "一个每天都在用AI干活的人, 教你怎么也让AI帮你干活." The 8 years Java backend experience is personal context, not a content hook.
- **"知识库搭建" is a metaphor, not a literal topic.** When the user says "教人搭知识库," they mean teaching AI skills that everyone can use. Do not create tutorials about how to set up folder structures or markdown files.
- **User categorization corrections are high-priority** — if the user re-frames content (e.g., "these are Skills, not standalone tools"), rewrite the wiki page immediately, delete the old file, and update index.md. Don't leave both versions.
- **Never modify raw/ files** — sources are immutable
- **Always orient first** — read CLAUDE.md + index.md before any operation
- **Don't create isolated pages** — every page needs ≥2 cross-references
- **Frontmatter is required** on every wiki page
- **Keep pages scannable** — split at 200 lines
- **Update CLAUDE.md stats immediately** — stale stats degrade trust
- **内容真实性优先** — 只能基于实际提取到的内容写入 wiki。视频转录不可用时应标注「🎬 视频内容待观看后补充」，不要脑补或合成内容。用户有权看到哪些是原始信息、哪些是待补充的。
- **The 12 deferred articles are intentionally skipped** — don't digest them unless user explicitly asks
- **Horizon PYTHONHOME/PYTHONPATH contamination**
- **Cron job DeepSeek model name** — cron jobs using DeepSeek provider must explicitly pass `model: deepseek-v4-pro`. The default model name is not recognized by DeepSeek and will fail with `'The supported API model names are deepseek-v4-pro or deepseek-v4-flash, but you passed .'`. Always set `model` when creating DeepSeek cron jobs.
- **Cron job prompt is static — must update manually after skill changes.** Updating SKILL.md does NOT auto-update the cron job that loads it. The cron job stores a snapshot of the prompt at creation time. After any pipeline change (new steps, format changes, new tools), run `cronjob(action='update', job_id='...', prompt='<new full prompt>')`. Failing to do this means the cron job silently runs the OLD workflow. This is the #1 reason today's push didn't match expectations.
- **Profile .env isolation** — cron jobs run under a specific profile (e.g., kb-manager). API keys added to `~/.hermes/.env` (default profile) are NOT visible to profile-scoped cron jobs. Always copy new keys to the profile's own `.env` file: `~/.hermes/profiles/<name>/.env`. This session's case: SILICONFLOW_API_KEY was in default but missing from kb-manager, so Step 4 image generation silently failed.
- **WeChat iLink rate limiting** — rapid cron triggers (manual re-runs within minutes) can hit iLink `rate limited` errors. Normal daily schedule (once at 9:00) won't trigger this. If re-running for verification, wait at least 30 minutes between runs.
- **Feishu webhook post not supported** — bot webhooks (`/bot/v2/hook/...`) reject `msg_type: post` with code 10208. Use `msg_type: interactive` (card) instead.

## Verification

After any digest operation, verify:
- [ ] New/updated pages appear in wiki/index.md
- [ ] Log entry exists in log/YYYYMMDD.md
- [ ] CLAUDE.md stats match reality (page count, source count)
- [ ] Reading list checkbox updated if using digest-next

## References

- `references/horizon-integration.md` — Horizon daily pipeline, config tuning for 2-5 articles/day, China-accessible AI providers
- `references/reading-list-template.md` — Format for focused reading lists with [[wikilinks]] and `[ ]` checkboxes
- `references/wechat-push-format.md` — 微信推送格式: `日期 - 今日AI速报: [大标题]` → 📋速览 → 文章(🔥💬📖💡) → ━━━━━━
- `references/cover-image-generation.md` — Step 4 封面配图: SiliconFlow 命令、prompt 指南、发送格式
- `references/reading-list-template.md` — 精选阅读清单格式
- `references/video-creation-pipeline.md` — 视频内容创作流水线：口播稿→HyperFrames动效视频→MP4渲染
- `references/voxcpm-tts.md` — VoxCPM2 语音合成：安装、内存/GPU要求、ModelScope国内源、音色描述优化
- `references/coze-api.md` — 扣子Coze API调用方式：bot_id获取、pat token管理、stream_run接口格式
- `references/hyperframes-video.md` — HyperFrames 视频制作：Kinetic Type模板、音频路径避坑、Windows Node.js 22 + FFmpeg 配置
- `references/content-writing-workflow.md` — 写作流程方案: 两条内容线、周更节奏、多角色配合
- `references/douyin-extraction.md` — 抖音链接提取：什么能用、什么不行 + 完整命令
- `references/feishu-push.md` — 飞书推送：interactive card 格式、图片上传流程、webhook 避坑指南
