"""Competitor discovery: Gemini proposes, SerpAPI verifies & supplies real ads. Every record carries its source."""
import logging
import re
from urllib.parse import urlparse

import requests

from . import config, gemini_client as gem

log = logging.getLogger("competitors")
GENERIC = {"wikipedia.org", "reddit.com", "quora.com", "youtube.com", "linkedin.com", "facebook.com", "medium.com", "instagram.com", "x.com", "twitter.com", "amazon.com", "github.com", "forbes.com", "g2.com", "capterra.com", "trustpilot.com", "yelp.com"}


class NoSourceError(Exception):
    pass


def domain_of(url: str) -> str:
    host = urlparse(url if "//" in (url or "") else f"//{url or ''}").netloc.lower()
    host = re.split(r"[\s\u203a/]", host.strip())[0]  # handles "site.com › path" display links
    return re.sub(r"^www\.", "", host)


def pretty(domain: str) -> str:
    return domain.split(".")[0].replace("-", " ").title() if domain else "Unknown"


def serp(q: str, location: str | None = None) -> dict:
    params = {"engine": "google", "q": q, "api_key": config.SERPAPI_KEY, "num": 10, "hl": "en"}
    if location:
        params["location"] = location
    r = requests.get("https://serpapi.com/search.json", params=params, timeout=40)
    if not r.ok:
        raise RuntimeError(f"SerpAPI {r.status_code}: {r.text[:200]}")
    return r.json()


def _gemini_competitors(b):
    prompt = f"""Business: {b['company']} ({b.get('website') or 'no website'})
Industry: {b['industry']}
What it sells: {', '.join(b.get('offerings') or [])}
Description: {b.get('description') or ''}
Audience: {b.get('audience') or ''}; Region: {b.get('geo') or 'global'}
List the 6 most relevant REAL direct competitors. Return JSON array of objects:
{{"name":str,"domain":str,"positioning":str,"strengths":[str,str],"weaknesses":[str,str],"threat":number 1-10}}
Only include companies you are confident exist."""
    data = gem.generate_json(prompt, system="You are a competitive-intelligence analyst. Be factual; never invent companies.")
    return data if isinstance(data, list) else data.get("competitors", [])


def _gemini_ads(b, comps):
    prompt = f"""Write 2 realistic SAMPLE search/social ads for each competitor of {b['company']} ({b['industry']}).
Competitors: {[c['name'] for c in comps]}
Return JSON array: {{"competitor":str,"platform":"Google"|"Meta"|"LinkedIn"|"YouTube","title":str,"description":str}}"""
    data = gem.generate_json(prompt, temperature=0.8)
    return data if isinstance(data, list) else data.get("ads", [])


def discover(b: dict):
    """-> (competitors, ads, notes). Raises NoSourceError if neither Gemini nor SerpAPI is configured/working."""
    comps, ads, notes = {}, [], []
    own = domain_of(b.get("website") or "")
    if gem.available():
        try:
            for c in _gemini_competitors(b)[:6]:
                d = domain_of(c.get("domain") or "")
                if c.get("name") and d != own:
                    comps[d or c["name"].lower()] = {**c, "domain": d, "source": "gemini", "verified": False}
        except Exception as e:
            notes.append(f"Gemini competitor lookup failed: {e}")
    if config.SERPAPI_KEY:
        seen = {}
        queries = [f"{o} {b['industry']}" for o in (b.get("offerings") or [b["industry"]])[:3]]
        for q in queries:
            try:
                res = serp(q, b.get("geo"))
            except Exception as e:
                notes.append(str(e)); continue
            for o in res.get("organic_results", []):
                d = domain_of(o.get("link", ""))
                if d and d != own and d not in GENERIC:
                    seen[d] = seen.get(d, 0) + 1
                    if d in comps:
                        comps[d]["verified"] = True; comps[d]["source"] = "gemini+serpapi"
            for a in res.get("ads", []):
                d = domain_of(a.get("link") or a.get("displayed_link", ""))
                if not d or d == own:
                    continue
                if d not in comps:
                    comps[d] = {"name": pretty(d), "domain": d, "positioning": "", "strengths": [], "weaknesses": [], "threat": 5, "source": "serpapi", "verified": True}
                ads.append({"competitor_key": d, "platform": "Google", "ad_type": "Search Ad", "title": a.get("title", ""), "description": a.get("description", ""), "link": a.get("link", ""), "source": "serpapi"})
        if not comps:  # no Gemini: promote most frequent organic domains
            for d, n in sorted(seen.items(), key=lambda x: -x[1])[:6]:
                comps[d] = {"name": pretty(d), "domain": d, "positioning": "", "strengths": [], "weaknesses": [], "threat": min(9, 3 + n), "source": "serpapi", "verified": True}
    if not comps:
        raise NoSourceError("; ".join(notes) or "Set GEMINI_API_KEY and/or SERPAPI_KEY to discover competitors")
    if not ads and gem.available():
        try:
            by_name = {c["name"].lower(): k for k, c in comps.items()}
            for a in _gemini_ads(b, list(comps.values())):
                k = by_name.get(str(a.get("competitor", "")).lower())
                if k:
                    ads.append({"competitor_key": k, "platform": a.get("platform", "Google"), "ad_type": "Sample", "title": a.get("title", ""), "description": a.get("description", ""), "link": "", "source": "gemini-simulated"})
            notes.append("No live ads found - ads shown are AI-simulated samples.")
        except Exception as e:
            notes.append(f"Ad simulation failed: {e}")
    return comps, ads, notes
