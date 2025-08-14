from __future__ import annotations
import math

def _unit_from_zsum(zsum: float) -> float:
    zc = max(-3.0, min(3.0, zsum))
    return (zc + 3.0) / 6.0

def digital(norm: dict, flags: dict) -> dict:
    v = 0.4 * norm["pagespeed_scaled"] + 0.3 * (1 if flags["crm_flag"] else 0) + 0.3 * (1 if flags["ecom_flag"] else 0)
    return {"value": max(0.0, min(1.0, v)), "inputs_used": ["digital.pagespeed", "digital.crm_flag", "digital.ecom_flag"]}

def ops(norm: dict) -> dict:
    zsum = norm["z_employees"] + norm["z_locations"] + norm["z_services"]
    return {"value": _unit_from_zsum(zsum), "inputs_used": ["ops.employees", "ops.locations", "ops.services_count"]}

def infoflow(rec: dict, norm: dict) -> dict:
    return {"value": max(0.0, min(1.0, norm["log_docs_over4"])), "inputs_used": ["info_flow.daily_docs_est"]}

def market(norm: dict) -> dict:
    zsum = norm["z_comp_density"] + norm["z_growth"] - norm["z_rivalry"]
    return {"value": _unit_from_zsum(zsum), "inputs_used": ["market.competitor_density", "market.industry_growth_pct", "market.rivalry_index"]}

def budget(rec: dict, norm: dict) -> dict:
    rev = rec["budget"]["revenue_est_usd"]
    if rev <= 0:
        return {"value": 0.0, "inputs_used": ["budget.revenue_est_usd"], "warnings": ["budget.zero_or_missing"]}
    return {"value": max(0.0, min(1.0, norm["log_rev_over7"])), "inputs_used": ["budget.revenue_est_usd"]}
