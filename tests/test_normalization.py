import json
from aioscore.normalization.apply import normalize_record

def test_normalization_deterministic():
    rec = json.loads(open("fixtures/companies.jsonl").readline())
    ctx = json.load(open("norm_contexts/ns_2025-08-07.json"))
    out1 = normalize_record(rec, ctx)
    out2 = normalize_record(rec, ctx)
    assert out1["norm"] == out2["norm"]
    assert out1["norm_stats_id"] == ctx["norm_stats_id"]
