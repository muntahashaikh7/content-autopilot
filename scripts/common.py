#!/usr/bin/env python3
"""Shared helpers — free sources, graceful degradation, never fails the run."""
import json, os, re, datetime, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "Mozilla/5.0 (MJS-Content-Autopilot/1.0)"}

def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")

def news_rss(query, limit=15):
    """Google News RSS — free, no key. Returns [titles] or ['_err:...'] on failure."""
    try:
        q = urllib.parse.quote(query)
        raw = get(f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en")
        titles = re.findall(r"<title>(.*?)</title>", raw)
        out = []
        for t in titles[1:limit + 1]:
            t = re.sub(r"<[^>]+>", "", t).strip().lower()
            if t:
                out.append(t)
        return out
    except Exception as e:
        return [f"_err:{type(e).__name__}"]

def seasonal(today, max_days=60):
    try:
        cal = json.load(open(os.path.join(ROOT, "config", "seasonal-calendar.json")))
    except Exception:
        return []
    near = []
    for ev in cal.get("events", []):
        for key in ("date_2026", "date_2027"):
            d = ev.get(key)
            if not d:
                continue
            try:
                dt = datetime.date.fromisoformat(d)
            except ValueError:
                continue
            delta = (dt - today).days
            if 0 <= delta <= max_days:
                near.append({"event": ev["name"], "date": d, "in_days": delta,
                             "keywords": ev.get("keywords", [])})
                break
    near.sort(key=lambda x: x["in_days"])
    return near

def load_state(name):
    p = os.path.join(ROOT, "state", name + ".json")
    try:
        return json.load(open(p))
    except Exception:
        return {"used": []}

def save_state(name, state):
    p = os.path.join(ROOT, "state", name + ".json")
    json.dump(state, open(p, "w"), indent=1)

def not_used_recently(state, key, days=30):
    today = datetime.date.today()
    for u in state.get("used", []):
        if u.get("key") == key:
            try:
                if (today - datetime.date.fromisoformat(u["date"])).days < days:
                    return False
            except ValueError:
                pass
    return True

def mark_used(state, key):
    state.setdefault("used", []).append({"date": datetime.date.today().isoformat(), "key": key})
    # keep last 200 to bound file size
    state["used"] = state["used"][-200:]

def day_dir():
    d = os.path.join(ROOT, "daily", datetime.date.today().isoformat())
    os.makedirs(d, exist_ok=True)
    return d

def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)

def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
