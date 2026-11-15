"""Run once: python setup_telegram.py
Finds your chat id, sends a test message, saves both as GitHub secrets and starts the bot."""
import json, subprocess, urllib.request, urllib.parse

GH = r"C:\Program Files\GitHub CLI\gh.exe"
token = input("Paste the bot token from @BotFather: ").strip()
input("Now open your bot in Telegram, press Start / send it 'hi', then press Enter here...")
api = f"https://api.telegram.org/bot{token}/"
updates = json.load(urllib.request.urlopen(api + "getUpdates"))["result"]
chats = [u["message"]["chat"]["id"] for u in updates if "message" in u]
if not chats:
    raise SystemExit("No message found. Send the bot a message and run again.")
chat = str(chats[-1])
urllib.request.urlopen(api + "sendMessage", urllib.parse.urlencode(
    {"chat_id": chat, "text": "✅ deal-hunter connected. Deals will arrive here."}).encode())
for name, val in (("TG_TOKEN", token), ("TG_CHAT_ID", chat)):
    subprocess.run([GH, "secret", "set", name, "--body", val], check=True)
subprocess.run([GH, "workflow", "enable", "hunt.yml"], check=True)
subprocess.run([GH, "workflow", "run", "hunt.yml"], check=True)
print("\nDone. Bot is live: first run records current ads, then new deals ping you.")
