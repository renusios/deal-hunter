"""Run once (double-click SETUP.bat). Finds your chat id, sends a test message,
saves both as GitHub secrets and starts the bot. Errors go to setup_log.txt (token never logged)."""
import json, subprocess, time, traceback, urllib.request, urllib.parse

GH = r"C:\Program Files\GitHub CLI\gh.exe"


def step(msg):
    print(msg)
    open("setup_log.txt", "a", encoding="utf-8").write(msg + "\n")


try:
    open("setup_log.txt", "w").close()
    token = input("Paste the bot token from @BotFather and press Enter: ").strip()
    step(f"token received ({len(token)} chars, has colon: {':' in token})")
    api = f"https://api.telegram.org/bot{token}/"
    me = json.load(urllib.request.urlopen(api + "getMe"))["result"]
    step(f"token OK -> bot @{me['username']}")
    chat = None
    for _ in range(30):  # waits up to ~1 min for you to message the bot
        updates = json.load(urllib.request.urlopen(api + "getUpdates"))["result"]
        chats = [u["message"]["chat"]["id"] for u in updates if "message" in u]
        if chats:
            chat = str(chats[-1])
            break
        step(f"no message yet: open @{me['username']} in Telegram and send 'hi'...")
        time.sleep(2)
    if not chat:
        raise SystemExit("Still no message to the bot. Send it 'hi' and run SETUP.bat again.")
    step(f"chat found: {chat}")
    urllib.request.urlopen(api + "sendMessage", urllib.parse.urlencode(
        {"chat_id": chat, "text": "✅ deal-hunter connected. Deals will arrive here."}).encode())
    step("test message sent")
    for name, val in (("TG_TOKEN", token), ("TG_CHAT_ID", chat)):
        subprocess.run([GH, "secret", "set", name, "--body", val], check=True)
    step("GitHub secrets saved")
    subprocess.run([GH, "workflow", "enable", "hunt.yml"], check=True)
    subprocess.run([GH, "workflow", "run", "hunt.yml"], check=True)
    step("Done. Bot is live: first run records current ads, then new deals ping you.")
except SystemExit as e:
    step(str(e))
except Exception:
    step("ERROR:\n" + traceback.format_exc().replace(token if "token" in dir() and token else "\0", "<token>"))
