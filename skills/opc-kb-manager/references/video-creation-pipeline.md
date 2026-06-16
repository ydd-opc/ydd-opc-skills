# 视频内容创作流水线

一人公司视频内容制作流程: 公众号文章 → 口播稿 → 录音/VoxCPM → HyperFrames动效视频

## 完整流程

```
公众号文章（wechat-push/）
  → 口播稿（drafts/，遵 writing-style-guide.md 口播稿规范）
  → 录音（自己录或 VoxCPM 线上生成）
  → HyperFrames 动效视频
  → 导出 MP4
```

## 口播稿 → HyperFrames 视频

### 1. 创建项目

```bash
mkdir videos/<project-name>
cd videos/<project-name>
# 创建 package.json 含 hyperframes 依赖
# npm install hyperframes@0.3.0
```

### 2. HTML 结构要点

- 必须用 Node.js 22（v18 不支持 util.styleText）
- root 元素: `data-composition-id="main" data-width="1920" data-height="1080" data-duration="<秒数>"`
- 音频: `<audio src="narration.wav" data-start="0" data-duration="<秒数>" data-track-index="0" data-volume="1">`
- 音频文件名：用英文字母（中文文件名 HF 文件服务器 404）
- GSAP 时间轴: `window.__timelines["main"] = tl`
- `paused: true` 在 GSAP timeline

### 3. 渲染

```bash
# FFmpeg 必须在 PATH 中
export PATH="/c/Users/yuanjiafeng/AppData/.../bin:$PATH"
/d/soft/nvm/v22.10.0/node-v22.10.0-win-x64/node.exe node_modules/hyperframes/dist/cli.js render
```

### 4. 动效模板（kinetic-type 风格）

每个场景包含:
- 文字从某个方向滑入（x: -80 → 0 / y: 40 → 0）
- 带模糊入场（blur: 8 → 0）
- 停留若干秒
- 退场（opacity:0 + y:-30 + blur:6）
- 场景间用 stagger 错开时间

GSAP 动效参数参考:
- `power3.out` — 平滑缓出
- `back.out(1.7)` — 弹性过头效果
- `elastic.out(1,0.5)` — 弹性振动
- `scale: 0.5 → 1` — 缩放入场
- `rotation: -10 → 0` — 旋转入场

## 音色设计（VoxCPM）

- 线上体验站: https://voxcpm.modelbest.cn/
- 声音描述用英文效果好，示例: `(male, warm and confident, like a podcaster talking to a friend)`
- 口播稿不要用【停顿】标记，用句号断句
