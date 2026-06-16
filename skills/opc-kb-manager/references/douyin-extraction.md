# 抖音链接提取指南

## 视频链接（可行）

使用 iPhone User-Agent 请求分享页，提取嵌入式 JSON：

```bash
D:/opc-workdown/.venv/Scripts/python.exe D:/opc-workdown/extract_douyin_full.py "链接"
```

**可获取**: 标题、作者、互动数据（点赞/评论/分享）、话题标签

**不可获取**: 视频口播内容/字幕（Douyin 不公开）

## 图文/文章（不可行）

抖音图文页面返回 `_$jsvmprt` 反爬脚本，需 Playwright 无头浏览器渲染。
当前未安装 Playwright，标记为"需手动搬运"。

## 反爬注意事项

- 使用 iPhone UA（`Mozilla/5.0 iPhone...`）
- 不需要 cookie 或登录
- 与用户抖音账号无关，零风险
- 提取失败 → 归档到 audit/failed/

## 合并到知识库时

- 视频内容待补充 → 标注「🎬 视频内容待观看后补充」
- 不能脑补或合成内容
- 只写已提取到的信息
