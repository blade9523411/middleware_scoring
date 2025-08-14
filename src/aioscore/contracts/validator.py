from __future__ import annotations
from typing import Iterable
from .schema_loader import get_company_validator
from ..io.jsonl import read_jsonl

def validate_record(rec: dict) -> list[str]:
    """Return list of error strings; empty list means valid."""
    v = get_company_validator()
    errors = []
    for e in sorted(v.iter_errors(rec), key=lambda x: x.path):
        path = ".".join(str(p) for p in e.path)
        errors.append(f"{path or '$'}: {e.message}")
    return errors

def validate_stream(inp_path: str, *, stop_on_error: bool=False) -> bool:
    ok_all = True
    for i, rec in enumerate(read_jsonl(inp_path), start=1):
        errors = validate_record(rec)
        if errors:
            ok_all = False
            print(f"[{i}] company_id={rec.get('company_id','?')}: INVALID")
            for msg in errors:
                print("   -", msg)
            if stop_on_error:
                return False
        else:
            print(f"[{i}] company_id={rec.get('company_id','?')}: OK")
    return ok_all
