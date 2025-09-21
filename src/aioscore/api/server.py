from __future__ import annotations
import json, glob, os, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from aioscore.logging import setup as setup_logging
from aioscore.contracts.validator import validate_record
from aioscore.normalization.apply import normalize_record
from aioscore.scoring.final import score_one
from .models import ScorePayload, ErrorDetail

import yaml
from collections import Counter

app = FastAPI(title="AI Opportunity Scorer", version="1.0.0")

# simple in-memory metrics
_METRICS = Counter()

def _latest_norm_path() -> str:
    files = sorted(glob.glob("norm_contexts/*.json"), key=os.path.getmtime)
    if not files:
        raise HTTPException(500, "No NormContext found (create one via batch or script)")
    return files[-1]

def _load_weights_rounding() -> tuple[dict, dict, str]:
    cfg = yaml.safe_load(open("weights/weights.yaml", encoding="utf-8"))
    return cfg["weights"], cfg.get("rounding", {"score_decimals": 2, "contribution_decimals": 3}), cfg.get("version","weights@unknown")

class ScoreRequest(BaseModel):
    record: dict
    norm_stats_id: str | None = None

class BatchRequest(BaseModel):
    records: list[dict]
    norm_stats_id: str | None = None

@app.on_event("startup")
def _startup():
    setup_logging()
    app.state.started_at = time.time()

@app.get("/healthz")
def healthz():
    return {"ok": True, "uptime_s": round(time.time() - app.state.started_at, 3)}

@app.get("/metrics")
def metrics():
    # Prometheus-ish plaintext
    lines = [
        f"aioscore_requests_total {sum(_METRICS.values())}",
        f"aioscore_requests_score {_METRICS['score']}",
        f"aioscore_requests_score_batch {_METRICS['score_batch']}",
        f"aioscore_validations_failed {_METRICS['validation_failed']}",
    ]
    return "\n".join(lines)

@app.get("/stats")
def stats():
    p = _latest_norm_path()
    ctx = json.load(open(p, encoding="utf-8"))
    return {"norm_context_path": p, "norm_stats_id": ctx.get("norm_stats_id"), "cohort_keys": sorted(ctx.get("cohort", {}).keys())}

@app.get("/weights")
def weights():
    cfg = yaml.safe_load(open("weights/weights.yaml", encoding="utf-8"))
    return {"version": cfg.get("version","weights@unknown"), "weights": cfg["weights"]}

@app.post("/score", response_model=ScorePayload, responses={422: {"model": ErrorDetail}})
def score(req: ScoreRequest):
    _METRICS["score"] += 1
    errs = validate_record(req.record)
    if errs:
        _METRICS["validation_failed"] += 1
        raise HTTPException(422, {"errors": errs})

    ctx_path = f"norm_contexts/{req.norm_stats_id.replace(':','_')}.json" if req.norm_stats_id else _latest_norm_path()
    if not os.path.exists(ctx_path):
        raise HTTPException(404, f"NormContext not found: {req.norm_stats_id}")

    ctx = json.load(open(ctx_path, encoding="utf-8"))
    recn = normalize_record(req.record, ctx)
    weights, rounding, wver = _load_weights_rounding()

    payload = score_one(recn, weights, rounding)
    payload["weights_version"] = wver
    return payload

@app.post("/score/batch")
def score_batch(req: BatchRequest):
    _METRICS["score_batch"] += 1
    if len(req.records) > 1000:
        raise HTTPException(413, "Batch too large (max 1000)")

    ctx_path = f"norm_contexts/{req.norm_stats_id.replace(':','_')}.json" if req.norm_stats_id else _latest_norm_path()
    if not os.path.exists(ctx_path):
        raise HTTPException(404, f"NormContext not found: {req.norm_stats_id}")
    ctx = json.load(open(ctx_path, encoding="utf-8"))
    weights, rounding, wver = _load_weights_rounding()

    out = []
    for r in req.records:
        errs = validate_record(r)
        if errs:
            _METRICS["validation_failed"] += 1
            raise HTTPException(422, {"errors": errs})
        recn = normalize_record(r, ctx)
        p = score_one(recn, weights, rounding)
        p["weights_version"] = wver
        out.append(p)
    return {"count": len(out), "results": out}
