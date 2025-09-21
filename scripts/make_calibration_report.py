#!/usr/bin/env python3
import argparse, subprocess, json, statistics as st, sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scores_jsonl")
    ap.add_argument("labels_csv")
    ap.add_argument("--out", default="docs/calibration.md")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.verbose:
        print(f"[report] running calibrator: {args.scores_jsonl} vs {args.labels_csv}")

    p = subprocess.run(
        [sys.executable, "scripts/calibrate.py", args.scores_jsonl, args.labels_csv],
        capture_output=True, text=True
    )

    if args.verbose:
        print(f"[report] calibrator rc={p.returncode}")
        if p.stdout: print("[report] calibrator stdout:\n" + p.stdout)
        if p.stderr: print("[report] calibrator stderr:\n" + p.stderr)

    if p.returncode != 0:
        # Bubble up calibrator details but still exit nonzero so CI fails
        sys.stderr.write(p.stdout)
        sys.stderr.write(p.stderr)
        print(f"[report] calibrator failed (rc={p.returncode}). No report written.")
        sys.exit(p.returncode)

    metrics = p.stdout.strip()
    scores = [json.loads(l)["score"] for l in open(args.scores_jsonl, encoding="utf-8") if l.strip()]

    parts = []
    parts.append("# Calibration Report\n\n")
    parts.append(f"**Scores file:** `{args.scores_jsonl}`  \n")
    parts.append(f"**Labels file:** `{args.labels_csv}`\n\n")
    parts.append("## Metrics\n```\n")
    parts.append(metrics + "\n```\n\n")
    if scores:
        parts.append("## Score Distribution (summary)\n")
        parts.append(f"- count: {len(scores)}\n")
        parts.append(f"- mean: {st.mean(scores):.2f}\n")
        parts.append(f"- median: {st.median(scores):.2f}\n")
        parts.append(f"- min / max: {min(scores):.2f} / {max(scores):.2f}\n\n")
    else:
        parts.append("## Score Distribution (summary)\n- No scores found.\n\n")
    parts.append("## Notes\n")
    parts.append("- Freeze `weights/weights.yaml` at `version: weights@1.0` once acceptable.\n")
    parts.append("- Re-run this report whenever weights or normalization change.\n")

    out_path.write_text("".join(parts), encoding="utf-8")
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
