from __future__ import annotations
import sqlite3, json, pathlib

DDL = """
CREATE TABLE IF NOT EXISTS scores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id TEXT NOT NULL,
  norm_stats_id TEXT NOT NULL,
  weights_version TEXT NOT NULL,
  score REAL NOT NULL,
  subscores TEXT NOT NULL,
  contributions TEXT NOT NULL,
  reason_text TEXT NOT NULL,
  risk TEXT NOT NULL,
  feasibility TEXT NOT NULL,
  warnings TEXT NOT NULL,
  calc_ts TEXT NOT NULL,
  deterministic_hash TEXT NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_scores_company_norm ON scores(company_id, norm_stats_id);
"""

def open_db(path: str) -> sqlite3.Connection:
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript(DDL)
    return con

def upsert_score(con: sqlite3.Connection, payload: dict) -> None:
    con.execute("""
    INSERT OR IGNORE INTO scores
    (company_id, norm_stats_id, weights_version, score, subscores, contributions, reason_text, risk, feasibility, warnings, calc_ts, deterministic_hash)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        payload["company_id"], payload["norm_stats_id"], payload["weights_version"], payload["score"],
        json.dumps(payload["subscores"], separators=(",",":")),
        json.dumps(payload["contributions"], separators=(",",":")),
        payload["reason_text"],
        json.dumps(payload.get("risk", {}), separators=(",",":")),
        json.dumps(payload.get("feasibility", {}), separators=(",",":")),
        json.dumps(payload.get("warnings", []), separators=(",",":")),
        payload["calc_ts"], payload["deterministic_hash"]
    ))
    con.commit()
