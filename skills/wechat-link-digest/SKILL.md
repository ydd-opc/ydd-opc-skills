---
name: wechat-link-digest
description: "微信链接消化：从微信接收链接→保存→解析→生成wiki→更新索引→回复摘要"
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [wechat, link, wiki, digest, knowledge-base]
    category: research
    related_skills: [opc-kb-manager]
    auto_load: true
---

# 微信链接消化 (WeChat Link Digest)

当用户在微信中分享一个链接给 Hermes 时，自动完成：保存 → 解析 → wiki 入库 → 索引更新 → 微信回复。

## 触发条件

收到微信消息，内容包含 http:// 或 https:// 链接。

## 完整工作流

```
① 提取链接 → ② 保存原始链接到 audit/links/ 
→ ③ 抓取网页内容 → ④ 解析提取正文
→ ⑤ 分类到六大板块 → ⑥ 生成 wiki 页面
→ ⑦ 更新 wiki/index.md → ⑧ 更新 CLAUDE.md 统计
→ ⑨ 微信回复摘要卡片
```

## 目录结构

```
D:\opc-workdown\
├── audit/links/              ← 待处理链接（处理前暂存）
├── audit/resolved/           ← 已完成链接（wiki 生成后移入）
├── wiki/concepts/<板块>/     ← 消化后的 wiki 页面
├── wiki/index.md             ← 导航索引
└── CLAUDE.md                 ← 项目统计
```

## 操作步骤

### ① 提取链接

从微信消息中提取所有 URL：
```python
import re
urls = re.findall(r'https?://[^\s]+', message_text)
```

如果消息中没有链接，不触发此流程。

### ② 保存到 audit/links/

为每个链接创建存档文件 `audit/links/YYYY-MM-DD-<slug>.md`：

```markdown
---
url: https://example.com/article
title: (待解析后填入)
domain: example.com
saved: YYYY-MM-DD HH:MM
status: fetched | failed
category: (解析后填入)
---

## 原始信息
- URL: https://example.com/article
- 分享时间: YYYY-MM-DD HH:MM
- 来源: 微信

## 解析结果
(解析后填入)
```

### ③ 抓取网页内容

**重要：禁用 `python -c` 行内执行**，Hermes 会将其拦截为危险命令导致 WeChat 端失败。改用手动调用或封装好的脚本。

**方式一：trafilatura（推荐，中文友好）**

创建临时抓取脚本或直接用 `execute_code` 工具调用 Python：

```python
import trafilatura, json
url = "目标链接"
html = trafilatura.fetch_url(url)
if html:
    result = trafilatura.extract(html, output_format='json', with_metadata=True, include_comments=False)
    print(result or '{}')
else:
    print('{"error": "fetch failed"}')
```

**方式二（备用）：readability-lxml + requests**

同样通过 `execute_code` 工具直接执行 Python 代码块，不需要 `python -c`。

### ③-特殊：抖音/短视频链接

**两级提取策略**（`extract_douyin_full.py` 一次调用全覆盖）：

**Level 1**：iPhone UA + 括号计数法提取 `videoInfoRes` 嵌入 JSON → 标题/作者/互动数据。
**Level 2**：Playwright 无头 Chromium 渲染页面 → 尝试提取视频描述/字幕文本。

```bash
D:/opc-workdown/.venv/Scripts/python.exe D:/opc-workdown/extract_douyin_full.py "抖音链接"
```

返回 JSON 字段：`status`, `title`, `author`, `author_id`, `video_text`, `likes`, `comments`, `shares`, `hashtags`, `video_id`。

**如果 `status: failed` 或 `video_text` 为空**：视频转录不可用（抖音不公开）。执行失败流程：audit/links/ → audit/failed/ → 微信通知用户决定是否自动生成。

**其他短视频平台**：
- **B站 (bilibili)** → 类似方法，使用 `api.bilibili.com` 开放 API
- **抖音图文 (douyin article/note)** — `_$jsvmprt` 反爬保护。Level 1 (HTTP) 无法获取内容。Level 2 (Playwright headless) 也**只能获取元数据和 UI 文案，无法获取视频字幕/口播转录文本**——这是抖音平台的限制，不是技术问题。处理流程：先跑 Level 1 拿元数据 → 再跑 Level 2 尝试 → 如果 `video_text` 为空 → 移到 `audit/failed/` → 微信通知用户"提取失败，是否自动生成？"
- **小红书 (xiaohongshu)** → 动态渲染 + 强反爬，暂标记为"暂不支持"
- **视频号 (weixin)** → 微信内部链接，标记为"暂不支持"

### ④ 解析提取核心信息

拿到网页正文后，用 DeepSeek 模型提取结构化信息（在同一个 terminal 调用中完成，避免额外 API 调用）：

直接基于抓取到的 `title + content`，提炼出：
- **标题**：中文标题（如原文为英文则翻译）
- **作者/来源**：作者名、网站名
- **发布日期**：如有
- **一句话摘要**：核心观点（≤50 字）
- **关键要点**：3-5 个要点（每个 1-2 句）
- **知识点标签**：从六大板块中选择 1-3 个
- **相关概念**：可关联的已有 wiki 页面

分类映射：
| 关键词 | 板块 | wiki 目录 |
|--------|------|-----------|
| Agent, RAG, LLM, Prompt, Transformer, 微调, 模型 | AI 应用 | wiki/concepts/ai应用/ |
| 商业模式, 定价, 法务, 税务, 财务 | 商业基础 | wiki/concepts/商业基础/ |
| 内容创作, 平台运营, 个人品牌, 社群 | 自媒体学习 | wiki/concepts/自媒体学习/ |
| 变现, 赚钱, SaaS, 订阅, 付费 | AI 商业化 | wiki/concepts/ai商业化/ |
| 增长, 获客, 转化, SEO, 营销 | 产品与增长 | wiki/concepts/产品与增长/ |
| 自动化, 工具, 效率, 工作流 | 效率与自动化 | wiki/concepts/效率与自动化/ |

### ⑤ 更新 audit/links/ 存档

填充步骤②创建的存档文件的"解析结果"部分：
```markdown
## 解析结果
- 标题: xxx
- 作者: xxx
- 日期: YYYY-MM-DD
- 分类: xxx
- 摘要: xxx

### 关键要点
1. ...
2. ...
3. ...

### 提取的正文
(前 2000 字)
```

### ⑥ 生成 wiki 页面

在 `wiki/concepts/<板块>/` 下创建 wiki 页面，文件名使用中文：

```markdown
---
title: 页面标题
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: concept
tags: [标签1, 标签2]
sources: [https://原链接]
source_type: wechat-link
---

# 页面标题

## 一句话总结
核心观点

## 关键要点
1. **要点1**：详细说明
2. **要点2**：详细说明
3. **要点3**：详细说明

## 我的思考
（如果可以链接到已有知识库内容，写 2-3 句关联思考）

## 相关链接
- [[concepts/相关板块/已有页面]] — 关联说明
- [[concepts/相关板块/另一个页面]] — 关联说明

## 原始来源
- [原文标题](https://原链接)
- 分享日期：YYYY-MM-DD
```

### Wiki 页面放入合适的子目录

```
wiki/concepts/ai应用/        → AI Agent、RAG、LLM 等
wiki/concepts/商业基础/      → 商业模式、法务、财务等
wiki/concepts/自媒体学习/    → 内容创作、平台运营等
wiki/concepts/ai商业化/      → 变现、案例等
wiki/concepts/产品与增长/    → 增长、营销等
wiki/concepts/效率与自动化/  → 工具、自动化等
```

如果没有对应板块的目录，先 `mkdir -p` 创建。

### ⑦ 更新 wiki/index.md

在 index.md 的对应板块下添加新条目：

```markdown
- [[concepts/<板块>/页面名]] — 一句话摘要
```

按如下规则插入：
1. 定位到对应板块的 `## 🏢/📱/🤖/💼/📈/⚡` 区域
2. 在该板块的列表末尾追加新条目
3. 不要覆盖已有内容

同步更新 CLAUDE.md 的 "已有 wiki 页面" 计数。

### ⑧ 微信回复格式

处理完成后，在微信回复摘要卡片：

```
🔗 已消化链接

📄 标题
📂 分类：AI应用 / 商业基础 / ...
📝 摘要：一句话核心观点

💡 要点：
1. 要点一
2. 要点二
3. 要点三

📖 已存入知识库 → [[concepts/<板块>/页面名]]
（可在多Agent配置中查看完整内容）
```

### ⑨ 归档到 resolved/

处理完成后，将 `/audit/links/` 中的文件移动到 `/audit/resolved/`：

```bash
mv D:/opc-workdown/audit/links/YYYY-MM-DD-<slug>.md D:/opc-workdown/audit/resolved/
```

这样 `audit/links/` 中始终只保留待处理的链接，方便排查遗漏。

### ⑩ 生成配图（可选）

消化完内容后，可调用硅基流动免费生成封面配图发送到微信：

```bash
D:/opc-workdown/.venv/Scripts/python.exe D:/opc-workdown/siliconflow_gen.py "配图描述" $SILICONFLOW_API_KEY
```

配图提示词建议：基于文章主题，描述风格为"dark tech illustration, neon blue, clean modern"。详见 `references/siliconflow-image-gen.md`。

## 批量链接处理

如果用户一次分享多个链接（最多 5 个），逐个处理：
1. 先回复"收到 N 个链接，正在逐个消化..."
2. 每个链接独立执行步骤 ①-⑥
3. 步骤 ⑦ 在所有链接处理完后统一更新一次 index.md
4. 步骤 ⑧ 合并为一条消息推送所有摘要

## 内容质量规则

- **有实际内容 → 正常入库**。如果提取到了正文/转录，直接基于原文整理。
- **只有元数据 → 通知用户选择**。如果只拿到标题/作者（抖音视频常见情况），微信告知用户"无法提取内容，是否需要基于元数据自动生成？"
- **自动生成 → 必须标记**。如果用户同意生成，wiki 页面的 frontmatter 必须加 `generation: auto-synthesized`，并在页面底部注明"本文为自动生成，源内容未能提取"。
- **禁止**：创建只有结构没有正文的空壳页面。用户明确反对这种行为。

| 问题 | 处理方式 |
|------|---------|
| 无法访问（超时/403） | 记录到 audit/links/，状态=failed，回复"无法访问该链接" |
| 内容为空（JS 渲染页面） | 尝试 Level 2 Playwright 提取，仍失败 → 归档 failed/ |
| 抖音提取失败（无转录） | 移到 `audit/failed/`，微信通知"抖音不公开视频字幕，是否自动生成？" |
| 内容与知识库领域无关 | 保存到 audit/links/，标记 category=none，不创建 wiki 页面 |
| 已存在相同链接 | 检查 audit/failed/ + audit/resolved/，已有则跳过 |
| `python -c` 行内执行被拦截 | **禁止使用**，改用 `execute_code` 工具或调用脚本文件 |

## 环境依赖

Python venv: `D:\opc-workdown\.venv`（已预装所有依赖）

| 包 | 用途 |
|----|------|
| `trafilatura` | 普通网页正文提取（推荐） |
| `readability-lxml`, `beautifulsoup4` | 备用网页提取 |
| `requests` | HTTP 请求 |
| `playwright` | 抖音深度提取（Level 2），Chromium 已安装 |

### 图像生成参考

Hermes 内置 `image_gen` 工具集（FAL.ai），无需额外安装 Skill。需在 `.env` 中配置 `FAL_KEY`，注册：https://fal.ai

**提取脚本**：
- `scripts/extract_douyin_full.py` — 抖音统一提取（L1 快速 + L2 深度，一次调用）。skill 目录自带，可移植。
- `scripts/extract_douyin.py` — 纯 L1 快速提取（轻量备用）
- 外部路径：`D:\\opc-workdown\\extract_douyin_full.py`（与 skill 脚本保持同步）
- 详见 `references/extraction-scripts.md`

## Pitfalls

- **禁用 `python -c` 行内执行**：Hermes 安全机制将其判定为危险命令（exit code 49），微信端无人批准导致失败，且会导致 Gateway 会话卡死——后续微信消息无限排队不处理。改用脚本文件或 `execute_code` 工具。
- **禁止脑补内容**：如果视频/文章内容无法提取（status: failed），不要基于标题猜测或编造内容。移到 `audit/failed/`，微信通知用户"爬取失败已归档，是否需要自动生成？"由用户决定。
- **抖音图文不可提取**：抖音 `_$jsvmprt` 反爬保护使 Playwright 也无法获取图文内容，标记 failed 即可。
- **检查重复链接**：处理前搜索 `audit/links/` 和 `audit/resolved/`，发现已有则跳过。
- **Gateway 会话卡死诊断**：如果微信消息长时间无响应，检查 `gateway.log` 是否出现 "Queued follow-up... final stream delivery not confirmed"。用 `hermes gateway restart` 清除。
- **抖音图文 vs 视频**：视频用 iPhone UA 可提取，图文（文章/note）触发 `_$jsvmprt` 反爬，需 Playwright 方案。
- **空 wiki 页面** — 只写入实际提取到的内容。视频转录不可用时不脑补。
- **WeChat 会话排队** — 如果前一个请求未释放（如因危险命令拦截），后续消息会被排队不处理。重启 Gateway 清除。
- **audit/links/ 文件滞留** — 处理完立即 move 到 resolved/ 或 failed/。

## 参考文件

- `references/extraction-scripts.md` — 抖音提取脚本详解（extract_douyin_full.py 等）
- `references/douyin-extraction.md` — 抖音提取技术参考：Level 1/2 方法对比、API 字段、已知限制

## 验证

处理完每个链接后确认：
- [ ] **未使用 `python -c` 行内执行**（触发危险命令拦截导致 WeChat 静默失败）
- [ ] audit/links/ 中有对应的存档文件
- [ ] wiki/concepts/ 中有新页面
- [ ] wiki/index.md 中新增了索引条目
- [ ] 文件已从 audit/links/ 移到 resolved/ 或 failed/
- [ ] 微信已收到回复
