import json
import os
import pathlib
from jsonschema import Draft202012Validator

def _find_project_root(start: pathlib.Path) -> pathlib.Path:
    """
    Walk up from `start` until we find a directory that contains 'schemas'.
    Falls back to start.parents[3] to handle typical <root>/src/aioscore/... layout.
    """
    cur = start
    for _ in range(6):
        if (cur / "schemas").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    # Fallback: assume <root>/src/aioscore/... -> root is parents[3]
    return start.parents[3]

def _schemas_dir() -> pathlib.Path:
    # Allow override via env if you ever want to relocate schemas
    env = os.getenv("AIOSCORE_SCHEMAS_DIR")
    if env:
        return pathlib.Path(env).resolve()
    # Auto-discover root/schemas
    start = pathlib.Path(__file__).resolve()
    root = _find_project_root(start)
    return (root / "schemas").resolve()

def load_company_schema_path() -> pathlib.Path:
    return _schemas_dir() / "company_schema_1_0_0.json"

def load_company_schema() -> dict:
    with open(load_company_schema_path(), "r", encoding="utf-8") as f:
        return json.load(f)

def get_company_validator() -> Draft202012Validator:
    schema = load_company_schema()
    return Draft202012Validator(schema)
