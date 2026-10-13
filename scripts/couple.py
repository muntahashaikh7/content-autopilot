#!/usr/bin/env python3
"""Couple Reels lane — trend watch + story brief (reverse-engineered-prompt method).
Free sources only. Never fails the run."""
import os, sys, re, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (news_rss, seasonal, load_state, save_state, not_used_recently,
                    mark_used, day_dir, write_text, write_json, ROOT)

FORMULAS = ["F1 romantic-sweet", "F2 funny-domestic", "F3 comedy-exaggeration", "F4 angry-sweet"]

def parse_tropes():
    text = open(os.path.join(ROOT, "bank", "couple-tropes.md"), encoding="utf-8").read()
    tropes = []
    for m in re.finditer(r"^(\d+)\.\s+([\w-]+):\s*(.+)$", text, re.M):
        tropes.append({"key": m.group(2), "desc": m.group(3).strip()})
    return tropes

def parse_kw_pools():
    text = open(os.path.join(ROOT, "bank", "couple-tropes.md"), encoding="utf-8").read()
    pools = {}
    for m in re.finditer(r"^-\s+(base|romantic|domestic):\s*(.+)$", text, re.M):
        pools[m.group(1)] = [k.strip() for k in m.group(2).split(",")]
    return pools

def research():
    today = datetime.date.today()
    return {
        "date": today.isoformat(),
        "news_ai_couple_reels": news_rss("ai couple reels viral"),
        "news_couple_comedy": news_rss("couple comedy reels trend"),
        "news_short_drama": news_rss("married couple funny skit"),
        "seasonal_next_60d": seasonal(today),
        "note": "Free sources only. _err = source failed, skipped gracefully. IG model pages need login — checked on main runtime, not here.",
    }

def build_brief(trope, formula, trends):
    key, desc = trope["key"], trope["desc"]
    title = key.replace("-", " ").title()
    # Reverse-engineered-prompt skeleton: shot-by-shot mechanics, original replica
    replica_prompt = f"""[REPLICA PROMPT SKELETON — fill with video tool, keep characters locked]
Characters: Zayn (husband), Mira (wife), baby Abeer, kitten Pip. Cinematic photorealistic 3D, same face/outfit, zero drift.
Trope: {key} — {desc}
Formula: {formula}
SHOT 1 (hook, 0-1s): exaggerated frame-1 gag OR bold visual claim — must stop scroll.
SHOTS 2-4 (beats): 3-step escalation, each beat bigger than last. Camera: punchy cuts, close-ups on reactions.
DIALOGUE RHYTHM: short banter lines, tone-flip on beat 3 (mock outrage -> melt).
PAYOFF (last 2s): visual gag + reaction close-up (eye-pop / facepalm / smug wink).
REACTION BUTTON: Pip copies the emotion (crossed-paws angry / clapping / smug).
Audio: trending comedy bed or dialogue-driven per formula. 9:16 vertical.
DO NOT copy any creator's reel verbatim — original dialogue, our characters, same mechanics."""

    yt_title = f"{title} 😂 | Zayn & Mira Couple Comedy"
    yt_desc = (f"{title} — Zayn & Mira ki nayi funny short! {desc} "
               f"Watch till the end for the twist. New couple comedy shorts daily.\n\n"
               f"#couplecomedy #funnyreels #aianimation")
    yt_tags = ["couple comedy", "funny reels", "ai cartoon", "zayn and mira",
               "married life humor", "desi couple comedy", "short drama",
               "relatable couple", "comedy skit", "cute animation",
               "husband wife funny", "daily shorts", "viral reels",
               key.replace("-", " "), formula.split()[1] + " comedy"]
    return {
        "trope": key, "formula": formula, "title": title,
        "hook": "First 1s: exaggerated frame-1 gag — " + desc.split("—")[0].strip(),
        "beats": ["Beat 1: setup — everyday moment", "Beat 2: escalation — bigger attempt/fail",
                  "Beat 3: tone-flip — mock outrage or surprise twist"],
        "dialogue_rhythm": "Short banter, 1-2 lines per beat, punchline on payoff.",
        "payoff": "Visual gag + reaction close-up (eye-pop / facepalm / smug wink).",
        "reaction_button": "Pip mirrors the emotion.",
        "replica_prompt": replica_prompt,
        "yt_title": yt_title, "yt_desc": yt_desc, "yt_tags": yt_tags[:15],
    }

def captions(brief, pools):
    formula = brief["formula"]
    pool = list(pools.get("base", []))
    if "romantic" in formula:
        pool += pools.get("romantic", [])
    else:
        pool += pools.get("domestic", [])
    # dedupe, keep 8-12
    seen, kws = set(), []
    for k in pool:
        if k not in seen:
            seen.add(k); kws.append(k)
    kws = kws[:12]
    ig = (f"{brief['title']} 😂\nZayn vs Mira — round {brief['trope'].replace('-', ' ')}! "
          f"Watch till the end 👀\n\n[{', '.join(kws)}]")
    threads = f"{brief['title']} 😂 — Zayn & Mira. Full short on YouTube/IG. [{', '.join(kws[:6])}]"
    return {"ig_caption": ig, "ig_keywords": kws, "threads_text": threads,
            "note": "IG: keyword block only, NO hashtags (standing law)."}

def main():
    d = day_dir()
    trends = research()
    write_json(os.path.join(d, "couple-trends.json"), trends)

    tropes = parse_tropes()
    state = load_state("couple")
    # formula rotation: least recently used
    counts = {}
    for u in state.get("used", []):
        counts[u.get("formula", "")] = counts.get(u.get("formula", ""), 0) + 1
    formula = min(FORMULAS, key=lambda f: counts.get(f, 0))

    trope = next((t for t in tropes if not_used_recently(state, t["key"])), tropes[0] if tropes else {"key": "cake-share", "desc": "food-share skit"})
    pools = parse_kw_pools()
    brief = build_brief(trope, formula, trends)
    brief["captions"] = captions(brief, pools)
    brief["trend_snapshot"] = {
        "news_hits": len([t for t in trends["news_ai_couple_reels"] if not t.startswith("_err")]),
        "seasonal": [e["event"] for e in trends["seasonal_next_60d"][:3]],
    }
    write_json(os.path.join(d, "couple-brief.json"), brief)

    md = f"""# Couple Reel Brief — {datetime.date.today().isoformat()}

**Trope:** {brief['trope']} | **Formula:** {brief['formula']} | **Title:** {brief['title']}

## Reverse-engineered-prompt method
Shot-by-shot mechanics neeche — video tool me ORIGINAL replica banao (verbatim copy kabhi nahi).

## Hook (0-1s)
{brief['hook']}

## Beats
- {brief['beats'][0]}
- {brief['beats'][1]}
- {brief['beats'][2]}

## Dialogue rhythm
{brief['dialogue_rhythm']}

## Payoff
{brief['payoff']}

## Reaction button
{brief['reaction_button']}

## Replica prompt skeleton (video tool ke liye)
```
{brief['replica_prompt']}
```

## YouTube
**Title:** {brief['yt_title']}
**Description:** {brief['yt_desc']}
**Tags (15):** {', '.join(brief['yt_tags'])}

## Instagram (keyword block, NO hashtags)
{brief['captions']['ig_caption']}

## Threads
{brief['captions']['threads_text']}

## Trend snapshot
News hits: {brief['trend_snapshot']['news_hits']} | Seasonal: {', '.join(brief['trend_snapshot']['seasonal']) or 'none'}
"""
    write_text(os.path.join(d, "couple-brief.md"), md)
    mark_used(state, trope["key"])
    state.setdefault("used", [])[-1]["formula"] = formula
    save_state("couple", state)
    print(json.dumps({"trope": trope["key"], "formula": formula}))

if __name__ == "__main__":
    main()
