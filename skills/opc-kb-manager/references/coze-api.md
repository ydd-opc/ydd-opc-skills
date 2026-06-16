# 扣子 Coze 智能体 API 调用

## Bot 分享 API 调用方式

Coze 智能体发布为 API 服务后，通过 stream_run 接口调用：

**Endpoint**: `POST https://{subdomain}.coze.site/stream_run`

**Headers**:
```
Authorization: Bearer pat_xxxxxxxxxxxxx
Content-Type: application/json
```

**Request Body**:
```json
{
    "content": {
        "query": {
            "prompt": [{"type": "text", "content": {"text": "你的问题"}}]
        }
    },
    "type": "query",
    "session_id": "自定义会话ID",
    "project_id": 7651088279185539126
}
```

## 获取必要信息

- **Token**: 扣子 → 空间设置 → API 管理 → 添加个人访问令牌（`pat_`开头）
- **Bot ID**: 在智能体编辑页 URL 中获取 `https://www.coze.cn/space/***/bot/73428668***`，`bot/`后的数字
- **Project ID**: 在 stream_run URL 中获取，或从分享信息中拿到
- **Session ID**: 任意字符串，同一会话上下文共享

## SSE 响应格式

响应是 Server-Sent Events (SSE) 格式，逐行解析 `data:` 前缀的 JSON：

```python
def call_coze_bot(prompt):
    r = requests.post(url, json=payload, headers=headers, timeout=120)
    full_answer = ""
    for line in r.text.split("\n"):
        if line.startswith("data: "):
            data = json.loads(line[6:])
            if data.get("type") == "answer" and not data.get("finish"):
                answer = data.get("content", {}).get("answer", "")
                if answer:
                    full_answer += answer
    # Extract image URLs from markdown
    urls = re.findall(r'https?://[^\s"<>]+\.(?:png|jpg|jpeg|gif|webp)[^\s"<>]*', full_answer)
    return full_answer, urls
```

## 简笔画生成 Prompt 模板

```
[固定主角描述] + [动作/场景] + [情绪] + [风格约束]
```

示例：
```
一只英短蓝猫，圆脸大眼睛灰色毛发，垂头丧气坐在空荡荡的办公桌前，桌上只有一个空杯子，简笔画风格
```

- 主角描述固定不变，保持形象一致性
- 只改动动作/场景/情绪部分
- 文字对话框可以通过描述加入："旁边有一个对话框，里面写着'没工作没饭吃'"

## Token 与配额

- 个人免费版：累计 500 次免费额度
- 超出后返回 `402 此应用已停止服务，可联系开发者充值积分`
- API 调用失败时检查：token 是否过期、bot 是否已发布为 API 服务
