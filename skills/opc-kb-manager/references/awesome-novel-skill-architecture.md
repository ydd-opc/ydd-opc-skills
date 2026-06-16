# awesome-novel-skill 架构参考

> 来源：https://github.com/modoojunko/awesome-novel-skill
> Claude Code 原生小说写作插件，26K+ Star

## 角色体系

| Agent | 职责 |
|-------|------|
| **novel-agent** | 项目入口，检测进度、调度子 agent（状态驱动循环） |
| **volume-planner** | 主线拆纲 + 卷纲规划（四维方法论） |
| **chapter-planner** | 章纲生成（memo + 情绪设计 + hooks） |
| **prompt-crafter** | 9 层提示词组装 |
| **writer** | 正文生成 + AI 味自检（纯净上下文，只读 prompt） |
| **reader** | 10 维 60+ 细项深度评审（可选环节） |
| **updater** | 归档 + lore-keeping + 设定变更 |

## 核心架构：状态驱动循环

```
Step 1（检测状态）→ 匹配路由 → Read 子skill → 执行子task → 更新状态 → 回到 Step 1
```

`chapter.md#status` 字段是路由决策的唯一依据。所有子 skill 读取此状态并在完成后更新它。

### 调度流程

```
主 AI（加载 @novel-agent）
  │
  ├── 读 status.md → 判断当前 phase
  ├── 写 order 文件到 .agent/task/{type}-order.md
  ├── 通过 Agent 工具调度子 agent
  │     ├── volume-planner / chapter-planner（outline）
  │     ├── prompt-crafter / writer（draft）
  │     ├── reader（review，可选）
  │     └── updater（archive / setting-update）
  ├── 子 agent 完成后清理 order 文件
  └── 检测到 order 清理 → 推进下一阶段
```

要点：novel-agent 不直接写内容文件，只写 order 文件。子 agent 通过 Agent 工具调用，独立完成任务。

## 目录结构

```
{project-name}/
├── story.md              # 项目索引（元信息/主线拆纲/卷规划）
├── CLAUDE.md             # 项目级 AI 指令
├── .agent/status.md      # 当前状态
├── settings/
│   ├── world-setting.md  # 世界观
│   ├── writing-style.md  # 写作风格
│   ├── genre-setting.md  # 题材设定
│   └── character-setting/
│       └── <id>.md       # 每角色一个
├── volumes/
│   └── volume-{N}.md     # 卷纲（四维：情绪走向/冲突阶梯/信息差/场景卡）
├── chapters/
│   └── vol-{N}-ch-{M}.md # 章纲（status 驱动路由）
├── archives/
│   ├── *.draft.md        # 草稿
│   └── vol-{N}-ch-{M}.md # 完本章节
├── review/
│   └── vol-{N}-review.md # 卷评审
└── .claude/
    ├── agents/            # 各 agent 的 system prompt
    ├── knowledge/         # 知识库（写作风格、章节检查清单等）
    └── memory/            # 动态记忆（章节/角色/提示词）
```

## 卷规划四维方法论

| 维度 | 说明 |
|------|------|
| **情绪走向** | 整卷情绪变化弧线（压抑→提升→打脸→装逼） |
| **冲突阶梯** | 2-4 层逐级升高的障碍，每层间有转折点 |
| **信息差** | 起点→终点（开始时谁知道什么不知道什么，结束时谁知道了新信息） |
| **场景卡** | 每章三要素（主角想干啥+拦着他+悬念） |

## 章节状态驱动

每章文件通过 `status` 字段标识当前阶段：outline → drafted → verified → archived。

## Hermes 能复刻的部分 vs 不能复刻的

| 功能 | Hermes | awesome-novel-skill |
|------|--------|:-------------------:|
| 目录结构 + 设定管理 | ✅ | ✅ |
| 卷纲/章纲生成 | ✅ | ✅ |
| 正文写作 | ✅ | ✅ |
| 读者审评 | ✅（我扮演 reader） | ✅（独立 reader agent） |
| 归档 | ✅ | ✅ |
| **自主循环**（检测状态→调下一环→无需人介入） | ❌ 需要你说"写下一章" | ✅ |
| **超长上下文一致性** | ❌ 长篇可能忘前面伏笔 | ✅（子 agent 独立上下文） |
| **并行写作** | ❌ 一步步来 | ✅（writer 写一章同时 planner 规划下一章） |

## 实战结论

- **短篇（3000-8000字）**：Hermes 完全够用，差距约等于零
- **长篇（10万+字）**：建议用 awesome-novel-skill（Claude Code 插件），有自主循环和上下文优势
- Hermes 和 awesome-novel-skill 互不冲突——前者管理知识库和公众号，后者写小说
