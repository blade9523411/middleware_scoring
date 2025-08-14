#!/usr/bin/env python3
import argparse, json, sys
from aioscore.normalization.stats import compute_norm_context

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="companies.jsonl")
    ap.add_argument("--out", dest="out", required=True, help="norm_contexts/ns_*.json")
    args = ap.parse_args()
    ctx = compute_norm_context(args.inp)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(ctx, f, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    print("norm_stats_id:", ctx["norm_stats_id"])

if __name__ == "__main__":
    sys.exit(main())
