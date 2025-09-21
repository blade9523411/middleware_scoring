from __future__ import annotations
import json

def norm_drift(baseline_ctx_path: str, new_ctx_path: str) -> dict:
    base = json.load(open(baseline_ctx_path, encoding="utf-8"))
    new  = json.load(open(new_ctx_path, encoding="utf-8"))
    out = {}
    for k, stats in base.get("cohort", {}).items():
        bm, bs = stats["mean"], stats["std"]
        nm = new["cohort"].get(k, {}).get("mean", bm)
        ns = new["cohort"].get(k, {}).get("std", bs)
        out[k] = {"mean_delta": nm - bm, "std_delta": ns - bs}
    return out
