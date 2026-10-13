#!/usr/bin/env python3
"""Nostalgia 3D World lane — trend watch + memory-topic brief.
Free sources only. Never fails the run."""
import os, sys, re, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (news_rss, seasonal, load_state, save_state, not_used_recently,
                    mark_used, day_dir, write_text, write_json, ROOT)

def parse_topics():
    text = open(os.path.join(ROOT, "bank", "nostalgia-memories.md"), encoding="utf-8").read()
    topics = []
    for m in re.finditer(r"^(\d+)\.\s+([\w-]+):\s*(.+)$", text, re.M):
        topics.append({"key": m.group(2), "desc": m.group(3).strip()})
    return topics

def parse_kw():
    text = open(os.path.join(ROOT, "bank", "nostalgia-memories.md"), encoding="utf-8").read()
    pools = {}
    for m in re.finditer(r"^-\s+(base|extra):\s*(.+)$", text, re.M):
        pools[m.group(1)] = [k.strip() for k in m.group(2).split(",")]
    return pools

def research():
    today = datetime.date.today()
    return {
        "date": today.isoformat(),
        "news_nostalgia": news_rss("90s nostalgia childhood memories"),
        "news_retro": news_rss("retro childhood trend reels"),
        "seasonal_next_60d": seasonal(today),
        "note": "Free sources only. _err = source failed, skipped gracefully.",
    }

def build_brief(topic, trends):
    key, desc = topic["key"], topic["desc"]
    title = key.replace("-", " ").title()
    yt_title = f"{title} 🕰️ | 90s Childhood Memories in 3D"
    yt_desc = (f"{title} — {desc} Kya tumhe bhi ye din yaad hain? "
               f"90s ki yaadein, 3D me zinda. Comment me apni yaad share karo!\n\n"
               f"#nostalgia #90s #childhoodmemories")
    yt_tags = ["90s nostalgia", "childhood memories", "desi nostalgia",
               "pakistan memories", "nostalgic 3d", "bachpan ki yaadein",
               "retro vibes", "old is gold", "memory lane", "90s kids",
               "nostalgia reels", "3d animation", "emotional short",
               key.replace("-", " "), "growing up desi"]
    keyword_comment = (f"🔑 {title} — {desc} "
                       f"Tumhe sab se zyada kya yaad aaya? Comment karo! 👇")
    pin_title = f"{title} — 90s Nostalgia 3D | Childhood Memories"
    pin_desc = f"{desc} Relive the 90s in beautiful 3D. #nostalgia #90s"
    return {
        "topic": key, "title": title, "sensory_hook": desc,
        "story_beat": ("0-2s: sensory trigger (" + desc.split(",")[0] + "). "
                       "2-10s: Nova & Prime ka chhota warm moment. "
                       "10-15s: soft smile payoff + 'tumhe bhi yaad hai?'"),
        "yt_title": yt_title, "yt_desc": yt_desc, "yt_tags": yt_tags[:15],
        "keyword_comment": keyword_comment,
        "pin_title": pin_title, "pin_desc": pin_desc,
    }

def main():
    d = day_dir()
    trends = research()
    write_json(os.path.join(d, "nostalgia-trends.json"), trends)

    topics = parse_topics()
    state = load_state("nostalgia")
    topic = next((t for t in topics if not_used_recently(state, t["key"])),
                 topics[0] if topics else {"key": "gully-cricket", "desc": "gali cricket"})
    pools = parse_kw()
    kws = []
    for k in pools.get("base", []) + pools.get("extra", []):
        if k not in kws:
            kws.append(k)
    kws = kws[:12]

    brief = build_brief(topic, trends)
    ig = (f"{brief['title']} 🕰️\n{brief['sensory_hook']}\n"
          f"Tumhe bhi yaad hai? Comment me batao 👇\n\n[{', '.join(kws)}]")
    brief["ig_caption"] = ig
    brief["ig_keywords"] = kws
    brief["trend_snapshot"] = {
        "news_hits": len([t for t in trends["news_nostalgia"] if not t.startswith("_err")]),
        "seasonal": [e["event"] for e in trends["seasonal_next_60d"][:3]],
    }
    write_json(os.path.join(d, "nostalgia-brief.json"), brief)

    md = f"""# Nostalgia 3D Brief — {datetime.date.today().isoformat()}

**Topic:** {brief['topic']} | **Title:** {brief['title']}

## Relatable-memory mechanics
- **Sensory hook (0-2s):** {brief['sensory_hook']}
- **Story:** {brief['story_beat']}
- **Characters:** Nova (male hero) + Prime (female lead) — same design, zero drift

## YouTube
**Title:** {brief['yt_title']}
**Description:** {brief['yt_desc']}
**Tags (15):** {', '.join(brief['yt_tags'])}

## Keyword comment (post + pin)
{brief['keyword_comment']}

## Instagram (keyword block, NO hashtags)
{brief['ig_caption']}

## Pinterest pin
**Title:** {brief['pin_title']}
**Description:** {brief['pin_desc']}

## Trend snapshot
News hits: {brief['trend_snapshot']['news_hits']} | Seasonal: {', '.join(brief['trend_snapshot']['seasonal']) or 'none'}
"""
    write_text(os.path.join(d, "nostalgia-brief.md"), md)
    mark_used(state, topic["key"])
    save_state("nostalgia", state)
    print(json.dumps({"topic": topic["key"]}))

if __name__ == "__main__":
    main()
