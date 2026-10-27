"""Gemini-powered ad copy + image generation, with offline template fallback for copy."""
from . import gemini_client as gem


def gen_copy(b, brief, platform, tone, n=3):
    prompt = f"""Create {n} distinct {platform} ad variations for {b['company']} ({b['industry']}).
Offer/brief: {brief}
Audience: {b.get('audience') or 'general'}; Tone: {tone}; Region: {b.get('geo') or 'global'}
Return JSON array of {{"headline":str(<=40 chars),"primary_text":str(<=140 chars),"cta":str,"angle":str,"audience":str}}.
Each variation must use a different persuasion angle. No false claims or guarantees of income."""
    if gem.available():
        try:
            data = gem.generate_json(prompt, temperature=0.9, ttl=0)
            data = data if isinstance(data, list) else data.get("ads", [])
            return {"source": "gemini", "variations": data[:n]}
        except Exception as e:
            err = str(e)
    else:
        err = "GEMINI_API_KEY not set"
    angles = [("outcome", "Start your next chapter"), ("value", "Learn more, spend less"), ("authority", "Learn from experts")]
    return {"source": "template", "warning": f"Gemini unavailable ({err}); showing templates.",
            "variations": [{"headline": h, "primary_text": f"{brief} - from {b['company']}. Built for {b.get('audience') or 'you'}.", "cta": "Get started", "angle": a, "audience": b.get("audience") or ""} for a, h in angles[:n]]}


def gen_image(b, headline, visual_brief, platform, style="clean, modern, high-contrast"):
    prompt = (f"Design a {platform} advertising creative for {b['company']} ({b['industry']}). Style: {style}. "
              f"Visual idea: {visual_brief}. Include the short headline text \"{headline}\" legibly. No logos of other brands, no real people's likenesses.")
    return gem.generate_image(prompt)
