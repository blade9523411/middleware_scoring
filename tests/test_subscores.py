import json, math
from aioscore.normalization.apply import normalize_record
from aioscore.scoring.subscores import digital, ops, infoflow, market, budget

def test_subscores_match_handcalc():
    rec = json.loads(open("fixtures/companies.jsonl").readline())
    ctx = json.load(open("norm_contexts/ns_2025-08-07.json"))
    recn = normalize_record(rec, ctx)
    D = digital(recn["norm"], {"crm_flag": recn["digital"]["crm_flag"], "ecom_flag": recn["digital"]["ecom_flag"]})["value"]
    assert abs(D - 0.612) < 1e-6
