from __future__ import annotations
from typing import Dict
import yaml

from .subscores import digital, ops, infoflow, market, budget
from .reason import build_reason
from ..io.jsonl import read_jsonl, write_jsonl
from ..io.timestamps import now_utc_iso
from ..io.hashing import sha256_json

# Optional Phase-4 import (won't break Phase-3 if not present)
try:
    from ..risk.assess import assess_risk_and_feasibility  # type: ignore
    _HAS_RISK = True
except Exception:
    assess_risk_and_feasibility = None  # type: ignore
    _HAS_RISK = False


def _round_half_away(x: float, decimals: int) -> float:
    """Deterministic half-away-from-zero rounding."""
    from decimal import Decimal, ROUND_HALF_UP
    q = Decimal(10) ** (-decimals)
    return float(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP))


def score_one(rec: dict, weights: Dict[str, float], rounding: Dict[str, int]) -> dict:
    warnings: list[str] = []

    # Subscores
    D_obj = digital(rec["norm"], {"crm_flag": rec["digital"]["crm_flag"], "ecom_flag": rec["digital"]["ecom_flag"]})
    O_obj = ops(rec["norm"])
    I_obj = infoflow(rec, rec["norm"])
    M_obj = market(rec["norm"])
    B_obj = budget(rec, rec["norm"])

    for obj in (D_obj, O_obj, I_obj, M_obj, B_obj):
        warnings.extend(obj.get("warnings", []))

    subs = {"D": D_obj["value"], "O": O_obj["value"], "I": I_obj["value"], "M": M_obj["value"], "B": B_obj["value"]}

    # Final score
    score_raw = 100.0 * sum(weights[k] * subs[k] for k in ("D", "O", "I", "M", "B"))
    score_final = _round_half_away(score_raw, rounding.get("score_decimals", 2))

    # Contributions
    contrib = [
        {
            "key": k,
            "points": _round_half_away(weights[k] * subs[k] * 100.0, rounding.get("contribution_decimals", 3)),
        }
        for k in subs
    ]
    contrib.sort(key=lambda x: x["points"], reverse=True)

    # Base payload
    payload = {
        "schema_version": rec.get("model_version", "company_schema@1.0.0"),
        "weights_version": None,  # filled by caller
        "norm_stats_id": rec["norm_stats_id"],
        "company_id": rec["company_id"],
        "score": score_final,
        "subscores": subs,
        "contributions": contrib,
        "reason_text": build_reason(subs, rec),
        "warnings": warnings,
        "calc_ts": now_utc_iso(),
        # kept for backward-compat with any downstream that expects it
        "flags": {"risk": [], "feasibility": []},
    }

    # Phase 4 (optional): attach risk & feasibility if available
    if _HAS_RISK:
        risk, feas = assess_risk_and_feasibility(rec, payload)  # type: ignore
        payload["risk"] = risk
        payload["feasibility"] = feas

    # Compute deterministic hash AFTER all fields are present
    payload["deterministic_hash"] = sha256_json(payload)
    return payload


def score_stream(inp_path: str, weights_path: str, out_path: str) -> None:
    cfg = yaml.safe_load(open(weights_path, "r", encoding="utf-8"))
    weights = cfg["weights"]
    rounding = cfg.get("rounding", {"score_decimals": 2, "contribution_decimals": 3})

    out_records = []
    for rec in read_jsonl(inp_path):
        payload = score_one(rec, weights, rounding)
        payload["weights_version"] = cfg.get("version", "weights@unknown")
        out_records.append(payload)
    write_jsonl(out_path, out_records)
