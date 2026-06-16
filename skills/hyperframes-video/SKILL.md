---
name: hyperframes-video
description: 基于 HyperFrames 官方 7 步流水线制作中文口播视频。Capture → Design → Script → Storyboard → Voiceover → Build → Validate。适配 Windows 中文环境，包含 whisper 时间轴生成、逐场景 preview 验证、FFmpeg 音频合成。适用：知识分享/个人经历/产品介绍口播视频。
---

# HyperFrames 口播视频制作 Skill

---

## 前置依赖

| 依赖 | 版本要求 | 检查命令 |
|---|---|---|
| Node.js | 22+ | `node --version` |
| FFmpeg | 8.x（含 whisper） | `ffmpeg -version` |
| whisper 模型 | small（中文推荐） | `ls models/ggml-small.bin` |

### Windows 特殊设置

- HyperFrames CLI 入口：`<node22路径> node_modules/hyperframes/dist/cli.js`
- 渲染参数：`--workers 2`（低压 CPU 防卡顿）
- 音频路径：Windows 绝对路径会导致 404，用 FFmpeg 后期合成

---

## 项目目录结构

```
项目名/
├── DESIGN.md              # 视觉规范（配色/字体/动效边界/禁止项）
├── SCRIPT.md              # 口播定稿（全量文案）
├── STORYBOARD.md          # 分镜表（每段口播→画面→动画→素材）
├── transcript.srt         # whisper 生成的原始字幕
├── transcript.md          # SRT 文本版（Obsidian 可读）
├── transcript-可读版.md    # 表格版（人工校对用）
├── package.json           # HyperFrames 项目配置
├── hyperframes.json       # 组件路径配置
├── index.html             # 主工程文件
├── assets/
│   ├── 口播音频.wav        # 配音文件
│   ├── screenshots/       # 真实界面截图（命名：场景-序号-描述.png）
│   ├── images/            # 生成的背景/装饰图
│   └── broll/             # 录屏素材（命名：场景-描述.mp4）
└── renders/               # 渲染输出目录
```

---

## 七步流水线

### 第 1 步：采集素材（Capture）

**输入**：无
**输出**：`assets/` 目录下的截图/录屏/参考图
**完成标志**：分镜表里所有素材项的 `assets/` 路径已确认

**做什么**：
- 截取真实界面（招聘软件、Dan Koe 页面、微信截图等）
- 录屏操作过程（如果有演示环节）
- 收集品牌参考图（logo、配色卡）
- 文件命名规范：`screenshots/场景序号-描述.png`，如 `screenshots/s2-招聘软件.png`
- 如果没有素材，明确标注"纯文字动效风格"

**常见坑**：
- 截图分辨率不够（至少 1920×1080）
- 文件名用中文 + 空格可能路径问题（建议用英文描述或数字）

---

### 第 2 步：设计风格（Design）

**输入**：素材、口播主题、目标受众
**输出**：`DESIGN.md`
**完成标志**：颜色/字体/字幕样式/动效边界全部定稿，用户确认

**做什么**：
```
DESIGN.md 必须包含：
├── 基础参数（分辨率/帧率/时长/渲染引擎）
├── 配色方案（每种情绪的色板：主色/辅色/强调色/文字色）
├── 字体体系（标题/字幕/数字各自的字体+备选+字号范围）
├── 字幕样式（位置/字号/颜色/背景/动画）
├── 动效边界（哪些能用、哪些禁止——基于渲染器兼容性）
├── 转场规则（硬切 vs 特效转场的位置和类型）
└── 禁止项（字体/颜色/CSS属性/GitHub Claude Design 禁令）
```

**关键决策**：
- 不同叙事情绪 → 不同背景色板（不能全片一个色）
- 动效只用什么：opacity/autoAlpha, transform, filter:blur(), backgroundPosition
- 动效禁止什么：Math.random(), mix-blend-mode, -webkit-background-clip:text, className切换
- 字体禁止什么：Inter, Roboto, Open Sans, Lato, Poppins（Claude Design 官方禁令）

---

### 第 3 步：写脚本（Script）

**输入**：视频主题、目标时长
**输出**：`SCRIPT.md`
**完成标志**：口播文案定稿，按场景分好段

**做什么**：
- 将口播文案按叙事节奏分段（通常 7-15 个场景）
- 每个场景标注核心情绪和关键短语
- 全文统计字数，估算时长（中文约 4-5 字/秒）
- 脚本是后续分镜的唯一文字来源，定稿后不改

---

### 第 4 步：写分镜（Storyboard）

**输入**：`SCRIPT.md` + `DESIGN.md`
**输出**：`STORYBOARD.md`
**完成标志**：每段口播都有对应的画面/素材/动画/转场描述

**做什么**：
```
STORYBOARD.md 格式（每个场景一张表）：
| 时间 | 口播 | 画面 | 素材路径 | 动画 | 转场 |
```

**核心原则**：
- 时间列留空，等 whisper SRT 后再填
- 每个场景标注情绪和配色（引用 DESIGN.md 的色板名）
- 素材路径明确到文件名：`assets/screenshots/xxx.png`
- 转场只设计 2-3 个关键时刻，其余硬切
- 每场景必须有"静止期做什么"——不能让画面完全不动

---

### 第 5 步：配音和时间戳（Voiceover）

**输入**：口播音频 WAV + whisper 模型
**输出**：`transcript.srt` + 人工确认
**完成标志**：用户逐条校对完 SRT，时间戳 + 文字都正确

**做什么**：
```bash
# ① 转换音频格式（可选，WAV 也可以直接用）
ffmpeg -i 口播.wav -codec:a libmp3lame -b:a 192k -ar 44100 口播.mp3

# ② whisper 转录（small 模型，中文）
ffmpeg -i 口播.wav -af "whisper=model=ggml-small.bin:language=zh:format=srt:destination=transcript.srt" -f null NUL

# ③ 生成 Obsidian 可读版本
node -e "转换 SRT → transcript-可读版.md（表格格式）"
```

**关键决策**：
- 模型选择：base（142MB，快但中文差）vs small（466MB，慢但中文好）
- SRT 时间戳精度：2-3 秒/段，分段太碎会难校对
- **这一步必须用户确认后才能进入 Build**

**把 SRT 时间戳回填到分镜表**：
- 将确认后的精确时间写入 STORYBOARD.md 的时间列
- GSAP 动画的 `tl.fromTo(el, {}, {}, startTime)` 直接使用 SRT 的时间

---

### 第 6 步：构建 HTML（Build）

**输入**：`STORYBOARD.md`（含确认时间戳） + `DESIGN.md`
**输出**：`index.html`
**完成标志**：所有场景在 preview 中逐场景验证通过

**Build 规则（逐场景迭代，不允许一次性写完全部）**：

```
for 每个场景:
  ① 写该场景的 HTML 结构（文字 + 背景 + 叠加层）
  ② 写 GSAP 动画（ENTRY → HOLD → EXIT 三段）
  ③ 用户刷新 preview → 确认 → 通过/修改
  ④ 锁定该场景，进入下一个
```

**index.html 架构**：
```
<html>
  <head>: GSAP CDN + 字体 + 全部 CSS
  <body>:
    ├── 背景层（多个 div 叠加，通过 opacity 切换）
    ├── 音频 <audio>
    ├── 场景文字元素（每个场景独立 div）
    ├── 转场叠加层（grid wipe / parallax / morph）
    ├── 编辑器强调层（editorial emphasis）
    ├── 粒子容器
    ├── 暗角 + 颗粒层
  <script>:
    ├── GSAP timeline（paused:true）
    ├── 每场景 ENTRY + HOLD + EXIT
    ├── 转场动画
    ├── window.__timelines["main"] = tl
```

**技术约束**：
- 背景切换：用多个 bg div 的 opacity 过渡，不用 className 切换
- 文本可见性：用 `autoAlpha`，不用 `opacity` + `visibility` 分开写
- 确定性渲染：不用 `Math.random()` / `Date.now()` / `setInterval`
- 缓动多样性：每场景至少用 3 种不同 ease
- HOLD 阶段：每场景至少有一段持续微动（呼吸/浮动/脉冲）

---

### 第 7 步：预览校验渲染（Validate）

**输入**：`index.html`
**输出**：`renders/最终版.mp4`
**完成标志**：视频可播放，音频同步，所有效果正常

**流程**：
```bash
# ① Lint
node node_modules/hyperframes/dist/cli.js lint

# ② Preview（逐场景人工确认）
node node_modules/hyperframes/dist/cli.js preview
# → 浏览器 http://localhost:3002 拖进度条抽查

# ③ 全量渲染（--workers 2 防卡顿）
node node_modules/hyperframes/dist/cli.js render --fps 30 --workers 2

# ④ 合成音频（Windows 需要后期合成）
ffmpeg -i renders/xxx.mp4 -i assets/口播音频.wav \
  -c:v copy -c:a aac -b:a 192k -shortest renders/最终版.mp4
```

**验证清单**：
- [ ] `lint` 0 error
- [ ] 每个场景在 preview 拖进度条确认
- [ ] 音频和字幕时间轴同步（抽检 5 个时间点）
- [ ] 背景色切换平滑（无白屏/闪烁）
- [ ] 转场效果正常（无黑屏/残留）
- [ ] 渲染输出：1920×1080, 30fps, 含双轨（视频+音频）
- [ ] 暗角+颗粒全片持续

---

## 改进建议（相比本次实战）

| 问题 | 本次实战 | 改进方案 |
|---|---|---|
| whisper 模型选择 | 先用 base 后换 small，浪费一轮 | 直接上 small，或在 CI 环境跑 large 模型 |
| Build 策略 | 一次性写完整 284 秒 HTML，渲染 30 分钟才发现问题 | 逐场景 preview 验证，全对了一次渲染 |
| 背景切换 | 用 className 切换，渲染器里变白屏 | 用独立 bg div + opacity 过渡 |
| 动效兼容 | 用了 mix-blend-mode/webkit-background-clip 等失效属性 | 限制为已验证属性集合 |
| 字体映射 | Noto Sans SC 不在确定性映射表中 | 用 `@font-face` 指定本地/托管字体，或接受 fallback |
| 音频嵌入 | 依赖 HyperFrames `<audio>` 标签，Windows 路径 404 | 始终用 FFmpeg 后期合成 |
| 时间轴来源 | 手写硬编码 | SRT 驱动所有 GSAP 时间参数 |
| 分镜表 | 边写 HTML 边想 | 先写 STORYBOARD.md，再用它指导 HTML 结构 |
| 用户确认 | 渲染完才知道不对 | 每个步骤有明确的完成标志和用户确认点 |

---

## 适用场景

此 Skill 适用于：
- 中文口播类视频（知识分享、个人经历、产品介绍）
- 单人录制，纯音频 + 文字动效画面
- 时长 1-10 分钟
- Windows 开发环境

不适用于：
- 需要实拍画面剪辑的视频
- 多人物对话/采访
- 需要唇形同步的数字人口播
