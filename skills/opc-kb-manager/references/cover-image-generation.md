# 配图生成规范 v2 — 每篇文章配相关图片

> 不再使用"一张通用电脑图"，改为根据文章主题生成/选择相关配图。

## 原则

1. **封面图** — 1 张，cover_wechat 尺寸（1024×512），代表当日整体 AI 趋势
2. **文章配图** — 每篇文章配 1 张，landscape_16_9 尺寸（1024×576），与文章主题强相关
3. **提示词**必须用**英文**，描述具体场景而非抽象概念
4. 风格统一：minimalist, dark theme, neon blue/purple accents

## 配图策略

| 文章主题 | 配图思路 | Prompt 关键词 |
|---------|---------|-------------|
| LLM/模型/数学 | 黑板公式、研究论文堆、思维图谱 | equations, blackboard, research, deep thinking |
| 大公司新闻（Meta/Google/OpenAI） | 公司 logo + 相关场景 | logo, interface, cybersec |
| 编程/工具/基础设施 | 代码、服务器、终端界面 | code, terminal, server rack, data flow |
| AI 安全/伦理/政策 | 锁、盾牌、天平、网络脉络 | security shield, digital lock, balance |
| 硬件/芯片/性能 | 芯片、电路板、光速脉冲 | chip, circuit board, photon, pulse |
| 创业/商业/个人 | 箭头、曲线、光、上升轨迹 | arrow, growth curve, light beam |

## 性能优化

封面图和文章配图之间没有依赖关系，可**并行生成**：
1. 先起封面图（1 个 terminal call）
2. 立即并行起所有文章配图（N 个 parallel terminal calls）

## 封面图

```bash
D:/opc-workdown/.venv/Scripts/python.exe D:/opc-workdown/siliconflow_gen.py \
  "English prompt for the day's overall trend" \
  --ratio cover_wechat \
  --output D:/opc-workdown/outputs/cover-YYYY-MM-DD.png
```

## 文章配图

```bash
D:/opc-workdown/.venv/Scripts/python.exe D:/opc-workdown/siliconflow_gen.py \
  "English prompt strongly related to this article" \
  --ratio landscape_16_9 \
  --output D:/opc-workdown/outputs/article-关键词-YYYY-MM-DD.png
```

## 三种尺寸

| 用途 | --ratio | 尺寸 |
|------|---------|------|
| 公众号封面 | cover_wechat | 1024×512 (2.35:1) |
| 文章配图 | landscape_16_9 | 1024×576 (16:9) |
| 小红书封面 | cover_xhs | 1024×1365 (3:4) |

## 提示词指南

- 英文 prompt，描述具体场景
- 风格：minimalist, futuristic, dark theme, neon blue/purple
- 不要文字、不要中文
- 基于文章主题提取 3-5 个关键词融入 prompt

## 小说封面生成

小说封面用 square_1_1 尺寸（1024×1024），番茄小说等平台通常需要竖向封面。

### Prompt 模式

```
"<人物描述> standing on the <左/右> side of the frame, back to the viewer, 
upper body visible, slightly turning to reveal a handsome delicate side profile, 
<着装风格> with ethereal fabric, vast starry galaxy sky background, 
deep blue and purple cosmic tones, dreamy atmosphere, cinematic lighting, 
composition: person on <左/右> third"
```

### 着装风格选项

| 风格 | 关键词 |
|------|--------|
| 古风玄幻 | ancient fantasy robes, long flowing robes, ethereal fabric |
| 未来科幻 | futuristic sleek armor, high-tech sci-fi suit, subtle glowing accents |
| 现代 | dark coat, casual elegant clothes |

### 中文文字

AI 生图对中文文字的渲染**不可靠**（可能缺字、错字、变形）。如果需要书名文字，建议用修图工具后期添加，不要在 prompt 中依赖 AI 生成文字。如果一定要在 prompt 中加入，格式为：

```
On the left side of the starry sky, large glowing elegant Chinese calligraphy 
text reading '破万法', luminous characters floating among the stars
```

### 迭代策略

- 第一版确认构图和风格
- 第二版调整人物位置（左/右）、着装风格
- 文字后期用修图工具添加更可靠

### 文件命名

```
D:/opc-workdown/outputs/<书名>-封面.png
```

## 依赖

- SILICONFLOW_API_KEY 在 `D:/soft/hermes/.env` 或 librarian 的 .env 中
- 免费额度，不消耗余额
- iLink 限流：不要在短时间内发送多张图片，正常日更（每天一次）不会触发
