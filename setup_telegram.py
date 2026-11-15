"""Run once: python setup_telegram.py  -> finds your chat id and sends a test message."""
import json, urllib.request, urllib.parse

token = input("Paste the bot token from @BotFather: ").strip()
input("Now open your bot in Telegram, press Start / send it 'hi', then press Enter here...")
api = f"https://api.telegram.org/bot{token}/"
updates = json.load(urllib.request.urlopen(api + "getUpdates"))["result"]
chats = [u["message"]["chat"]["id"] for u in updates if "message" in u]
if not chats:
    raise SystemExit("No message found. Send the bot a message and run again.")
chat = chats[-1]
urllib.request.urlopen(api + "sendMessage", urllib.parse.urlencode(
    {"chat_id": chat, "text": "✅ deal-hunter connected. Deals will arrive here."}).encode())
print(f"\nWorks! Add these two GitHub secrets:\n  TG_TOKEN   = {token}\n  TG_CHAT_ID = {chat}")
