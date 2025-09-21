#!/usr/bin/env python3
import argparse, csv, json, os, sys
import numpy as np
from scipy.stats import spearmanr, kendalltau
from sklearn.metrics import roc_auc_score

def load_scores(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    # strip company_id just in case of whitespace
    return {str(r["company_id"]).strip(): float(r["score"]) for r in rows}

def load_labels(path):
    lab = {}
    with open(path, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        if "company_id" not in rdr.fieldnames or "target" not in rdr.fieldnames:
            sys.exit("labels.csv must have headers: company_id,target")
        for row in rdr:
            cid = str(row["company_id"]).strip()
            if cid == "":  # skip empties
                continue
            lab[cid] = float(row["target"])
    return lab

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scores_jsonl")
    ap.add_argument("labels_csv")
    args = ap.parse_args()

    if not os.path.exists(args.scores_jsonl):
        sys.exit(f"scores file not found: {args.scores_jsonl}")
    if not os.path.exists(args.labels_csv):
        sys.exit(f"labels file not found: {args.labels_csv}")

    scores = load_scores(args.scores_jsonl)
    labels = load_labels(args.labels_csv)

    ids = sorted(set(scores) & set(labels))
    n = len(ids)
    if n == 0:
        only_in_scores = sorted(set(scores) - set(labels))
        only_in_labels = sorted(set(labels) - set(scores))
        print("N=0 (no overlapping company_id values).")
        print(f"- scores.jsonl ids (sample): {only_in_scores[:5]}")
        print(f"- labels.csv  ids (sample): {only_in_labels[:5]}")
        sys.exit(2)

    # vectors aligned by ids
    y = np.array([labels[i] for i in ids], float)
    s = np.array([scores[i] for i in ids], float)

    print(f"N={n}")

    # Rank correlations need at least 2
    if n >= 2:
        sp = float(spearmanr(s, y).correlation)
        kt = float(kendalltau(s, y).correlation)
        print(f"Spearman rho: {sp:.3f}")
        print(f"Kendall tau:  {kt:.3f}")
    else:
        print("Spearman/Kendall: not computed (need N>=2)")

    # AUC only for binary labels with both classes present and N>=2
    classes = set(np.unique(y))
    if n >= 2 and classes <= {0.0, 1.0} and len(classes) == 2:
        auc = float(roc_auc_score(y, s))
        print(f"AUC:          {auc:.3f}")
    else:
        print("AUC: not computed (need binary labels with both 0 and 1, N>=2)")

if __name__ == "__main__":
    main()
