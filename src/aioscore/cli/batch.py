from __future__ import annotations
import json, pathlib, typer
from typing import Optional

from aioscore.contracts.validator import validate_stream
from aioscore.normalization.stats import compute_norm_context
from aioscore.normalization.apply import normalize_stream
from aioscore.scoring.final import score_stream
from aioscore.persist.db import open_db, upsert_score
from aioscore.io.jsonl import read_jsonl
from aioscore.logging import setup as setup_logging
import logging

app = typer.Typer(add_completion=False, help="Batch scoring runner")

@app.command("run")
def run(
    inp: str = typer.Argument(..., metavar="INP", help="Path to companies.jsonl"),
    out: str = typer.Argument(..., metavar="OUT", help="Scores JSONL"),
    db_path: str = typer.Option("results/aioscore.db", "--db-path", help="SQLite path"),
    norm_out: Optional[str] = typer.Option(None, "--norm-out", help="Where to save NormContext JSON"),
):
    setup_logging()
    log = logging.getLogger("aioscore.batch")
    log.info("batch_start inp=%s out=%s db=%s", inp, out, db_path)

    ok = validate_stream(inp)
    log.info("phase0_validate ok=%s", ok)
    if not ok:
        raise typer.Exit(code=2)

    ctx = compute_norm_context(inp)
    norm_path = norm_out or f"norm_contexts/{ctx['norm_stats_id'].replace(':','_')}.json"
    pathlib.Path(norm_path).parent.mkdir(parents=True, exist_ok=True)
    json.dump(ctx, open(norm_path, "w", encoding="utf-8"), separators=(",", ":"), sort_keys=True)
    log.info("phase1_norm_context path=%s id=%s", norm_path, ctx.get("norm_stats_id"))

    features_path = out + ".features.jsonl"
    normalize_stream(inp, norm_path, features_path)
    log.info("phase1_normalize features=%s", features_path)

    weights_path = "weights/weights.yaml"
    score_stream(features_path, weights_path, out)
    log.info("phase2_3_4_scored out=%s", out)

    con = open_db(db_path)
    for rec in read_jsonl(out):
        upsert_score(con, rec)
    log.info("persist_done db=%s", db_path)
