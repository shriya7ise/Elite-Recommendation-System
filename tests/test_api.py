import os
import tempfile

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "t.db")
os.environ["GEMINI_API_KEY"] = ""
os.environ["SERPAPI_KEY"] = ""
from fastapi.testclient import TestClient  # noqa: E402

from backend.api import competitors, gemini_client, main, nlp  # noqa: E402

client = TestClient(main.app)
PAYLOAD = dict(name="Riya", email="riya@x.com", password="supersecret1", role_title="CMO", company="FitFuel", industry="Sports nutrition",
               offerings=["Whey Protein", "Vegan Bars"], audience="Gym-goers 20-35", geo="India", monthly_budget=50000)


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_nlp_basics():
    a = nlp.analyze_ad("Limited seats - Enroll now", "Join thousands of certified students. Free trial!")
    assert a["cta"] in ("Strong", "Medium") and "scarcity" in a["triggers"] and a["sentiment"] == "Positive"
    assert nlp.analyze_ad("", "")["words"] == 0


def test_auth_flow_and_isolation():
    r = client.post("/auth/register", json=PAYLOAD)
    assert r.status_code == 200
    t = r.json()["token"]
    assert client.post("/auth/register", json=PAYLOAD).status_code == 409
    assert client.post("/auth/login", json={"email": "riya@x.com", "password": "bad"}).status_code == 401
    assert client.get("/me").status_code == 401
    assert client.get("/me", headers=auth(t)).json()["business"]["company"] == "FitFuel"
    cs = client.get("/campaigns", headers=auth(t)).json()["campaigns"]
    assert len(cs) >= 3 and any("Whey" in c["name"] for c in cs)
    rec = client.get("/recommendations", headers=auth(t)).json()
    assert rec["platforms"] and rec["notice"]


def test_demo_persona_and_reco():
    t = client.post("/auth/demo").json()["token"]
    cs = client.get("/campaigns", headers=auth(t)).json()["campaigns"]
    assert {c["name"] for c in cs} == {"DS Bootcamp Q3", "AI Crash Course", "ML Pro Cert"}
    comps = client.get("/competitors", headers=auth(t)).json()["competitors"]
    assert comps and comps[0]["ads"]
    rec = client.get("/recommendations", headers=auth(t)).json()
    assert rec["angles"] and rec["campaign_actions"] and abs(sum(p["suggested_budget"] for p in rec["platforms"]) - 40000) < 1000
    assert client.get("/nlp/themes", headers=auth(t)).json()["themes"]
    assert client.get("/insights", headers=auth(t)).json()["insights"]


def test_discover_without_keys_is_503():
    t = client.post("/auth/login", json={"email": "riya@x.com", "password": "supersecret1"}).json()["token"]
    assert client.post("/competitors/discover", headers=auth(t)).status_code == 503


def test_discover_with_mocked_providers(monkeypatch):
    monkeypatch.setattr(gemini_client, "available", lambda: True)
    monkeypatch.setattr(competitors.config, "SERPAPI_KEY", "x")
    monkeypatch.setattr(gemini_client, "generate_json", lambda p, *a, **k: [{"name": "MuscleBlaze", "domain": "muscleblaze.com", "positioning": "Value whey", "strengths": ["price"], "weaknesses": ["trust"], "threat": 8}])
    monkeypatch.setattr(competitors, "serp", lambda q, loc=None: {"organic_results": [{"link": "https://www.muscleblaze.com/x"}], "ads": [{"title": "Whey 50% off", "description": "Buy now", "link": "https://muscleblaze.com/w"}]})
    t = client.post("/auth/login", json={"email": "riya@x.com", "password": "supersecret1"}).json()["token"]
    r = client.post("/competitors/discover", headers=auth(t))
    assert r.status_code == 200 and r.json()["ads"] >= 1
    c = client.get("/competitors", headers=auth(t)).json()["competitors"][0]
    assert c["verified"] and c["source"] == "gemini+serpapi" and c["ads"][0]["source"] == "serpapi"


def test_adgen_fallback_and_image_error():
    t = client.post("/auth/login", json={"email": "riya@x.com", "password": "supersecret1"}).json()["token"]
    r = client.post("/adgen/copy", headers=auth(t), json={"brief": "Protein launch"}).json()
    assert r["source"] == "template" and r["variations"]
    assert client.post("/adgen/image", headers=auth(t), json={"headline": "Hi", "visual_brief": "gym"}).status_code == 502
