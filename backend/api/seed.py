"""Create businesses, campaigns, competitors, ads; plus the demo ed-tech persona."""
import json
import re

import pandas as pd

from . import config, db, nlp
from .competitors import domain_of, pretty
from .security import hash_password
from .simulate import build_campaigns

DEMO_EMAIL = "demo@elite.demo"


def save_campaigns(b, demo=False):
    db.run("DELETE FROM campaigns WHERE business_id=?", (b["id"],))
    db.many("INSERT INTO campaigns(business_id,name,platform,status,budget,spend,roi,ctr,cpc,cvr,impressions,score,copy) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            [(b["id"], c["name"], c["platform"], c["status"], c["budget"], c["spend"], c["roi"], c["ctr"], c["cpc"], c["cvr"], c["impressions"], c["score"], c["copy"]) for c in build_campaigns(b, demo)])


def save_competitors(business_id, comps: dict, ads: list):
    db.run("DELETE FROM competitors WHERE business_id=?", (business_id,))  # cascades to ads
    ids = {}
    for key, c in comps.items():
        ids[key] = db.run("INSERT INTO competitors(business_id,name,domain,positioning,strengths,weaknesses,threat,source,verified) VALUES(?,?,?,?,?,?,?,?,?)",
                          (business_id, c["name"], c.get("domain", ""), c.get("positioning", ""), json.dumps(c.get("strengths", [])), json.dumps(c.get("weaknesses", [])),
                           float(c.get("threat") or 5), c.get("source", ""), int(bool(c.get("verified")))))
    db.many("INSERT INTO ads(business_id,competitor_id,platform,ad_type,title,description,link,source,analysis) VALUES(?,?,?,?,?,?,?,?,?)",
            [(business_id, ids.get(a["competitor_key"]), a.get("platform"), a.get("ad_type"), a.get("title"), a.get("description"), a.get("link"), a.get("source"),
              json.dumps(nlp.analyze_ad(a.get("title"), a.get("description")))) for a in ads if a["competitor_key"] in ids])


def create_user_business(email, password, name, role_title, biz: dict, is_demo=False):
    uid = db.run("INSERT INTO users(email,password_hash,name,role_title,is_demo) VALUES(?,?,?,?,?)", (email.lower(), hash_password(password), name, role_title, int(is_demo)))
    bid = db.run("INSERT INTO businesses(user_id,company,industry,website,description,offerings,audience,geo,monthly_budget) VALUES(?,?,?,?,?,?,?,?,?)",
                 (uid, biz["company"], biz["industry"], biz.get("website"), biz.get("description"), json.dumps(biz.get("offerings", [])), biz.get("audience"), biz.get("geo"), biz.get("monthly_budget") or 0))
    b = db.one("SELECT * FROM businesses WHERE id=?", (bid,)); b["offerings"] = biz.get("offerings", [])
    save_campaigns(b, demo=is_demo)
    return uid, b


def ensure_demo():
    u = db.one("SELECT id FROM users WHERE email=?", (DEMO_EMAIL,))
    if u:
        return u["id"]
    import secrets
    uid, b = create_user_business(DEMO_EMAIL, secrets.token_urlsafe(16), "Aarav Mehta", "Head of Growth", dict(
        company="UpSkill Academy", industry="Ed-tech / online courses", website="https://upskill-academy.example",
        description="Online academy for data science and AI career courses.", audience="Working professionals and graduates upskilling into data/AI roles",
        offerings=["DS Bootcamp Q3", "AI Crash Course", "ML Pro Cert"], geo="India", monthly_budget=40000), is_demo=True)
    comps, ads = {}, []
    if config.DEMO_CSV.exists():  # real scraped ads that ship with the project
        df = pd.read_csv(config.DEMO_CSV).fillna("")
        for _, r in df.iterrows():
            ch = str(r.get("Channel")).strip()
            dom = domain_of(str(r.get("Link")))
            key = ch or dom or "unknown"
            comps.setdefault(key, {"name": ch or pretty(dom), "domain": domain_of(str(r.get("Link"))), "positioning": "From project dataset", "strengths": [], "weaknesses": [], "threat": 5, "source": "demo-dataset", "verified": True})
            ads.append({"competitor_key": key, "platform": str(r.get("Platform")), "ad_type": str(r.get("Ad Type")), "title": str(r.get("Title")), "description": re.sub(r"\s+", " ", str(r.get("Description")))[:400], "link": str(r.get("Link")), "source": "demo-dataset"})
        for c in comps.values():
            n = sum(1 for a in ads if comps.get(a["competitor_key"]) is c)
            c["threat"] = round(min(9, 3 + n / 2), 1)
    if not ads:  # CSV missing -> small built-in sample so the demo is never empty
        for name, pl, t, d in [("Skillwave", "LinkedIn", "Become a Data Scientist", "Industry-recognized program. Learn ML, AI, and more."),
                               ("Skillwave", "Google", "Data Science Certification", "Join thousands of learners. Enroll now."),
                               ("CodeNest", "Meta", "AI Career Fast-Track", "Limited seats. Hands-on projects with mentors."),
                               ("CodeNest", "YouTube", "Learn Python in 1 Hour", "Free beginner course - start today!")]:
            comps.setdefault(name, {"name": name, "domain": "", "positioning": "Sample data", "strengths": [], "weaknesses": [], "threat": 6, "source": "demo-sample", "verified": False})
            ads.append({"competitor_key": name, "platform": pl, "ad_type": "Sample", "title": t, "description": d, "link": "", "source": "demo-sample"})
    save_competitors(b["id"], comps, ads)
    return uid
