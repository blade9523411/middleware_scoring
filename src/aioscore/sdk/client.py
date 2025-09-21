from __future__ import annotations
import requests

class ScorerClient:
    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")

    def score_record(self, rec: dict, norm_stats_id: str | None = None) -> dict:
        r = requests.post(f"{self.base}/score", json={"record": rec, "norm_stats_id": norm_stats_id}, timeout=10)
        r.raise_for_status()
        return r.json()

    def score_batch(self, recs: list[dict], norm_stats_id: str | None = None) -> list[dict]:
        r = requests.post(f"{self.base}/score/batch", json={"records": recs, "norm_stats_id": norm_stats_id}, timeout=30)
        r.raise_for_status()
        return r.json()["results"]
