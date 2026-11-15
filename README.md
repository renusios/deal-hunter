# deal-hunter

Checks ss.lv + pp.lv every ~10 min and sends cheap or repairable consoles/tech to Telegram. Runs free on GitHub Actions.

## Setup (about 5 min, you do this part)
1. Telegram: message **@BotFather**, send `/newbot`, and copy the token.
2. Send your new bot any message, then open `https://api.telegram.org/bot<TOKEN>/getUpdates` and copy `chat.id`.
3. GitHub: make a **public** repo (public = unlimited free minutes) and upload this folder.
4. Repo → Settings → Secrets and variables → Actions: add `TG_TOKEN` and `TG_CHAT_ID`.
5. Actions tab → enable workflows → **hunt** → Run workflow. The first run only records the ads already up. After that you get pinged for new ones.

## Tuning: `config.json`
- `max_price`: ping if the price is at or under this (0 = only ping for broken items).
- `max_price_repair`: a higher limit for ads that mention broken/defekts/nestrādā/не работает/запчасти.
- `watch`: items with their own limits. Now: broken PS4 ≤ €60, retro consoles (PS1-3, PSP, Wii, GameCube, N64, Game Boy, DS…) ≤ €25 or ≤ €40 broken. Any other broken console ≤ €40.
- `must_match`: only ping if the ad contains one of these words (empty = anything).
- Add any ss.lv category: copy its URL and add `sell/rss/` at the end.
- pp.lv: `site: "pp"`, URL `https://apipub.pp.lv/lv/api_user/v1/categories/<id>/lots` (shops and services are skipped).

Test locally: `DRY_RUN=1 python hunt.py`
