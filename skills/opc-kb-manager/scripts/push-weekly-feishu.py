"""Push weekly digest to Feishu - interactive card format.
Usage: python push-weekly-feishu.py
Requires: FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_WEBHOOK in profile .env
"""
import json, requests, os, sys

def load_env(profile_env):
    env = {}
    with open(profile_env, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip("\"'")
    return env

env = load_env(os.path.expanduser("~/.hermes/profiles/librarian/.env"))
app_id, app_secret, webhook = env.get("FEISHU_APP_ID"), env.get("FEISHU_APP_SECRET"), env.get("FEISHU_WEBHOOK")
if not all([app_id, app_secret, webhook]):
    print("ERROR: Missing Feishu env vars"); sys.exit(1)

# Get token
r = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                   json={"app_id": app_id, "app_secret": app_secret}, timeout=30)
token = r.json()["tenant_access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Upload images
keys = {}
for fpath, label in [("cover.png", "cover"), ("body.png", "body")]:
    with open(fpath, "rb") as f:
        resp = requests.post("https://open.feishu.cn/open-apis/im/v1/images",
                             headers=headers, files={"image": (f"{label}.png", f, "image/png")},
                             data={"image_type": "message"}, timeout=60)
    keys[label] = resp.json()["data"]["image_key"]

# Build card (simplified - expand with actual content)
card = {
    "config": {"wide_screen_mode": True},
    "header": {"title": {"tag": "plain_text", "content": "📡 本周 AI 要闻精选"},
               "template": "blue"},
    "elements": [
        {"tag": "img", "img_key": keys["cover"],
         "alt": {"tag": "plain_text", "content": "cover"}},
        {"tag": "div", "text": {"tag": "lark_md",
         "content": "**🔥 Article Title**\nDescription\n💡 *insight*"}},
        {"tag": "hr"},
        {"tag": "note", "elements": [{"tag": "plain_text",
         "content": "🤖 一人公司知识库 · 下周见"}]}
    ]
}

payload = {"msg_type": "interactive", "card": json.dumps(card, ensure_ascii=False)}
r = requests.post(webhook, json=payload, timeout=30)
print(f"Status: {r.status_code}, Response: {r.text[:200]}")
