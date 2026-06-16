"""
飞书富文本推送工具 — 上传图片 + 发送富文本消息
用于 Horizon 每周精选推送。用法：

    from scripts.feishu_push import push_to_feishu

    push_to_feishu(
        cover_path=r"D:\opc-workdown\outputs\weekly-cover-....png",
        body_path=r"D:\opc-workdown\outputs\weekly-body-....png",
        title="📰 本周 AI 要闻精选｜M月D日 - M月D日",
        content_lines=["🟣 速览\n...", "一、标题\n\n正文...\n\n💡 复盘..."],
        footer="📮 如果觉得 AI 资讯对您有用，帮忙点点关注点点赞。"
    )

环境变量（在 librarian profile 的 .env 中）:
    FEISHU_APP_ID=cli_xxx
    FEISHU_APP_SECRET=xxx
    FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
"""
import requests, os

def push_to_feishu(cover_path, body_path, title, content_lines, footer=""):
    app_id = os.environ.get("FEISHU_APP_ID", "")
    app_secret = os.environ.get("FEISHU_APP_SECRET", "")
    webhook = os.environ.get("FEISHU_WEBHOOK", "")
    if not all([app_id, app_secret, webhook]):
        print("❌ 缺少 FEISHU 环境变量")
        return False

    r = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret}, timeout=15)
    token = r.json()["tenant_access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    with open(cover_path, "rb") as f:
        r2 = requests.post("https://open.feishu.cn/open-apis/im/v1/images",
            headers=headers, files={"image": ("cover.png", f, "image/png"), "image_type": (None, "message")}, timeout=30)
    cover_key = r2.json()["data"]["image_key"]
    print(f"✅ Cover: {cover_key}")

    body_key = None
    if body_path and os.path.exists(body_path):
        with open(body_path, "rb") as f:
            r3 = requests.post("https://open.feishu.cn/open-apis/im/v1/images",
                headers=headers, files={"image": ("body.png", f, "image/png"), "image_type": (None, "message")}, timeout=30)
        body_key = r3.json()["data"]["image_key"]
        print(f"✅ Body: {body_key}")

    elements = [[{"tag": "img", "image_key": cover_key}]]
    elements.append([{"tag": "text", "text": "\n"}])
    for line in content_lines:
        elements.append([{"tag": "text", "text": line}])
    if body_key:
        elements.append([{"tag": "img", "image_key": body_key}])
        elements.append([{"tag": "text", "text": "\n"}])
    if footer:
        elements.append([{"tag": "text", "text": f"\n\n━━━━━━━━━━━━━━━━\n\n{footer}"}])

    payload = {"msg_type": "post", "content": {"post": {"zh_cn": {"title": title, "content": elements}}}}
    r4 = requests.post(webhook, json=payload, timeout=15)
    ok = r4.json().get("code") == 0
    print(f"{'✅' if ok else '❌'} Push: {r4.json().get('msg', r4.text)}")
    return ok
