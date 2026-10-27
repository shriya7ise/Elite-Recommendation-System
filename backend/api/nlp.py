"""Ad-copy NLP: sentiment, CTA, urgency, persuasion triggers, readability, themes, similarity, gaps.
Runs fully offline (scikit-learn). Set NLP_EMBEDDINGS=st (and pip install sentence-transformers)
for semantic embeddings in similarity search."""
import os
import re
from collections import Counter

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

POS = set("best great free easy fast love win save boost grow proven trusted amazing improve success master achieve enjoy powerful simple smart exclusive guaranteed premium top rated results".split())
NEG = set("worst hard difficult slow lose risk fail problem pain waste expensive stuck struggle mistake fear missing behind complicated confusing".split())
NEGATORS = {"not", "no", "never", "without", "dont", "don't"}
CTA_VERBS = "enroll register apply join start get learn buy shop book download try sign subscribe claim discover explore reserve upgrade watch".split()
TRIGGERS = {
    "scarcity": "limited seats left only last hurry exclusive spots".split(),
    "urgency": "now today tonight ends deadline soon immediately instantly fast".split(),
    "social_proof": "trusted students customers rated reviews join thousands millions community popular".split(),
    "authority": "certified expert industry-recognized accredited official leading certification mentors professionals".split(),
    "value": "free discount save off bonus offer deal sale cheap affordable".split(),
    "outcome": "career job salary promotion transform master achieve grow success become results".split(),
    "curiosity": "secret discover revealed how why truth hidden".split(),
    "guarantee": "guarantee guaranteed refund risk-free money-back".split(),
}
_tok = lambda t: re.findall(r"[a-z][a-z'\-]*", (t or "").lower())


def _syll(w):
    return max(1, len(re.findall(r"[aeiouy]+", w)))


def flesch(text):
    words, sents = _tok(text), max(1, len(re.findall(r"[.!?]+", text or "")) or 1)
    if not words:
        return 0.0
    return round(206.835 - 1.015 * len(words) / sents - 84.6 * sum(_syll(w) for w in words) / len(words), 1)


def analyze_ad(title: str = "", description: str = "") -> dict:
    text = f"{title or ''}. {description or ''}".strip()
    toks = _tok(text)
    pos = neg = 0
    for i, t in enumerate(toks):
        flip = i > 0 and toks[i - 1] in NEGATORS
        if t in POS:
            neg, pos = (neg + 1, pos) if flip else (neg, pos + 1)
        elif t in NEG:
            pos, neg = (pos + 1, neg) if flip else (pos, neg + 1)
    score = round((pos - neg) / max(1, pos + neg), 2)
    label = "Positive" if score > 0.15 else "Negative" if score < -0.15 else "Neutral"
    triggers = sorted(k for k, ws in TRIGGERS.items() if any(w in toks for w in ws))
    ctas = [v for v in CTA_VERBS if v in toks]
    cta = "Strong" if len(ctas) >= 2 or (ctas and ({"urgency", "scarcity"} & set(triggers))) else "Medium" if ctas else "Weak"
    urg_hits = len({"urgency", "scarcity"} & set(triggers)) + text.count("!") // 2
    ease = flesch(text)
    return {
        "words": len(toks), "chars": len(text),
        "sentiment": label, "sentiment_score": score,
        "confidence": round(min(0.99, 0.5 + abs(score) / 2), 2) if (pos + neg) else 0.5,
        "cta": cta, "cta_verbs": ctas,
        "urgency": "High" if urg_hits >= 2 else "Medium" if urg_hits == 1 else "Low",
        "triggers": triggers,
        "reading_ease": ease,
        "reading_level": "Easy" if ease >= 70 else "Medium" if ease >= 45 else "Hard",
        "persuasion": len(triggers) + (1 if cta != "Weak" else 0),
        "keywords": top_keywords([text], 6),
    }


def top_keywords(texts, n=10):
    texts = [t for t in texts if t and t.strip()]
    if not texts:
        return []
    try:
        v = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True, token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z\-]+\b")
        X = v.fit_transform(texts)
    except ValueError:
        return []
    w = np.asarray(X.sum(axis=0)).ravel()
    terms = v.get_feature_names_out()
    return [terms[i] for i in w.argsort()[::-1][:n]]


def themes(texts, k=4):
    texts = [t for t in texts if t and t.strip()]
    if len(texts) < 4:
        return [{"theme": " / ".join(top_keywords(texts, 3)) or "n/a", "size": len(texts), "terms": top_keywords(texts, 6), "example": texts[0] if texts else ""}] if texts else []
    v = TfidfVectorizer(stop_words="english", sublinear_tf=True, token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z\-]+\b")
    X = v.fit_transform(texts)
    k = max(2, min(k, len(texts) // 2))
    km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
    terms, out = v.get_feature_names_out(), []
    for c in range(k):
        idx = np.where(km.labels_ == c)[0]
        top = [terms[i] for i in km.cluster_centers_[c].argsort()[::-1][:6]]
        out.append({"theme": " / ".join(top[:3]), "size": int(len(idx)), "terms": top, "example": texts[int(idx[0])]})
    return sorted(out, key=lambda x: -x["size"])


def _embed(texts):
    if os.getenv("NLP_EMBEDDINGS") == "st":
        try:
            from sentence_transformers import SentenceTransformer
            return SentenceTransformer("all-MiniLM-L6-v2").encode(texts, normalize_embeddings=True)
        except Exception:
            pass
    return TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True).fit_transform(texts)


def similar(query: str, docs: list[str], k=3):
    """Nearest docs to query -> [(index, similarity)]"""
    if not query.strip() or not docs:
        return []
    try:
        M = _embed([query] + docs)
        sims = cosine_similarity(M[0:1], M[1:]).ravel()
    except ValueError:
        return []
    return [(int(i), round(float(sims[i]), 3)) for i in sims.argsort()[::-1][:k] if sims[i] > 0.05]


def trigger_profile(analyses):
    n = max(1, len(analyses))
    return {t: round(sum(t in (a.get("triggers") or []) for a in analyses) / n, 2) for t in TRIGGERS}


def messaging_gaps(own, comp):
    """Compare own vs competitor trigger usage -> ranked opportunities."""
    out = []
    for t in TRIGGERS:
        o, c = own.get(t, 0), comp.get(t, 0)
        if c - o >= 0.15:
            kind, gain = "catch-up", c - o
        elif c < 0.1 and o < 0.1:
            kind, gain = "whitespace", 0.25
        elif o - c >= 0.15:
            kind, gain = "defend", 0.0
        else:
            continue
        out.append({"trigger": t, "own_share": o, "competitor_share": c, "type": kind, "priority": round(gain, 2)})
    return sorted(out, key=lambda x: -x["priority"])


def summarize(analyses):
    if not analyses:
        return {}
    avg = lambda k: round(sum(a[k] for a in analyses) / len(analyses), 2)
    return {"n": len(analyses), "avg_sentiment": avg("sentiment_score"), "avg_reading_ease": avg("reading_ease"),
            "avg_persuasion": avg("persuasion"), "weak_cta_share": round(sum(a["cta"] == "Weak" for a in analyses) / len(analyses), 2),
            "cta": dict(Counter(a["cta"] for a in analyses))}
