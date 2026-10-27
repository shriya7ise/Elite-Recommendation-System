"""Minimal Gemini REST client (text, JSON, image) with retry + cache. No SDK version headaches."""
import base64
import hashlib
import json
import logging
import re
import time

import requests

from . import config

log = logging.getLogger("gemini")
BASE = "https://generativelanguage.googleapis.com/v1beta/models"
_cache: dict = {}


class GeminiError(Exception):
    pass


def available() -> bool:
    return bool(config.GEMINI_API_KEY)


def _call(model: str, body: dict, timeout=90) -> dict:
    if not available():
        raise GeminiError("GEMINI_API_KEY is not set")
    last = ""
    for attempt in range(3):
        r = requests.post(f"{BASE}/{model}:generateContent", json=body, timeout=timeout,
                          headers={"x-goog-api-key": config.GEMINI_API_KEY, "Content-Type": "application/json"})
        if r.status_code in (429, 500, 502, 503):
            last = f"{r.status_code}"
            time.sleep(1.5 * (attempt + 1))
            continue
        if not r.ok:
            raise GeminiError(f"Gemini {r.status_code}: {r.text[:300]}")
        return r.json()
    raise GeminiError(f"Gemini busy/rate-limited ({last})")


def _parts(resp: dict):
    try:
        return resp["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError):
        raise GeminiError(f"Empty Gemini response: {str(resp)[:200]}")


def generate_text(prompt: str, system: str | None = None, temperature=0.7) -> str:
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature}}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    return "".join(p.get("text", "") for p in _parts(_text_call(body))).strip()


def _loads(text: str):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"(\{.*\}|\[.*\])", text, re.S)
        if m:
            return json.loads(m.group(1))
        raise GeminiError("Gemini did not return valid JSON")


def generate_json(prompt: str, system: str | None = None, temperature=0.4, ttl=3600):
    key = hashlib.sha256(f"{config.GEMINI_TEXT_MODEL}|{system}|{prompt}".encode()).hexdigest()
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "responseMimeType": "application/json"}}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    data = _loads("".join(p.get("text", "") for p in _parts(_text_call(body))))
    _cache[key] = (time.time(), data)
    return data


def generate_image(prompt: str) -> str:
    """Returns a data: URL. Needs an image-capable model/plan on your key."""
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}}
    for p in _parts(_call(config.GEMINI_IMAGE_MODEL, body, timeout=120)):
        inline = p.get("inlineData") or p.get("inline_data")
        if inline:
            return f"data:{inline.get('mimeType') or inline.get('mime_type', 'image/png')};base64,{inline['data']}"
    raise GeminiError("Image model returned no image (check model name / plan / safety filters)")


def _text_call(body: dict) -> dict:
    """Try the primary text model, then each fallback, when Google is overloaded / rate-limited / model missing."""
    last = None
    for m in [config.GEMINI_TEXT_MODEL, *config.GEMINI_FALLBACK_MODELS]:
        try:
            return _call(m, body)
        except GeminiError as e:
            last = e
            if not any(k in str(e) for k in ("busy", "rate-limited", "429", "503", "404")):
                raise
            log.warning("Gemini model %s failed (%s); trying next fallback", m, e)
    raise last
