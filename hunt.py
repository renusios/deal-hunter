"""Checks marketplace feeds and sends cheap/repairable deals to Telegram.
Env: TG_TOKEN, TG_CHAT_ID. DRY_RUN=1 prints instead of sending."""
import json, os, re, sys, html, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SEEN_FILE = os.path.join(HERE, "seen.json")
UA = {"User-Agent": "Mozilla/5.0 (deal-hunter)"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read()


def parse_ss(feed_xml):
    for item in ET.fromstring(feed_xml).iter("item"):
        desc = item.findtext("description") or ""
        img = re.search(r'src="([^"]+)"', desc)
        fields = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", desc.split("Apskatīt")[0]))).strip()
        price = re.search(r"Cena: ([\d ,]+)", fields)
        yield {
            "id": item.findtext("link"),
            "url": item.findtext("link"),
            "title": html.unescape(item.findtext("title") or "").strip(),
            "details": fields,
            "price": float(re.sub(r"\D", "", price.group(1))) if price else None,
            "img": img.group(1).replace(".t.jpg", ".800.jpg") if img else None,
        }


def parse_pp(raw):
    for a in json.loads(raw)["content"]["data"]:
        if a.get("xmlImported") or a.get("company") or a["action"]["name"] != "Pārdod":
            continue  # skip shops and "buying" ads
        prices = [float(p["value"]) for p in a.get("prices", []) if p.get("value")]
        title = re.sub(r"\s+", " ", a.get("title", "")).strip()
        yield {
            "id": a["frontUrl"],
            "url": a["frontUrl"],
            "title": title[:200],
            "details": f"{a.get('publicLocation', {}).get('region', {}).get('name', '')}",
            "price": prices[0] if prices else None,
            "img": None,
        }


PARSERS = {"ss": parse_ss, "pp": parse_pp}


def matches(ad, feed, cfg):
    text = (ad["title"] + " " + ad["details"]).lower()
    if any(w in text for w in cfg["skip_words"]):
        return None
    if feed["must_match"] and not any(w in text for w in feed["must_match"]):
        return None
    clean = text
    for w in cfg["not_repair"]:  # "nav bojāts" = NOT broken
        clean = clean.replace(w, "")
    repair = any(w in clean for w in cfg["repair_words"])
    limit = feed["max_price_repair"] if repair else feed["max_price"]
    tag = "🔧 REPAIRABLE" if repair else "💸 CHEAP"
    for w in cfg.get("watch", []):  # items you want with their own higher limits
        if any(k in text for k in w["words"]):
            wl = w["max_price_repair"] if repair else w["max_price"]
            if wl > limit:
                limit, tag = wl, f"🎯 {w['name']} " + tag
    if ad["price"] is None or ad["price"] > limit:
        return None
    return tag


def send(ad, feed, tag):
    caption = (f"{tag} · {feed['name']} · <b>{ad['price']:g} €</b>\n"
               f"{html.escape(ad['title'][:300])}\n{html.escape(ad['details'][:200])}\n{ad['url']}")
    if os.environ.get("DRY_RUN"):
        print(caption, "\n")
        return
    token, chat = os.environ["TG_TOKEN"], os.environ["TG_CHAT_ID"]
    method, data = ("sendPhoto", {"photo": ad["img"], "caption": caption}) if ad["img"] \
        else ("sendMessage", {"text": caption})
    data.update(chat_id=chat, parse_mode="HTML")
    try:
        urllib.request.urlopen(f"https://api.telegram.org/bot{token}/{method}",
                               urllib.parse.urlencode(data).encode(), timeout=30)
    except Exception:  # photo failed -> plain text
        urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage",
                               urllib.parse.urlencode({"chat_id": chat, "text": caption,
                                                       "parse_mode": "HTML"}).encode(), timeout=30)


def main():
    cfg = json.load(open(os.path.join(HERE, "config.json"), encoding="utf-8"))
    seen = json.load(open(SEEN_FILE)) if os.path.exists(SEEN_FILE) else {}
    for feed in cfg["feeds"]:
        try:
            ads = list(PARSERS[feed.get("site", "ss")](get(feed["url"])))
        except Exception as e:
            print(f"{feed['name']}: fetch failed: {e}", file=sys.stderr)
            continue
        first_run = feed["name"] not in seen and not os.environ.get("DRY_RUN")
        old = set(seen.get(feed["name"], []))
        hits = 0
        for ad in ads:
            if ad["id"] in old:
                continue
            tag = matches(ad, feed, cfg)
            if tag and not first_run:  # first run only records what exists, no spam
                send(ad, feed, tag)
                hits += 1
        seen[feed["name"]] = ([a["id"] for a in ads] + list(old))[:500]
        print(f"{feed['name']}: {len(ads)} ads, {hits} sent{' (first run, seeded)' if first_run else ''}")
    json.dump(seen, open(SEEN_FILE, "w"), indent=0)


if __name__ == "__main__":
    main()
