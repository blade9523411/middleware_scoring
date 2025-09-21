# Calibration Report

**Scores file:** `.\scores.jsonl`  
**Labels file:** `.\labels.csv`

## Metrics
```
N=3
Spearman rho: 0.866
Kendall tau:  0.816
AUC:          1.000
```

## Score Distribution (summary)
- count: 3
- mean: 60.48
- median: 61.40
- min / max: 46.51 / 73.54

## Notes
- Freeze `weights/weights.yaml` at `version: weights@1.0` once acceptable.
- Re-run this report whenever weights or normalization change.
