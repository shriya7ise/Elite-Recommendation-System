"""Tiny SQLite layer (swap for Postgres later - all SQL lives here and in the routers)."""
import json
import sqlite3
from contextlib import closing
from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
  name TEXT NOT NULL, role_title TEXT, is_demo INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS businesses(
  id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  company TEXT NOT NULL, industry TEXT NOT NULL, website TEXT, description TEXT, offerings TEXT DEFAULT '[]',
  audience TEXT, geo TEXT, monthly_budget REAL DEFAULT 0);
CREATE TABLE IF NOT EXISTS competitors(
  id INTEGER PRIMARY KEY AUTOINCREMENT, business_id INTEGER NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
  name TEXT NOT NULL, domain TEXT, positioning TEXT, strengths TEXT DEFAULT '[]', weaknesses TEXT DEFAULT '[]',
  threat REAL DEFAULT 5, source TEXT, verified INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS ads(
  id INTEGER PRIMARY KEY AUTOINCREMENT, business_id INTEGER NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
  competitor_id INTEGER REFERENCES competitors(id) ON DELETE CASCADE, platform TEXT, ad_type TEXT, title TEXT,
  description TEXT, link TEXT, source TEXT, analysis TEXT DEFAULT '{}', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS campaigns(
  id INTEGER PRIMARY KEY AUTOINCREMENT, business_id INTEGER NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
  name TEXT, platform TEXT, status TEXT, budget REAL, spend REAL, roi REAL, ctr REAL, cpc REAL, cvr REAL,
  impressions INTEGER, score REAL, copy TEXT);
"""


def _conn():
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(config.DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c


def init():
    with closing(_conn()) as c:
        c.executescript(SCHEMA)


def run(sql, args=()):
    with closing(_conn()) as c:
        cur = c.execute(sql, args)
        c.commit()
        return cur.lastrowid


def many(sql, rows):
    with closing(_conn()) as c:
        c.executemany(sql, rows)
        c.commit()


def rows(sql, args=()):
    with closing(_conn()) as c:
        return [dict(r) for r in c.execute(sql, args).fetchall()]


def one(sql, args=()):
    r = rows(sql, args)
    return r[0] if r else None


def jl(v, default=None):
    try:
        return json.loads(v) if isinstance(v, str) else (v if v is not None else default)
    except json.JSONDecodeError:
        return default
