from __future__ import annotations
import json
from typing import Iterator
from .transforms import z, clip, unit_from_z, log10p, pagespeed_scaled
from ..io.jsonl import read_jsonl, write_jsonl

_Z_CLIP = (-3.0, 3.0)

def _zmap(x: float, m: float, s: float) -> float:
    return unit_from_z(clip(z(x, m, s), *_Z_CLIP))

def _get(ctx: dict, field: str, key: str) -> float:
    return float(ctx["cohort"][field][key])

def normalize_record(rec: dict, ctx: dict) -> dict:
    # Precompute z’s for fields used in O and M
    norm = {
        "z_employees": z(rec["ops"]["employees"], _get(ctx, "ops.employees", "mean"), _get(ctx, "ops.employees", "std")),
        "z_locations": z(rec["ops"]["locations"], _get(ctx, "ops.locations", "mean"), _get(ctx, "ops.locations", "std")),
        "z_services": z(rec["ops"]["services_count"], _get(ctx, "ops.services_count", "mean"), _get(ctx, "ops.services_count", "std")),
        "z_comp_density": z(rec["market"]["competitor_density"], _get(ctx, "market.competitor_density", "mean"), _get(ctx, "market.competitor_density", "std")),
        "z_growth": z(rec["market"]["industry_growth_pct"], _get(ctx, "market.industry_growth_pct", "mean"), _get(ctx, "market.industry_growth_pct", "std")),
        "z_rivalry": z(rec["market"]["rivalry_index"], _get(ctx, "market.rivalry_index", "mean"), _get(ctx, "market.rivalry_index", "std")),
        "pagespeed_scaled": pagespeed_scaled(rec["digital"]["pagespeed"]),
        "log_docs_over4": (log10p(rec["info_flow"]["daily_docs_est"]) / 4.0),
        "log_rev_over7": (0.0 if rec["budget"]["revenue_est_usd"] <= 0 else (log10p(rec["budget"]["revenue_est_usd"] - 1) / 7.0)),
    }
    out = dict(rec)
    out["norm"] = norm
    out["norm_stats_id"] = ctx["norm_stats_id"]
    return out

def normalize_stream(inp_path: str, norm_path: str, out_path: str) -> None:
    ctx = json.load(open(norm_path, "r", encoding="utf-8"))
    records = (normalize_record(r, ctx) for r in read_jsonl(inp_path))
    write_jsonl(out_path, records)
