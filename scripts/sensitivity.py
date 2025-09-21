#!/usr/bin/env python3
import argparse, itertools, json, numpy as np
from scipy.stats import kendalltau

def sweep(base: dict, pct: float = 0.10):
    keys = list(base)
    deltas = np.linspace(-pct, pct, 5)
    for change in itertools.product(deltas, repeat=len(keys)):
        w = {k: max(0.0, base[k]*(1+c)) for k, c in zip(keys, change)}
        s = sum(w.values())
        yield {k: v/s for k, v in w.items()}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scores_jsonl")
    ap.add_argument("--pct", type=float, default=0.10)
    args = ap.parse_args()
    rows = [json.loads(l) for l in open(args.scores_jsonl, encoding="utf-8") if l.strip()]
    base = np.array([r["score"] for r in rows])
    base_w = {"D":0.25,"O":0.20,"I":0.20,"M":0.20,"B":0.15}
    taus = []
    for w in sweep(base_w, args.pct):
        s = np.array([100*sum(w[k]*r["subscores"][k] for k in base_w) for r in rows])
        taus.append(kendalltau(base, s).correlation)
    print(f"Sweeps={len(taus)} | Kendall tau mean={np.nanmean(taus):.3f} min={np.nanmin(taus):.3f}")

if __name__ == "__main__":
    main()
