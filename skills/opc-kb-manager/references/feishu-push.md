# Feishu Push (飞书推送) — Weekly Digest Delivery

Push the Monday weekly digest to the user's Feishu bot/webhook.

## Overview

The user configured a Feishu custom bot webhook for weekly digest delivery.
The push is only done on **Mondays** as Step 7 of the weekly pipeline
(see "Weekly Digest (Monday)" in SKILL.md).

## Prerequisites

Three env vars in the profile `.env` (`D:/soft/hermes/profiles/<profile>/.env`):

| Variable | Purpose |
|----------|---------|
| `FEISHU_APP_ID` | Feishu app ID (starts with `cli_`) |
| `FEISHU_APP_SECRET` | Feishu app secret |
| `FEISHU_WEBHOOK` | Bot webhook URL (`https://open.feishu.cn/open-apis/bot/v2/hook/<uuid>`) |

## Message Format: Interactive Card (NOT post)

**Critical pitfall:** Feishu bot webhooks (`/bot/v2/hook/...`) do **NOT** support
`msg_type: post` for rich text messages. Sending a `post` payload returns:
```json
{"code": 10208, "msg": "'post' field required"}
```

Instead, use `msg_type: interactive` with a JSON card payload:

```json
{
  "msg_type": "interactive",
  "card": "<JSON string of card content>"
}
```

Text messages (`msg_type: text`) work fine for testing the webhook.

## Image Upload Flow

Images must be uploaded via the **tenant token** (not the webhook directly),
then referenced by `image_key` in the card:

```
Token: POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
       {"app_id": ..., "app_secret": ...}

Upload: POST https://open.feishu.cn/open-apis/im/v1/images
        Authorization: Bearer ***
        multipart: {image: (file.png, bytes, image/png)}
        form: {image_type: "message"}

Response: {"data": {"image_key": "img_v3_..."}}
```

## Script

Working script from the June 15 push:
`D:\opc-workdown\scripts\push-weekly-feishu.py`

Handles: token acquisition → image upload → card construction → webhook delivery.

## Card Structure

```python
card = {
    "config": {"wide_screen_mode": True},
    "header": {
        "title": {"tag": "plain_text", "content": "📡 本周 AI 要闻精选｜M月D日 - M月D日"},
        "template": "blue"
    },
    "elements": [
        {"tag": "img", "img_key": "cover_key", "alt": {"tag": "plain_text", "content": "cover"}},
        {"tag": "div", "text": {"tag": "lark_md", "content": "intro with **markdown**"}},
        {"tag": "hr"},
        {"tag": "div", "text": {"tag": "lark_md", "content": "**🔥 Title**\nDescription\n💡 *insight*"}},
        {"tag": "hr"},
        {"tag": "img", "img_key": "body_key", ...},
        {"tag": "note", "elements": [{"tag": "plain_text", "content": "footer"}]}
    ]
}
```

Supported element tags: `div` (text with `lark_md`), `img`, `hr`, `note`.

## Troubleshooting

| Symptom | Cause |
|---------|-------|
| 10208 "post field required" | Use `interactive` not `post` |
| 99991663 "system busy" | Image key expired — re-upload |
| 401 on image upload | Token expired — get fresh one |
