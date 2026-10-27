"""Deterministic business simulation: campaigns & series derived from the business profile (seeded)."""
import random
from datetime import date

PLATFORMS = ["Google", "Meta", "LinkedIn", "YouTube"]
BASE = {"Google": (2.1, 2.6, 4.1), "Meta": (1.2, 1.8, 3.3), "LinkedIn": (0.9, 3.2, 2.4), "YouTube": (0.8, 1.4, 2.2)}  # ctr, cpc, cvr
SUFFIX = ["", " - Retargeting", " - Always-on", " - Launch"]
DEMO_CAMPAIGNS = [("DS Bootcamp Q3", "LinkedIn", "Running", 12000, 132, 7.8), ("AI Crash Course", "Meta", "Paused", 8000, 96, 6.1), ("ML Pro Cert", "Google", "Running", 20000, 148, 8.4)]


def _row(name, plat, status, budget, roi, score, copy, rng):
    ctr0, cpc0, cvr0 = BASE.get(plat, (1, 2, 3))
    ctr, cpc, cvr = (round(x * rng.uniform(0.75, 1.25), 2) for x in (ctr0, cpc0, cvr0))
    spend = round(budget * rng.uniform(0.55, 0.95), -1)
    imps = int(spend / cpc / (ctr / 100)) if cpc and ctr else 0
    return dict(name=name, platform=plat, status=status, budget=budget, spend=spend, roi=roi, ctr=ctr, cpc=cpc, cvr=cvr, impressions=imps, score=score, copy=copy)


def build_campaigns(b: dict, demo=False):
    rng = random.Random(b["id"] * 7919 + len(b["company"]))
    aud = b.get("audience") or "you"
    mk = lambda off: f"{off} by {b['company']}. Built for {aud}. Enroll today and see results." if demo else f"{off} from {b['company']}. Made for {aud}. Get started today."
    if demo:
        return [_row(n, p, s, bud, roi, sc, mk(n), rng) for n, p, s, bud, roi, sc in DEMO_CAMPAIGNS]
    offs = b.get("offerings") or [b["company"]]
    n = min(max(len(offs), 3), 6)
    per = (b.get("monthly_budget") or 30000) / n
    rows = []
    for i in range(n):
        off = offs[i % len(offs)] + SUFFIX[(i // len(offs)) % len(SUFFIX)]
        roi = rng.randint(70, 170)
        rows.append(_row(off, PLATFORMS[(i + rng.randint(0, 3)) % 4], rng.choice(["Running", "Running", "Paused"]),
                         round(per * rng.uniform(0.6, 1.4), -2), roi, round(min(10, max(3, roi / 20 + rng.uniform(-0.5, 0.5))), 1), mk(off), rng))
    return rows


def series(campaigns, seed=1):
    rng, total = random.Random(seed), sum(c["spend"] for c in campaigns) or 1
    today, out = date.today(), []
    for i in range(5):
        m = (today.month - 4 + i - 1) % 12 + 1
        out.append({"month": date(2000, m, 1).strftime("%b"), "spend": round(total * (0.6 + 0.1 * i) * rng.uniform(0.95, 1.05) / 1000, 1)})
    return out


def platform_table(campaigns):
    agg = {}
    for c in campaigns:
        a = agg.setdefault(c["platform"], {"spend": 0, "rev": 0, "ctr": [], "cpc": [], "cvr": []})
        a["spend"] += c["spend"]; a["rev"] += c["spend"] * c["roi"] / 100
        for k in ("ctr", "cpc", "cvr"):
            a[k].append(c[k])
    m = lambda l: round(sum(l) / len(l), 2)
    return [{"name": p, "revenue": round(a["rev"]), "spend": round(a["spend"]), "CTR": m(a["ctr"]), "CPC": m(a["cpc"]), "CVR": m(a["cvr"])} for p, a in agg.items()]
