"""Password hashing (scrypt), JWT auth, and a small in-memory rate limiter."""
import hashlib
import hmac
import os
import time
from collections import defaultdict, deque

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import config, db

_bearer = HTTPBearer(auto_error=False)


def hash_password(pw: str) -> str:
    salt = os.urandom(16)
    h = hashlib.scrypt(pw.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"{salt.hex()}:{h.hex()}"


def verify_password(pw: str, stored: str) -> bool:
    try:
        salt, h = stored.split(":")
        calc = hashlib.scrypt(pw.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1)
        return hmac.compare_digest(calc.hex(), h)
    except ValueError:
        return False


def make_token(user_id: int) -> str:
    now = int(time.time())
    return jwt.encode({"sub": str(user_id), "iat": now, "exp": now + config.JWT_TTL_SECONDS}, config.JWT_SECRET, algorithm="HS256")


def current_user(cred: HTTPAuthorizationCredentials = Depends(_bearer)):
    if not cred:
        raise HTTPException(401, "Not authenticated")
    try:
        sub = jwt.decode(cred.credentials, config.JWT_SECRET, algorithms=["HS256"])["sub"]
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid or expired token")
    user = db.one("SELECT * FROM users WHERE id=?", (int(sub),))
    if not user:
        raise HTTPException(401, "User not found")
    return user


def current_business(user=Depends(current_user)):
    b = db.one("SELECT * FROM businesses WHERE user_id=?", (user["id"],))
    if not b:
        raise HTTPException(404, "Business profile missing")
    b["offerings"] = db.jl(b["offerings"], [])
    b["is_demo"] = bool(user["is_demo"])
    return b


_hits = defaultdict(deque)


def rate_limit(max_calls=10, window=60):
    def dep(request: Request):
        key = f"{request.url.path}:{request.client.host if request.client else 'x'}"
        q, now = _hits[key], time.time()
        while q and now - q[0] > window:
            q.popleft()
        if len(q) >= max_calls:
            raise HTTPException(429, "Too many requests, slow down")
        q.append(now)
    return dep
