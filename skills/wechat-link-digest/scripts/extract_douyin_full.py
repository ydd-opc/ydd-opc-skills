"""
抖音视频统一提取（Level 1 元数据 + Level 2 深度内容）
用法: python extract_douyin_full.py "https://v.douyin.com/xxxx/"
输出: JSON，status 为 success/partial/failed
"""
import asyncio, json, re, sys
from datetime import datetime

# ─── Level 1: Fast metadata extraction (no browser) ───
def extract_level1(url):
    """快速提取元数据（标题/作者/互动数据）"""
    import requests
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    
    resp = requests.get(url, headers=headers, allow_redirects=True, timeout=15)
    html = resp.text
    final_url = resp.url
    
    vid_match = re.search(r'/video/(\d+)', final_url)
    result = {
        "video_id": vid_match.group(1) if vid_match else "",
        "original_url": url,
        "final_url": final_url,
    }
    
    def extract_json(key):
        idx = html.find(key)
        if idx == -1: return None
        start = html.find('{', idx + len(key))
        if start == -1: return None
        depth = 0; in_string = False; escape_next = False
        for i in range(start, len(html)):
            c = html[i]
            if escape_next: escape_next = False; continue
            if c == '\\': escape_next = True; continue
            if c == '"': in_string = not in_string; continue
            if in_string: continue
            if c == '{': depth += 1
            elif c == '}': depth -= 1
            if depth == 0: return html[start:i+1]
        return None
    
    for key in ['"videoInfoRes"', 'videoInfoRes']:
        raw = extract_json(key)
        if raw:
            try:
                data = json.loads(raw)
                items = data.get("item_list", [])
                if items:
                    item = items[0]; author = item.get("author", {}); stats = item.get("statistics", {})
                    result.update({
                        "title": item.get("desc", ""),
                        "author": author.get("nickname", ""),
                        "author_id": author.get("unique_id", "") or author.get("short_id", ""),
                        "create_time": datetime.fromtimestamp(item.get("create_time", 0)).strftime("%Y-%m-%d %H:%M") if item.get("create_time") else "",
                        "likes": stats.get("digg_count", 0),
                        "comments": stats.get("comment_count", 0),
                        "shares": stats.get("share_count", 0),
                    })
                    text_extra = item.get("text_extra", [])
                    result["hashtags"] = [t.get("hashtag_name", "") for t in text_extra if "hashtag_name" in t]
                    return result
            except json.JSONDecodeError: pass
    
    return result

# ─── Level 2: Deep content with Playwright ───
async def extract_level2(url):
    from playwright.async_api import async_playwright
    result = {"video_text": "", "description": "", "status": "pending"}
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
                viewport={"width": 390, "height": 844}, locale="zh-CN")
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(4000)
            all_text = await page.evaluate("""() => {
                const seen = new Set(); const texts = [];
                const skip = new Set(['SCRIPT', 'STYLE', 'NAV', 'HEADER', 'FOOTER', 'BUTTON']);
                const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                let node; while (node = walker.nextNode()) {
                    if (skip.has(node.parentElement?.tagName)) continue;
                    const t = node.textContent?.trim();
                    if (t && t.length > 3 && !seen.has(t)) { seen.add(t); texts.push(t); }
                }
                return texts;
            }""")
            if all_text: result["video_text"] = "\n".join(all_text[:50])
            result["status"] = "success"
            await browser.close()
    except Exception as e:
        result["status"] = "failed"; result["error"] = str(e)[:300]
    return result

def extract_full(url):
    result = {"platform": "douyin", "original_url": url, "status": "pending"}
    try:
        l1 = extract_level1(url)
        result.update(l1)
        result["status"] = "success" if result.get("title") else "partial"
    except Exception as e:
        result["status"] = "failed"; result["error"] = str(e)[:300]
        return result
    if result["status"] in ("success", "partial"):
        try:
            l2 = asyncio.run(extract_level2(url))
            if l2.get("video_text"): result["video_text"] = l2["video_text"]
            if l2.get("status") == "failed": result["level2_error"] = l2.get("error", "")
        except Exception as e: result["level2_error"] = str(e)[:300]
    return result

if __name__ == "__main__":
    print(json.dumps(extract_full(sys.argv[1]), ensure_ascii=False, indent=2))
