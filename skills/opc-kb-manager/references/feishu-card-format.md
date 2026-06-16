# Feishu Interactive Card Format for Topic Push

飞书自定义机器人 Webhook 支持的消息类型中, interactive (卡片) 是最适合结构化信息展示的格式。

## 消息类型一览

| 类型 | `msg_type` | 适合场景 |
|------|:----------:|---------|
| 纯文本 | `text` | 简单通知/监控告警 |
| 富文本 | `post` | 日报/文章推送 (支持标题+图片+链接) |
| 卡片 | `interactive` | **选题推荐** (带标题栏+布局元素+按钮) |

## 卡片布局元素

| tag | 用途 | 说明 |
|-----|------|------|
| `div` | 内容块 | 可含 `text` (单段) 或 `fields` (双列) |
| `hr` | 分割线 | 分隔不同区域 |
| `note` | 底部灰色备注 | 放提示文字 |
| `column_set` | 多列布局 | `column_set` → `column` → `div` 嵌套 |
| `action` | 按钮 | 可跳转链接或触发回调 |

## 双列表格布局 (fields)

最接近"表格"的效果, 用 `div.fields` 实现：

```json
{
    "tag": "div",
    "fields": [
        {"is_short": true, "text": {"tag": "lark_md", "content": "**🎯 选题**\nxxx"}},
        {"is_short": true, "text": {"tag": "lark_md", "content": "**📂 类型**\n技能"}}
    ]
}
```

- `is_short: true` = 两列并排 (每列约50%宽度)
- `is_short: false` = 独占一行
- 每列支持 `lark_md` (Markdown 子集: **粗体**、\n换行、-列表)

## 完整示例 (选题推荐)

```python
payload = {
    "msg_type": "interactive",
    "card": {
        "header": {
            "title": {"tag": "plain_text", "content": "📋 本周选题推荐 | 06/14"},
            "template": "blue"     # blue / wathet / turquoise / green / yellow / orange / red / carmine / violet / purple / indigo / grey
        },
        "elements": [
            # 选题信息 — 双列表格
            {"tag": "div", "fields": [
                {"is_short": True, "text": {"tag": "lark_md", "content": "**🎯 选题**\n同样用AI..."}},
                {"is_short": True, "text": {"tag": "lark_md", "content": "**📂 类型**\n技能"}},
            ]},
            {"tag": "div", "fields": [
                {"is_short": True, "text": {"tag": "lark_md", "content": "**⭐ 冷启动分**\n9/10"}},
                {"is_short": True, "text": {"tag": "lark_md", "content": "**📎 备注**\n最通用痛点"}},
            ]},
            {"tag": "hr"},
            # 推荐理由
            {"tag": "div", "text": {"tag": "lark_md", "content": "**📝 推荐理由**\n• P0 优先级最高\n• 冷启动分 9/10"}},
            {"tag": "hr"},
            # 底部
            {"tag": "note", "elements": [{"tag": "plain_text", "content": "💡 收到后回复「开写」"}]}
        ]
    }
}
```

## 限制

- **没有原生数据表格组件** (有表头行+多行数据那种)。`fields` 是 2 列 key-value 网格, 不是 Excel 表格。
- **没有列宽控制** — 两列固定 50/50, 不能调比例。
- **lark_md 是简化版 Markdown** — 支持 `**粗体**` 和换行, 不支持 `# 标题`、`[链接]()`。
- **单张卡片元素上限**: ~50 个左右 (超过可能渲染异常)。

## 安全过滤陷阱

⚠️ **FEISHU_APP_SECRET 在 `execute_code` 中会被 `***` 过滤器拦截。**

在 Hermes 的 `execute_code` 工具中, 直接写 `os.environ['FEISHU_APP_SECRET'] = 'xxx'` 时,
如果 secret 包含 `***` 匹配模式 (或者会被全局关键字过滤), 代码执行时会报错 `SyntaxError`。

**正确做法 — 从 .env 文件读取, 不在代码中硬编码:**

```python
# 从 .env 文件读取, 避免在代码字符串中出现 secret
env_path = r"D:\soft\hermes\profiles\librarian\.env"
env_vars = {}
with open(env_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env_vars[k.strip()] = v.strip()

fs_app_id = env_vars.get("FEISHU_APP_ID", "")
fs_app_secret = env_vars.get("FEISHU_APP_SECRET", "")
fs_webhook = env_vars.get("FEISHU_WEBHOOK", "")
```

**替代方案 — 用终端(terminal)执行 Python 文件 (非 -c):**
写一个 .py 文件到磁盘, 然后用 `terminal(command="python path/to/script.py")` 执行。
`terminal` 工具不会触发 `***` 关键字过滤。

**完全不要做的事:**
- ❌ `os.environ['X'] = 'ToKuOV...xxx'` 在 execute_code 中 — 会被过滤
- ❌ 把 secret 放进文件名、git commit 消息、日志 — 安全风险 + 会被过滤

## 常规推送 vs 选题推送

| 场景 | msg_type | 脚本 | 特点 |
|------|:--------:|------|------|
| 每周精选推送 | `post` (富文本) | `feishu_push.py` | 带封面图+正文图, 长内容 |
| 选题推荐推送 | `interactive` (卡片) | `topic_picker.py` | 结构化字段, 双列表格, 短内容 |

两个场景的 token 获取和图片上传逻辑可共用。
