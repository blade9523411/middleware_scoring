from __future__ import annotations
import json, statistics
from typing import Iterable, Dict
from ..io.jsonl import read_jsonl
from ..io.hashing import sha256_json

FIELDS = {
    "ops.employees",
    "ops.locations",
    "ops.services_count",
    "market.competitor_density",
    "market.industry_growth_pct",
    "market.rivalry_index",
}

def _pluck(rec: dict, path: str) -> float:
    cur = rec
    for p in path.split("."):
        cur = cur[p]
    return float(cur)

def compute_norm_context(inp_path: str, *, schema_version="company_schema@1.0.0") -> dict:
    values = {k: [] for k in FIELDS}
    for rec in read_jsonl(inp_path):
        for f in FIELDS:
            values[f].append(_pluck(rec, f))
    cohort = {}
    for f, arr in values.items():
        m = statistics.fmean(arr) if arr else 0.0
        sd = statistics.pstdev(arr) if len(arr) > 1 else 0.0
        cohort[f] = {"mean": m, "std": sd}
    ctx = {
        "schema_version": schema_version,
        "cohort": cohort,
    }
    ctx["norm_stats_id"] = sha256_json(ctx)
    return ctx
