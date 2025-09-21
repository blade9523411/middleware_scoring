#!/usr/bin/env python3
import argparse, json, sys
from aioscore.monitoring.drift import norm_drift

ap = argparse.ArgumentParser()
ap.add_argument("baseline_ctx")
ap.add_argument("new_ctx")
ap.add_argument("--mean-thresh", type=float, default=0.35)
ap.add_argument("--std-thresh", type=float, default=0.35)
args = ap.parse_args()

diff = norm_drift(args.baseline_ctx, args.new_ctx)
bad = {}
for k, d in diff.items():
    if abs(d["mean_delta"]) > args.mean_thresh or abs(d["std_delta"]) > args.std_thresh:
        bad[k] = d

print(json.dumps({"diff": diff, "violations": bad}, indent=2))
sys.exit(1 if bad else 0)
