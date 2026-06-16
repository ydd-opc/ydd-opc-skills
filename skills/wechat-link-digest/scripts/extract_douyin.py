"""
抖音视频快速提取（Level 1 only, no browser）
用法: python extract_douyin.py "https://v.douyin.com/xxxx/"
"""
import requests, re, json, sys
from datetime import datetime

url = sys.argv[1]
headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
resp = requests.get(url, headers=headers, allow_redirects=True, timeout=15)
html = resp.text
vid = re.search(r'/video/(\d+)', resp.url)
result = {"video_id": vid.group(1) if vid else "", "original_url": url}

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
        except json.JSONDecodeError: pass

if not result.get("title"):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    desc_meta = soup.find('meta', attrs={'name': 'description'})
    title_tag = soup.find('title')
    title_text = title_tag.string.strip() if title_tag and title_tag.string else ""
    title_text = re.sub(r'\s*[-–—]\s*抖音\s*$', '', title_text)
    result["title"] = title_text
    if desc_meta:
        m = re.search(r'(\S+?)于\d{8}发布在抖音', desc_meta.get('content', ''))
        if m: result["author"] = m.group(1)

print(json.dumps(result, ensure_ascii=False, indent=2))
