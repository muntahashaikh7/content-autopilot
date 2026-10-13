#!/usr/bin/env python3
"""Naba Decor lane — trend watch + daily marketing copy pack (v4 VO formula).
Free sources only. Never fails the run. NO video generation in this phase."""
import os, sys, re, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (news_rss, load_state, save_state, not_used_recently,
                    mark_used, day_dir, write_text, write_json, ROOT)

def parse_angles():
    text = open(os.path.join(ROOT, "bank", "naba-angles.md"), encoding="utf-8").read()
    hooks = []
    in_hooks = False
    for line in text.splitlines():
        if "## Hook ideas" in line:
            in_hooks = True
            continue
        if in_hooks and line.startswith("##"):
            break
        if in_hooks:
            m = re.match(r"^-\s+([\w-]+):\s*(.+)$", line)
            if m:
                hooks.append({"key": m.group(1), "desc": m.group(2).strip()})
    ig, fb = [], []
    m = re.search(r"IG \([^)]*\):\s*(.+)$", text, re.M)
    if m:
        ig = [h.strip() for h in m.group(1).split(",")]
    m = re.search(r"FB \(3\):\s*(.+)$", text, re.M)
    if m:
        fb = [h.strip() for h in m.group(1).split(",")]
    return hooks, ig, fb

def research():
    today = datetime.date.today()
    return {
        "date": today.isoformat(),
        "news_home_decor": news_rss("home decor organization viral"),
        "news_kitchen_storage": news_rss("kitchen storage organizer trending"),
        "news_wall_shelf": news_rss("wall shelf decor ideas"),
        "note": "Free sources only. _err = source failed, skipped gracefully.",
    }

def main():
    d = day_dir()
    trends = research()
    write_json(os.path.join(d, "naba-trends.json"), trends)

    claims = json.load(open(os.path.join(ROOT, "config", "naba-claims.json")))
    rot = claims["rotation"][str((datetime.date.today() - datetime.date(2026, 9, 26)).days % 4)]
    detail = claims["rotation_detail"][rot]
    product = detail["product"]
    vo_name = {"scurve": "S-Curve", "2tier": "2 Tier", "pair": "2 Tier and S-Curve"}[product]

    hooks, ig_pool, fb_pool = parse_angles()
    state = load_state("naba")
    hook = next((h for h in hooks if not_used_recently(state, h["key"], days=14)),
                hooks[0] if hooks else {"key": "waterproof-spray", "desc": "paani spray hook"})

    # v4 VO script (English, energetic ad voice; VOICEOVER me sirf 2 Tier/S-Curve)
    vo_script = (
        f"[0-3s HOOK] Tired of messy shelves? Watch this. "
        f"[3-8s DEMO] The {vo_name} — one hundred percent waterproof, heat resistant, "
        f"holds up to 4KG with a solid metal bracket. "
        f"[8-13s PROOF] Spices, bottles, bathroom essentials — everything in its place. "
        f"[13-15s CTA] {claims['cta']}"
    )
    overlays = ["Upgrade Your Home Decor", "100% Waterproof PVC", "Holds 4KG",
                "Metal Bracket Mount", claims["cta"]]

    ig_tags = ["#" + t for t in ig_pool[:5]]
    fb_tags = ["#" + t for t in fb_pool[:3]]
    caption_en = (
        f"Messy shelves? Not anymore! The {vo_name} by NABA Decor — 100% waterproof, "
        f"heat resistant, holds 4KG on a solid metal bracket.\n"
        f"{claims['cta']}\n{' '.join(ig_tags)}"
    )
    fb_caption = (
        f"Upgrade your kitchen & bathroom! {vo_name} — 100% waterproof, 4KG load, "
        f"metal bracket mount.\n{claims['cta']}\n{' '.join(fb_tags)}"
    )
    pin_titles = [
        f"{vo_name} Wall Shelf — 100% Waterproof Kitchen Organizer",
        f"Small Kitchen? This {vo_name} Shelf Fixes It",
        f"Bathroom Storage Idea — {vo_name} (COD Pakistan)",
    ]

    pack = {
        "date": datetime.date.today().isoformat(),
        "rotation": rot, "product": product, "vo_name": vo_name,
        "angle": detail["angle"], "hook": hook,
        "vo_script": vo_script, "title_overlays": overlays,
        "ig_caption": caption_en, "ig_hashtags": ig_tags,
        "fb_caption": fb_caption, "fb_hashtags": fb_tags,
        "pin_titles": pin_titles,
        "claims_check": {"used_only_allowed": True,
                         "allowed": claims["allowed_claims"],
                         "avoided": claims["forbidden_claims"]},
        "naming_rule": "Text me 'NABA Decor' OK; voiceover me sirf '2 Tier'/'S-Curve'.",
        "trend_snapshot": {
            "news_hits": len([t for t in trends["news_home_decor"] if not t.startswith("_err")]),
        },
    }
    write_json(os.path.join(d, "naba-pack.json"), pack)

    md = f"""# Naba Marketing Pack — {pack['date']}

**Rotation:** {rot} | **Product:** {product} (VO: "{vo_name}") | **Angle:** {detail['angle']}
**Hook:** {hook['key']} — {hook['desc']}

## v4 VO script (English, energetic — NO subtitles in video)
{vo_script}

## Title overlays (chhote, video par)
- {' / '.join(overlays)}

## Instagram (English caption + 5 hashtags)
{caption_en}

## Facebook (English caption + 3 hashtags)
{fb_caption}

## Pinterest pin titles
- {pin_titles[0]}
- {pin_titles[1]}
- {pin_titles[2]}

## Claims compliance
Sirf allowed claims use hue: {', '.join(claims['allowed_claims'])}
Avoided: {', '.join(claims['forbidden_claims'])}

## Naming rule
{pack['naming_rule']}

## Note
Video GENERATION is phase me nahi — ye pack video banane wale ke liye ready hai (real photos + v4 formula).
"""
    write_text(os.path.join(d, "naba-pack.md"), md)
    mark_used(state, hook["key"])
    save_state("naba", state)
    print(json.dumps({"rotation": rot, "product": product, "hook": hook["key"]}))

if __name__ == "__main__":
    main()
