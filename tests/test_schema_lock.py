import hashlib, json, pathlib

def sha256(p: pathlib.Path) -> str:
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()

def test_schema_locked():
    root = pathlib.Path(__file__).resolve().parents[1]
    lock = json.loads((root/"schemas/schema_lock.json").read_text())
    path = root/"schemas/company_schema_1_0_0.json"
    assert lock["company_schema_1_0_0.json"] == sha256(path)

