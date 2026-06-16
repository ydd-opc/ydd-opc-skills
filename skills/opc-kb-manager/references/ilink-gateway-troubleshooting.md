# iLink Gateway Troubleshooting

## Rate Limit Recovery

### Key Finding (June 2026 — empirically verified)

**The iLink rate limit is tied to the WeChat user ID, NOT the iLink bot account.** Re-pairing with a new bot token does NOT resolve the issue. This was confirmed by:
1. Old bot `4caac71a` → rate limited
2. Full cleanup: removed `WEIXIN_TOKEN`, `WEIXIN_ACCOUNT_ID`, deleted all weixin account files
3. Fresh re-pair via QR code → new bot `bbb0fcb9`
4. Gateway connected with new bot ✅
5. First send attempt → still `rate limited` ❌
6. Conclusion: rate limit follows `o9cq80243XqLz2o1xHDnwUtk_iVs@im.wechat`, not the bot account

### Only Known Recovery Options

1. **Wait for natural expiration** — rate limit can last >48h. Do NOT keep testing, each retry resets the cooldown.
2. **Contact Tencent iLink support** via https://chatbot.weixin.qq.com
3. **Configure a backup channel** — Telegram or Email via `hermes gateway setup`
4. **Deliver via CLI** — cron jobs run normally and produce content locally

### Re-pairing Procedure (for reference, but ineffective for rate limit)

If a new WeChat user needs to be paired:

1. Kill existing gateway: `taskkill /f /im pythonw.exe`
2. Clear old config: `rm -rf D:/soft/hermes/weixin/`
3. Remove WEIXIN_* vars from both `D:/soft/hermes/.env` and `D:/soft/hermes/profiles/librarian/.env`
4. Auto-navigate the interactive setup:
   ```bash
   printf "12\ny\n\n" | timeout 120 hermes gateway setup 2>&1 | grep -oP 'https://liteapp[^\s"]+'
   ```
5. Present the QR URL to user IMMEDIATELY — it expires in ~2-3 minutes
6. Terminal can't render QR image (missing `qrcode` Python module) — URL only

## Gateway Process Management

### Check if gateway is alive
```bash
tasklist | grep pythonw
```
Expected: a process showing `pythonw.exe -m hermes_cli.main gateway run`

### Force-restart gateway
```bash
hermes gateway run --replace
```

### Verify connection
```bash
tail -5 D:/soft/hermes/logs/gateway.log
```
Expected: `✓ weixin connected` with recent timestamp

## Auto-Restart Setup

`Hermes_WakeUp` (WakeToRun=True, 08:55 daily) wakes the computer.
`Hermes_Gateway_Starter` (08:55 daily) starts `pythonw.exe -m hermes_cli.main gateway run`.
Together they ensure the gateway is alive when the 09:00 cron fires.

## Flow to Re-pair WeChat Account

### Step 1: Clear old WeChat config
```bash
# Kill the gateway
taskkill /f /im pythonw.exe 2>/dev/null
# Remove account files
rm -rf D:/soft/hermes/weixin/
rm -f D:/soft/hermes/gateway.lock
# Remove WeChat env vars from both configs
grep -v "WEIXIN_" D:/soft/hermes/.env > /tmp/h.env && mv /tmp/h.env D:/soft/hermes/.env
grep -v "WEIXIN_" D:/soft/hermes/profiles/librarian/.env > /tmp/l.env && mv /tmp/l.env D:/soft/hermes/profiles/librarian/.env
```

### Step 2: Generate QR code (non-interactive)
```bash
printf "12\ny\n\n" | timeout 120 hermes gateway setup 2>&1 | grep -oP 'https://liteapp[^\s"]+'
```
This auto-selects WeChat (12), answers "yes" to reconfigure, and confirms QR login.

### Step 3: Present to user
The URL expires in 2-3 minutes. Show it immediately and ask user to open with WeChat.

### Step 4: Verify
After user scans, check that a new `*.json` file appears in `D:/soft/hermes/weixin/accounts/` with a new account ID (not the old `4caac71a`).

### Step 5: Restart gateway
```bash
hermes gateway run --replace
```

### Step 6: Test
```bash
hermes send --to weixin "测试消息"
```
If still `rate limited`, the limit follows the WeChat user ID, not the bot account. Re-pairing won't help.

## Important Notes

- Gateway `start` and `stop` commands produce harmless UnicodeDecodeError tracebacks from worker threads — ignore them if the log shows `✓ weixin connected`
- The `hermes pairing list` command shows no pairing data — that's normal for iLink-based pairing
- Monthly quota is 1000 AI calls (free tier) — we used only 13 in June 2026
- The rate limit is NOT the monthly quota being exhausted
