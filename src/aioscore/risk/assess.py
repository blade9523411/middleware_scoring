from __future__ import annotations
from datetime import datetime, timezone
from typing import Tuple
import os, pathlib, yaml

def _get(d: dict, path: str, default=None):
    cur = d
    for p in path.split("."):
        if p not in cur:
            return default
        cur = cur[p]
    return cur

def _days_since(ts_iso: str) -> int:
    dt = datetime.fromisoformat(ts_iso.replace("Z", "+00:00"))
    return int((datetime.now(timezone.utc) - dt).total_seconds() // 86400)

def _policy_path() -> pathlib.Path:
    # 1) explicit env override
    if os.getenv("AIOSCORE_POLICY_PATH"):
        return pathlib.Path(os.getenv("AIOSCORE_POLICY_PATH")).resolve()
    if os.getenv("AIOSCORE_POLICY_DIR"):
        return (pathlib.Path(os.getenv("AIOSCORE_POLICY_DIR")) / "policy.yaml").resolve()

    # 2) search upwards from this file for a "policy/policy.yaml"
    start = pathlib.Path(__file__).resolve()
    for up in start.parents:
        cand = up / "policy" / "policy.yaml"
        if cand.exists():
            return cand.resolve()

    # 3) fallback (typical <root>/src/aioscore/... -> root is parents[3])
    # guard against IndexError if the tree is shallower
    try:
        return (start.parents[3] / "policy" / "policy.yaml").resolve()
    except IndexError:
        return (start.parents[-1] / "policy" / "policy.yaml").resolve()

def load_policy(path: str | None = None) -> dict:
    p = pathlib.Path(path).resolve() if path else _policy_path()
    return yaml.safe_load(open(p, "r", encoding="utf-8"))

def assess_risk_and_feasibility(rec: dict, payload: dict, policy: dict | None = None) -> Tuple[dict, dict]:
    p = policy or load_policy()
    # --- Risk ---
    conf = float(_get(rec, "meta.source_confidence", 0.0))
    age_days = _days_since(_get(rec, "meta.scrape_ts", "1970-01-01T00:00:00Z"))
    reasons_r: list[str] = []
    penalties = 0

    if conf >= p["risk"]["min_source_confidence_low"]:
        conf_tier = "low"
    elif conf >= p["risk"]["min_source_confidence_med"]:
        conf_tier = "medium"; reasons_r.append(f"source_confidence={conf:.2f}<low")
    else:
        conf_tier = "high"; reasons_r.append(f"source_confidence={conf:.2f}<med")

    if age_days <= p["risk"]["max_scrape_age_low_days"]:
        age_tier = "low"
    elif age_days <= p["risk"]["max_scrape_age_med_days"]:
        age_tier = "medium"; reasons_r.append(f"scrape_age={age_days}d>low")
    else:
        age_tier = "high"; reasons_r.append(f"scrape_age={age_days}d>med")

    missing = [f for f in p["risk"]["missing_penalty_fields"] if _get(rec, f, None) in (None, 0, 0.0)]
    if missing:
        penalties += len(missing)
        reasons_r.append("missing_or_zero:" + ",".join(missing))

    rank = {"low": 0, "medium": 1, "high": 2}
    level = ["low", "medium", "high"][min(2, max(rank[conf_tier], rank[age_tier]) + (1 if penalties else 0))]
    risk = {"level": level, "reasons": reasons_r, "confidence": conf, "scrape_age_days": age_days}

    # --- Feasibility ---
    reasons_f: list[str] = []
    docs_ok = (_get(rec, "info_flow.daily_docs_est", 0) or 0) >= p["feasibility"]["min_docs"]
    if not docs_ok: reasons_f.append(f"docs<{p['feasibility']['min_docs']}")

    floor_ok = (_get(rec, "budget.revenue_est_usd", 0.0) or 0.0) >= p["feasibility"]["budget_floor_usd"]
    if not floor_ok: reasons_f.append(f"budget<{p['feasibility']['budget_floor_usd']}")

    any_ok = any(bool(_get(rec, f, False)) for f in p["feasibility"]["require_any_of"])
    if not any_ok: reasons_f.append(f"none_of:{','.join(p['feasibility']['require_any_of'])}")

    ok = docs_ok and floor_ok and any_ok
    feasibility = {"ok": ok, "reasons": ([] if ok else reasons_f)}

    return risk, feasibility
