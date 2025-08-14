from aioscore.contracts.validator import validate_record
import json

def test_fixture_validates():
    rec = json.loads(open("fixtures/companies.jsonl","r",encoding="utf-8").read().splitlines()[0])
    errs = validate_record(rec)
    assert errs == []
