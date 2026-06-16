"""选题策略推送 v2 — 飞书卡片消息，表格布局
直接从 md 读取选题管线 → 推送到飞书群
无需 tenant_access_token，直接用 Webhook URL 发送 interactive 卡片。

用法:
    from scripts.topic_picker import pick_and_push
    pick_and_push()  # 读取选题管线.md → 自动推荐 → 推送飞书

环境变量:
    FEISHU_WEBHOOK  (必须，飞书机器人 Webhook URL)
    FEISHU_APP_ID   (用于获取 token，备用)
    FEISHU_APP_SECRET (用于获取 token，备用)
    
注意:
    send_card() 只用 WEBHOOK_URL，不需要 token。
    APP_ID/APP_SECRET 保留是为了向后兼容。
"""
import requests, json, os, sys
from datetime import datetime

ENV_PATH = r"D:\soft\hermes\profiles\librarian\.env"
PIPELINE_PATH = r"D:\opc-workdown\strategy\选题管线.md"


def _load_env():
    """从 librarian profile 读取飞书环境变量"""
    env_vars = {}
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env_vars[k.strip()] = v.strip()
    return env_vars


def read_pipeline():
    """读取 md 管线文件，返回结构化数据"""
    if not os.path.exists(PIPELINE_PATH):
        return None, "选题管线.md 不存在"
    
    with open(PIPELINE_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    sections = {"p0": [], "p1": [], "p2": [], "published": []}
    current = None
    
    for line in content.split("\n"):
        if line.startswith("## P0"):
            current = "p0"
        elif line.startswith("## P1"):
            current = "p1"
        elif line.startswith("## P2"):
            current = "p2"
        elif line.startswith("## ✅"):
            current = "published"
        elif current and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            first = cells[0] if cells else ""
            if first in ("#", "日期"):
                continue
            if all(c.replace("-", "").replace(":", "").strip() == "" for c in cells):
                continue
            sections[current].append(cells)
    
    return sections, None


def _parse(cells):
    """从表格行提取选题信息"""
    if len(cells) < 3:
        return None
    return {
        "title": cells[1].strip() if len(cells) > 1 else "",
        "type": cells[2].strip() if len(cells) > 2 else "",
        "score": cells[3].strip() if len(cells) > 3 else "",
        "note": cells[5].strip() if len(cells) > 5 else "",
    }


def build_card(sections):
    """构建飞书 interactive 卡片"""
    now = datetime.now().strftime("%m/%d")
    p0 = sections.get("p0", [])
    p1 = sections.get("p1", [])
    published = sections.get("published", [])
    
    elements = []
    
    # P0 推荐
    if p0:
        first = _parse(p0[0])
        if first:
            elements.append({
                "tag": "div",
                "fields": [
                    {"is_short": True, "text": {"tag": "lark_md",
                        "content": "**🎯 选题**\n" + first['title']}},
                    {"is_short": True, "text": {"tag": "lark_md",
                        "content": "**⭐ 冷启动**\n" + first['score']}},
                ]
            })
            elements.append({
                "tag": "div",
                "fields": [
                    {"is_short": True, "text": {"tag": "lark_md",
                        "content": "**📂 类型**\n" + first['type']}},
                    {"is_short": True, "text": {"tag": "lark_md",
                        "content": "**📎 备注**\n" + first['note']}},
                ]
            })
    
    elements.append({"tag": "hr"})
    
    # 管线一览
    pipe_lines = []
    for label, items in [("P0（优先写）", p0), ("P1（本周待排）", p1)]:
        entry_list = []
        for c in items:
            t = _parse(c)
            if t:
                short = t['title'][:20] + ".." if len(t['title']) > 20 else t['title']
                entry_list.append("`" + t['score'] + "` " + short)
        if entry_list:
            pipe_lines.append("**" + label + "**\n" + "\n".join(entry_list))
    
    if pipe_lines:
        elements.append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": "\n\n".join(pipe_lines)}
        })
        elements.append({"tag": "hr"})
    
    # 最近发布
    if published:
        items = []
        for c in published[-3:]:
            t = _parse(c)
            if t:
                items.append("`" + t['type'] + "` " + t['title'][:25])
        if items:
            elements.append({
                "tag": "div",
                "text": {"tag": "lark_md",
                    "content": "**📅 最近发布**\n" + "\n".join(items)}
            })
            elements.append({"tag": "hr"})
    
    elements.append({
        "tag": "note",
        "elements": [{"tag": "plain_text", "content": "回复「开写」我就开始写"}]
    })
    
    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "📋 选题推荐 | " + now},
                "template": "blue"
            },
            "elements": elements
        }
    }


def send_card(card, webhook_url=None):
    """发送卡片消息到飞书（直接用 Webhook URL，不需要 token）"""
    if webhook_url is None:
        env = _load_env()
        webhook_url = env.get("FEISHU_WEBHOOK", "")
    if not webhook_url:
        print("❌ 缺少 FEISHU_WEBHOOK")
        return False
    r = requests.post(webhook_url, json=card, timeout=15)
    result = r.json()
    ok = result.get("code") == 0
    print("✅ 推送成功" if ok else "❌ 推送失败: " + result.get("msg", r.text))
    return ok


def pick_and_push(webhook_url=None):
    """
    主入口：读取管线 → 推荐选题 → 推送到飞书
    可在 cron 中直接调用。
    """
    print("读取选题管线...")
    sections, err = read_pipeline()
    if err:
        print(err)
        return False
    
    print(f"  P0: {len(sections['p0'])} 条, "
          f"P1: {len(sections['p1'])} 条, "
          f"已发布: {len(sections['published'])} 条")
    
    card = build_card(sections)
    print("推送至飞书...")
    return send_card(card, webhook_url)


if __name__ == "__main__":
    pick_and_push()
