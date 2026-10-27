"""Hybrid recommender: content-based platform/angle scoring + competitor-pressure + explainable reasons."""
import statistics

from . import nlp
from .simulate import PLATFORMS

ANGLE_HINTS = {
    "scarcity": "Cap intake / limited seats", "urgency": "Deadline-driven offer", "social_proof": "Lead with learner/customer numbers",
    "authority": "Foreground certification & expert mentors", "value": "Highlight free trial / scholarship / bundle",
    "outcome": "Sell the career outcome, not the syllabus", "curiosity": "Open with a question or myth-buster", "guarantee": "Add a risk-reversal guarantee",
}


def _norm(vals):
    lo, hi = min(vals), max(vals)
    return [0.5 if hi == lo else (v - lo) / (hi - lo) for v in vals]


def platform_recs(campaigns, ads, budget):
    plats = sorted({c["platform"] for c in campaigns} | {a["platform"] for a in ads if a.get("platform")} | set(PLATFORMS))
    own = {p: [c for c in campaigns if c["platform"] == p] for p in plats}
    mean = lambda p, k: sum(c[k] for c in own[p]) / len(own[p]) if own[p] else None
    has = [p for p in plats if own[p]]
    roi_n = dict(zip(has, _norm([mean(p, "roi") for p in has]))) if has else {}
    cvr_n = dict(zip(has, _norm([mean(p, "cvr") for p in has]))) if has else {}
    cpc_n = dict(zip(has, _norm([mean(p, "cpc") for p in has]))) if has else {}
    total_ads = max(1, len(ads))
    rows = []
    for p in plats:
        pressure = sum(a.get("platform") == p for a in ads) / total_ads
        if p in roi_n:
            fit = 0.45 * roi_n[p] + 0.25 * cvr_n[p] + 0.1 * (1 - cpc_n[p])
            why = [f"Your avg ROI here is {mean(p, 'roi'):.0f}%", f"CVR {mean(p, 'cvr'):.1f}%, CPC {mean(p, 'cpc'):.2f}"]
        else:
            fit, why = 0.3, ["No campaigns yet - exploration prior"]
        score = round(fit + 0.2 * (1 - pressure), 3)
        why.append(f"Competitors hold {pressure:.0%} of tracked ads here")
        conf = "high" if len(own[p]) >= 2 and len(ads) >= 10 else "medium" if own[p] or len(ads) >= 5 else "low"
        rows.append({"platform": p, "score": score, "pressure": round(pressure, 2), "confidence": conf, "reasons": why})
    w = [r["score"] ** 2 for r in rows]
    s = sum(w) or 1
    for r, wi in zip(rows, w):
        r["suggested_budget"] = round(budget * wi / s, -2)
        r["action"] = "Scale" if r["score"] >= 0.6 else "Maintain" if r["score"] >= 0.4 else "Test small"
    return sorted(rows, key=lambda r: -r["score"])


def angle_recs(own_analyses, comp_analyses):
    gaps = nlp.messaging_gaps(nlp.trigger_profile(own_analyses), nlp.trigger_profile(comp_analyses))
    for g in gaps:
        g["recommendation"] = ANGLE_HINTS[g["trigger"]]
        g["why"] = {"catch-up": f"{g['competitor_share']:.0%} of competitor ads use it vs {g['own_share']:.0%} of yours",
                    "whitespace": "Nobody in your market is using this angle - differentiation opportunity",
                    "defend": "You out-use competitors here - keep it"}[g["type"]]
    return gaps


def campaign_actions(campaigns):
    if not campaigns:
        return []
    med = statistics.median(c["roi"] for c in campaigns)
    out = []
    for c in campaigns:
        a = nlp.analyze_ad(c["name"], c.get("copy", ""))
        if c["roi"] >= 1.15 * med and c["status"] == "Running":
            act, why = "Scale +20% budget", f"ROI {c['roi']:.0f}% beats median {med:.0f}%"
        elif c["roi"] < 0.8 * med:
            act, why = "Rework creative or pause", f"ROI {c['roi']:.0f}% trails median {med:.0f}%"
        elif c["status"] == "Paused" and c["roi"] >= med:
            act, why = "Resume", "Paused despite median-or-better ROI"
        else:
            act, why = "Optimize", "Near median performance"
        tips = (["Weak CTA - add a clear action verb"] if a["cta"] == "Weak" else []) + (["Copy is hard to read - simplify"] if a["reading_level"] == "Hard" else [])
        out.append({"campaign": c["name"], "platform": c["platform"], "action": act, "why": why, "copy_tips": tips})
    return out


def similar_ads(campaigns, ads, k=2):
    docs = [f"{a['title']}. {a['description']}" for a in ads]
    out = []
    for c in campaigns:
        hits = nlp.similar(f"{c['name']}. {c.get('copy', '')}", docs, k)
        if hits:
            out.append({"campaign": c["name"], "closest_competitor_ads": [{"title": ads[i]["title"], "competitor": ads[i].get("competitor"), "similarity": s} for i, s in hits]})
    return out


def build_insights(campaigns, ads, own_an, comp_an):
    ins = []
    if campaigns:
        best = max(campaigns, key=lambda c: c["roi"]); worst = min(campaigns, key=lambda c: c["roi"])
        ins.append(f"Positive: '{best['name']}' on {best['platform']} is your top performer at {best['roi']:.0f}% ROI.")
        if worst is not best:
            ins.append(f"Negative: '{worst['name']}' on {worst['platform']} returns only {worst['roi']:.0f}% ROI - rework or reallocate.")
    if own_an and comp_an:
        o, c = nlp.summarize(own_an), nlp.summarize(comp_an)
        (ins.append(f"Positive: only {o['weak_cta_share']:.0%} of your ads have a weak CTA vs {c['weak_cta_share']:.0%} for competitors.") if o["weak_cta_share"] < c["weak_cta_share"]
         else ins.append(f"Negative: {o['weak_cta_share']:.0%} of your ads have a weak CTA (competitors: {c['weak_cta_share']:.0%})."))
        (ins.append("Positive: your copy is more persuasive than the competitor average.") if o["avg_persuasion"] > c["avg_persuasion"]
         else ins.append("Negative: competitor copy uses more persuasion levers than yours."))
        for g in nlp.messaging_gaps(nlp.trigger_profile(own_an), nlp.trigger_profile(comp_an))[:3]:
            ins.append(("Negative: " if g["type"] != "defend" else "Positive: ") + f"{g['trigger'].replace('_', ' ')} - " + ("untapped by you and competitors - test it." if g["type"] == "whitespace" else f"competitors {g['competitor_share']:.0%} vs you {g['own_share']:.0%}."))
    return ins
