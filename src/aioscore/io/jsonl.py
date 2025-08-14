from __future__ import annotations
import json
from typing import Iterable, Iterator, TextIO, Any

def read_jsonl(path: str) -> Iterator[dict]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)

def write_jsonl(path: str, records: Iterable[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, separators=(",", ":"), ensure_ascii=False) + "\n")
