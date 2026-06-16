# Douyin Extraction Scripts

## Primary: `extract_douyin_full.py`

Locations (synced):
- Skill scripts: `scripts/extract_douyin_full.py` (portable, ships with skill)
- External: `D:\\opc-workdown\\extract_douyin_full.py`

Two-level extraction in one call:
- **L1 (fast)**: iPhone UA HTTP → bracket-count JSON extractor → title/author/stats
- **L2 (deep)**: Playwright headless Chromium → DOM text extraction → expanded description

Usage:
```bash
D:/opc-workdown/.venv/Scripts/python.exe D:/opc-workdown/extract_douyin_full.py "URL"
```

Output JSON fields: `status`, `title`, `author`, `author_id`, `author_signature`, `create_time`, `likes`, `comments`, `shares`, `hashtags`, `video_text`, `video_id`, `original_url`, `final_url`

## Fallback: `extract_douyin_playwright.py`

Location: `D:\opc-workdown\extract_douyin_playwright.py`

Pure Playwright approach. Use when `extract_douyin_full.py` L1 fails to get metadata. Slower (~15s).

## Legacy: `extract_douyin.py`

Location: `D:\opc-workdown\extract_douyin.py`

L1-only, no Playwright. Still useful for quick metadata checks. Superseded by `extract_douyin_full.py` for production use.

## Key Technical Details

### Bracket-counting JSON extractor (L1)
- Finds `videoInfoRes` key in HTML, then counts `{` and `}` to extract full nested JSON
- Avoids regex `re.DOTALL` which truncates on deeply nested objects
- Handles escaped strings and Unicode

### iPhone UA requirement
- `Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15`
- Without this, Douyin serves JS-only SPA with empty body
- With this, gets pre-rendered HTML with embedded `_ROUTER_DATA`

### Known Limitations
- **Video transcript/subtitles**: Douyin does NOT expose these via public API or DOM. Even Playwright cannot extract spoken content.
- **Articles (图文)**: Douyin articles use `_$jsvmprt` anti-bot protection. Not extractable without real browser automation (beyond current capability).
- **Short link resolution**: `v.douyin.com/XXX` redirects to `iesdouyin.com/share/video/ID/`. Must follow redirect to get video ID.
