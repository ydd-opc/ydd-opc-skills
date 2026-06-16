# 抖音内容提取技术参考

## 方法总结

### Level 1：快速提取（HTML 解析）

**原理**：用 iPhone User-Agent 请求抖音分享页，页面返回预渲染 HTML，内含嵌入式 JSON（`window._ROUTER_DATA` → `videoInfoRes`）。

**提取字段**：标题、作者昵称/ID/签名、发布时间、点赞/评论/分享数、话题标签。

**脚本**：`D:\opc-workdown\extract_douyin.py`（独立 Level 1）
**统一脚本**：`D:\opc-workdown\extract_douyin_full.py`（Level 1 + Level 2 合并）

**关键参数**：
- User-Agent: `Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15`
- `Accept-Language: zh-CN,zh;q=0.9`
- JSON 提取用 bracket-counting 算法（非正则，避免截断）

### Level 2：深度提取（Playwright）

**原理**：用无头 Chromium 渲染页面，展开完整描述，遍历 DOM 文本节点。

**局限**：抖音不公开视频字幕/转录文本，Playwright 也无法获取口播内容。仅能获取描述文本和 UI 文案。

**脚本**：`D:\opc-workdown\extract_douyin_full.py` 内部调用 `extract_level2()`
**独立脚本**：`D:\opc-workdown\extract_douyin_playwright.py`

**环境依赖**：
```bash
uv pip install --python D:/opc-workdown/.venv/Scripts/python.exe playwright
D:/opc-workdown/.venv/Scripts/python.exe -m playwright install chromium
```

### 失败处理

Level 1 成功 + Level 2 失败 → 元数据可用，但 `video_text` 为空
Level 1 失败 → 整体失败，归档到 `audit/failed/`

## 已知限制

| 类型 | 支持 | 原因 |
|------|:---:|------|
| 抖音视频 | ✅ Level 1 | iPhone UA 可获取元数据 |
| 抖音视频口播内容 | ❌ | 不公开字幕/转录 |
| 抖音图文(文章) | ❌ | `_$jsvmprt` 反爬保护，需真实浏览器执行 JS |
| B站视频 | 待验证 | 可能通过开放 API |
| 小红书 | ❌ | 强反爬 |
| 微信视频号 | ❌ | 微信内部链接 |

## 链接识别

**抖音域名**：`v.douyin.com`, `www.douyin.com`, `iesdouyin.com`

**提取 URL**：从微信消息中提取 `https://v.douyin.com/XXXXXXXXX/`，忽略后面的元数据（`mqR:/ 05/08 j@c.AT :2pm` 等）。

**注意**：日志可能截断长 URL（如 `https://v.douyin.com/Dv7lH...`），需要用户提供完整链接。
