# HyperFrames 视频生产参考

> HTML → MP4 渲染框架，文字动画+画面切换。
> 项目在 `D:\opc-workdown\videos\` 下。

## 前提条件

| 条件 | 说明 |
|------|------|
| Node.js 22+ | v18 不支持 `util.styleText`。用 `D:\soft\nvm\v22.10.0\node-v22.10.0-win-x64\node.exe` |
| FFmpeg | 已安装（WinGet），在终端 PATH 上 |
| 音频文件 | **必须存在**，否则渲染卡在 70% 不动（file server 无限 404 重试） |

## 已知坑（render 卡住）

**症状**: `70% Capturing frame N/1500` 不动，伴有 `[FileServer] 404 Not Found: /hf-ext/.../录音.m4a`

**原因**: HTML 中 `<audio src="文件.m4a">` 引用的音频文件不存在或路径不对。HyperFrames 的 file server 会无限重试 404，导致 frame capture 卡死。

**解决**: 
1. 确保音频文件存在，文件名不要含中文
2. 或者暂时去掉 `<audio>` 标签，先渲染无音频版看效果
3. 音频后续在剪映里合成

## 初始化项目

```json
// package.json
{ "dependencies": { "hyperframes": "^0.3.0" } }
```
```bash
npm install
```

## HTML 结构要点

- 固定尺寸：`data-width="1080" data-height="1920"`（竖屏）
- 总时长：`data-duration="<秒数>"`
- 所有元素用 CSS 绝对定位
- 动画用 GSAP 时间轴控制（不用 CSS animation/transition）

## GSAP 时间轴

```javascript
const tl = gsap.timeline({ paused: false });

// 平滑入场
tl.to("#element", { opacity:1, x:0, duration:0.8, ease:"power2.out" }, 启动时间);
// 退场
tl.to("#element", { opacity:0, x:80, duration:0.4 }, 退场时间);
// 场景停留
tl.to({}, { duration: 1.5 }, 停留开始时间);
// 循环动画（粒子）
tl.to("#particle", { y: -80, duration: 4, repeat: -1, yoyo: true }, 0);
// 暴露时间轴
window.__timelines = { main: tl };
```

## 支持的效果

| 效果 | 实现方式 |
|------|---------|
| 文字滑入 | x:0 + opacity:1 结合 translateX 初始偏移 |
| 缩放放大 | scale:0.5 → scale:1，配合 back.out 弹性 |
| 分割线展开 | width:0 → width:目标值 |
| 粒子浮动 | y 轴来回动画，repeat:-1, yoyo:true |
| 音频同步 | `<audio src="audio.m4a" data-start="0" data-duration="秒数"></audio>` |

## 渲染命令

```bash
/d/soft/nvm/v22.10.0/node-v22.10.0-win-x64/node.exe node_modules/hyperframes/dist/cli.js render
```

输出在 `renders/<project-name>_<timestamp>.mp4`。

## 注意事项

- CDN 资源会被自动 inline，不影响输出
- 音频文件名不要含中文（编码问题）
- 超长视频（50s+）渲染约 1 分钟/10 秒
