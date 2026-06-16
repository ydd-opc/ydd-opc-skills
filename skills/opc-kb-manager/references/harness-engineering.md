# Harness Engineering（驭缰工程）

> 2026 年 AI Agent 开发圈最热的概念。核心公式：Agent = Model + Harness

来源: [JavaGuide Harness Engineering 详解](https://javaguide.cn/ai/agent/harness-engineering.html)

---

## 一句话理解

模型是马，Harness 是**马具**。马（模型）再强，没有好的马具也跑不稳。

Harness = 模型之外的**整套系统**——系统提示词、工具调用、文件系统、沙箱环境、编排逻辑、反馈回路、约束机制。

## 为什么这个概念重要

**关键实验**：同一个模型，只换了文件编辑接口的调用方式，编码基准分数从 6.7% 跳到 68.3%。模型没变，变的是 Harness。

这意味着：**Agent 能不能稳定干活，很多时候跟模型关系不大，取决于你给模型搭的工作环境。**

## 六层架构

| 层级 | 名称 | 解决什么问题 | 关键设计 |
|:----:|------|------------|---------|
| L1 | 信息边界层 | Agent 该知道什么、不该知道什么 | 定义角色与目标，裁剪无关信息，结构化组织任务状态 |
| L2 | 工具系统层 | Agent 怎么和外部世界交互 | 选择工具、控制调用时机、提炼工具结果并反馈 |
| L3 | 执行编排层 | 多步骤任务怎么串起来 | 让模型按"理解目标→判断信息→分析→生成→检查"推进 |
| L4 | 记忆与状态层 | 长任务中间结果怎么管理 | 独立管理当前任务状态、中间产物和长期记忆 |
| L5 | 评估与观测层 | Agent 怎么知道自己做对了没有 | 建立独立于生成过程的验证机制 |
| L6 | 约束校验与恢复层 | 出错了怎么办 | 预设规则拦截错误，失败时重试/回滚/降级 |

**现实建议**：不要一上来想搭满六层。先做 L1（信息边界）和 L6（错误恢复），投入最低但见效最快。

## 与 Prompt / Context Engineering 的关系

| 层级 | 解决的问题 | 关注点 |
|------|-----------|--------|
| Prompt Engineering | 怎么把指令说清楚 | 让模型理解意图，减少局部歧义 |
| Context Engineering | 该给 Agent 看什么 | 在合适时机提供正确且必要的信息 |
| Harness Engineering | 系统怎么持续执行、纠偏、观测和恢复 | 长链路任务中的持续正确、偏差修正 |

三层一层套一层，范围越来越大。简单任务 Prompt 就够，需要外部知识时 Context 更重要，长链路商业场景 Harness 才是主矛盾。

## 生产线团队的实践经验

### OpenAI：三个人，五个月，一百万行，零手写代码
- 给 Agent 一张地图（架构图），不要塞一本千页手册
- 架构约束要靠工具执行（Linter 不通过就不让提交）
- 可观测性也要给 Agent 看（Agent 需要知道自己的行为日志）
- Slack 里的知识 Agent 很难稳定用上（知识要结构化，不要散落在聊天记录里）

### Anthropic：16 个 Agent 协作写 C 编译器
- 借鉴 GAN 架构：两个 Agent 互相监督和批评
- 遇到"上下文焦虑"（超过 40% token 窗口后质量下降）→ 直接清空上下文，通过结构化交接文档保留关键状态
- Context Reset 比压缩更有效

### Stripe：每周 1300+ 个 PR 的无人值守模式
- 高度自动化的 Harness 支撑大规模并发

### LangChain：Terminal Bench 2.0 从第 30 名升到第 5 名
- 只优化了 Agent 运行环境（文档组织、验证回路、追踪系统），模型没换
- 得分从 52.8% 提升到 66.5%

## 关键发现：上下文不是越多越好

168K token 窗口，用到约 40% 的时候质量开始明显下降：

| 区间 | 占比 | 表现 |
|------|:----:|------|
| Smart Zone | 0~40% | 推理聚焦、工具调用准确、代码质量高 |
| Dumb Zone | 超过 40% | 幻觉增多、兜圈子、格式混乱 |

目标不是给 Agent 塞更多信息，而是让它尽量停留在**干净、相关的上下文**里。生产环境监控上下文利用率，超过 40% 触发压缩或分段执行。

## 怎么从零开始搭 Harness

### P0：可以马上做
- 创建 AGENTS.md/CLAUDE.md，每次启动自动加载
- 写自定义 Linter + 修复指令
- 加基本的重试和错误恢复

### P1：稳了之后再补
- 渐进式上下文注入（不一次性塞完）
- Agent 可观测 Dashboard
- 任务状态持久化

### P2：有余力再考虑
- Multi-Agent 协作
- 动态工具选择
- 自优化反馈回路

## 和这个知识库的关系

这个项目（opc-workdown）本身就是 Harness Engineering 的一个实例：

```
CLAUDE.md       → L1 信息边界（告诉 Agent 该做什么）
Skills 系统      → L2 工具层（Horizon / wechat-digest / lint）
Cron 流水线      → L3 编排层（每天 9 点自动跑四步）
Memory + wiki   → L4 状态层（跨会话记忆和知识库）
健康检查 cron    → L5 评估层（每 3 天自动 lint）
iLink 限流处理   → L6 恢复层（错误拦截 + 替代方案）
```

用户正在做的 AI 客服产品，本质也是帮客户搭 Harness：知识库 = L1，DeepSeek = 推理引擎，回复逻辑 = L3，聊天记录 = L4。

## 延伸阅读

- JavaGuide: [Harness Engineering 详解](https://javaguide.cn/ai/agent/harness-engineering.html)
- LangChain: The Anatomy of an Agent Harness (Vivek Trivedi)
- Dex Horthy: 上下文窗口 40% 阈值理论
- [[concepts/ai应用/AIAgent开发架构]] — Agent 架构基础
- [[concepts/ai应用/WorldCup2026绿茵神算-Skill架构分析]] — 另一个 Skill = System Prompt 的实例
