import json, pathlib
from jsonschema import Draft202012Validator

SCHEMAS_DIR = pathlib.Path(__file__).resolve().parents[2] / "schemas"

def load_company_schema_path() -> pathlib.Path:
    return SCHEMAS_DIR / "company_schema_1_0_0.json"

def load_company_schema() -> dict:
    with open(load_company_schema_path(), "r", encoding="utf-8") as f:
        return json.load(f)

def get_company_validator() -> Draft202012Validator:
    schema = load_company_schema()
    return Draft202012Validator(schema)
