import json
from aioscore.normalization.apply import normalize_record
from aioscore.scoring.final import score_one

def test_reason_contains_expected_phrases():
    rec = json.loads(open("fixtures/companies.jsonl").readline())
    ctx = json.load(open("norm_contexts/ns_2025-08-07.json"))
    recn = normalize_record(rec, ctx)
    weights = {"D":0.25,"O":0.20,"I":0.20,"M":0.20,"B":0.15}
    rounding = {"score_decimals":2, "contribution_decimals":3}
    out = score_one(recn, weights, rounding)
    txt = out["reason_text"].lower()
    assert "digital" in txt and "market" in txt
