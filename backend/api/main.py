"""Elite API.  Run from repo root:  uvicorn backend.api.main:app --reload --port 8000"""
import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import adgen, config, db, gemini_client as gem, nlp, recommender as rec, security as sec, seed, simulate
from .competitors import NoSourceError, discover

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
app = FastAPI(title="Elite Marketing Intelligence API", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
db.init()


class Biz(BaseModel):
    company: str = Field(min_length=1, max_length=120)
    industry: str = Field(min_length=1, max_length=120)
    website: str | None = None
    description: str | None = Field(None, max_length=1500)
    offerings: list[str] = Field(default_factory=list, max_length=10)
    audience: str | None = None
    geo: str | None = None
    monthly_budget: float = Field(30000, ge=0)


class RegisterIn(Biz):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=128)
    role_title: str | None = None


class LoginIn(BaseModel):
    email: str
    password: str


class TextIn(BaseModel):
    title: str = ""
    text: str = Field(min_length=1, max_length=3000)


class CopyIn(BaseModel):
    brief: str = Field(min_length=3, max_length=500)
    platform: str = "Meta"
    tone: str = "confident, friendly"
    n: int = Field(3, ge=1, le=5)


class ImageIn(BaseModel):
    headline: str = Field(max_length=80)
    visual_brief: str = Field(min_length=3, max_length=400)
    platform: str = "Meta"


def profile(user, b):
    return {"user": {"id": user["id"], "name": user["name"], "email": user["email"], "role_title": user["role_title"], "is_demo": bool(user["is_demo"])},
            "business": {k: b[k] for k in ("id", "company", "industry", "website", "description", "offerings", "audience", "geo", "monthly_budget")}}


def session(uid):
    user = db.one("SELECT * FROM users WHERE id=?", (uid,))
    b = db.one("SELECT * FROM businesses WHERE user_id=?", (uid,)); b["offerings"] = db.jl(b["offerings"], [])
    return {"token": sec.make_token(uid), **profile(user, b)}


def ads_with_analysis(bid):
    out = db.rows("SELECT a.*, c.name AS competitor FROM ads a LEFT JOIN competitors c ON c.id=a.competitor_id WHERE a.business_id=?", (bid,))
    for a in out:
        a["analysis"] = db.jl(a["analysis"], {})
    return out


@app.get("/health")
def health():
    return {"status": "ok", "gemini": gem.available(), "serpapi": bool(config.SERPAPI_KEY), "text_model": config.GEMINI_TEXT_MODEL, "image_model": config.GEMINI_IMAGE_MODEL}


@app.post("/auth/register", dependencies=[Depends(sec.rate_limit(5, 60))])
def register(p: RegisterIn):
    if db.one("SELECT id FROM users WHERE email=?", (p.email.lower(),)):
        raise HTTPException(409, "Email already registered")
    uid, _ = seed.create_user_business(p.email, p.password, p.name, p.role_title, p.model_dump(exclude={"name", "email", "password", "role_title"}))
    return session(uid)


@app.post("/auth/login", dependencies=[Depends(sec.rate_limit(10, 60))])
def login(p: LoginIn):
    u = db.one("SELECT * FROM users WHERE email=?", (p.email.lower(),))
    if not u or not sec.verify_password(p.password, u["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    return session(u["id"])


@app.post("/auth/demo", dependencies=[Depends(sec.rate_limit(20, 60))])
def demo_login():
    return session(seed.ensure_demo())


@app.get("/me")
def me(user=Depends(sec.current_user), b=Depends(sec.current_business)):
    return profile(user, b)


@app.put("/business")
def update_business(p: Biz, b=Depends(sec.current_business)):
    import json
    db.run("UPDATE businesses SET company=?,industry=?,website=?,description=?,offerings=?,audience=?,geo=?,monthly_budget=? WHERE id=?",
           (p.company, p.industry, p.website, p.description, json.dumps(p.offerings), p.audience, p.geo, p.monthly_budget, b["id"]))
    return {"ok": True}


@app.post("/competitors/discover", dependencies=[Depends(sec.rate_limit(5, 300))])
def discover_competitors(b=Depends(sec.current_business)):
    try:
        comps, ads, notes = discover(b)
    except NoSourceError as e:
        raise HTTPException(503, f"Competitor discovery unavailable: {e}")
    seed.save_competitors(b["id"], comps, ads)
    return {"count": len(comps), "ads": len(ads), "notes": notes}


@app.get("/competitors")
def competitors(b=Depends(sec.current_business)):
    comps = db.rows("SELECT * FROM competitors WHERE business_id=? ORDER BY threat DESC", (b["id"],))
    ads = ads_with_analysis(b["id"])
    for c in comps:
        c["strengths"], c["weaknesses"] = db.jl(c["strengths"], []), db.jl(c["weaknesses"], [])
        c["ads"] = [a for a in ads if a["competitor_id"] == c["id"]]
        c["summary"] = nlp.summarize([a["analysis"] for a in c["ads"]])
    return {"competitors": comps}


@app.post("/nlp/analyze")
def analyze(p: TextIn):
    return nlp.analyze_ad(p.title, p.text)


@app.get("/nlp/themes")
def competitor_themes(b=Depends(sec.current_business)):
    ads = ads_with_analysis(b["id"])
    texts = [f"{a['title']}. {a['description']}" for a in ads]
    return {"themes": nlp.themes(texts), "keywords": nlp.top_keywords(texts, 12), "ads_analyzed": len(texts)}


@app.get("/campaigns")
def campaigns(b=Depends(sec.current_business)):
    cs = db.rows("SELECT * FROM campaigns WHERE business_id=?", (b["id"],))
    return {"campaigns": cs, "monthly_spend": simulate.series(cs, b["id"]), "platforms": simulate.platform_table(cs)}


@app.get("/recommendations")
def recommendations(b=Depends(sec.current_business)):
    cs, ads = db.rows("SELECT * FROM campaigns WHERE business_id=?", (b["id"],)), ads_with_analysis(b["id"])
    own_an = [nlp.analyze_ad(c["name"], c.get("copy", "")) for c in cs]
    comp_an = [a["analysis"] for a in ads]
    return {"platforms": rec.platform_recs(cs, ads, b["monthly_budget"] or sum(c["budget"] for c in cs)), "angles": rec.angle_recs(own_an, comp_an),
            "campaign_actions": rec.campaign_actions(cs), "similar_ads": rec.similar_ads(cs, ads), "data_points": {"campaigns": len(cs), "competitor_ads": len(ads)},
            "notice": None if ads else "No competitor ads yet - run competitor discovery for stronger recommendations."}


@app.get("/insights")
def insights(narrative: bool = False, b=Depends(sec.current_business)):
    cs, ads = db.rows("SELECT * FROM campaigns WHERE business_id=?", (b["id"],)), ads_with_analysis(b["id"])
    items = rec.build_insights(cs, ads, [nlp.analyze_ad(c["name"], c.get("copy", "")) for c in cs], [a["analysis"] for a in ads])
    out = {"insights": items}
    if narrative and gem.available():
        try:
            out["narrative"] = gem.generate_text(f"Business: {b['company']} ({b['industry']}). Findings:\n- " + "\n- ".join(items) + "\nWrite a 120-word executive summary with 3 prioritized next actions. Use only these findings.", temperature=0.4)
        except Exception as e:
            out["narrative_error"] = str(e)
    return out


@app.post("/adgen/copy", dependencies=[Depends(sec.rate_limit(15, 60))])
def ad_copy(p: CopyIn, b=Depends(sec.current_business)):
    return adgen.gen_copy(b, p.brief, p.platform, p.tone, p.n)


@app.post("/adgen/image", dependencies=[Depends(sec.rate_limit(6, 60))])
def ad_image(p: ImageIn, b=Depends(sec.current_business)):
    try:
        return {"image": adgen.gen_image(b, p.headline, p.visual_brief, p.platform)}
    except Exception as e:
        raise HTTPException(502, f"Image generation failed: {e}")
