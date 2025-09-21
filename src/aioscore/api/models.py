from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional

class Contribution(BaseModel):
    key: Literal["D","O","I","M","B"]
    points: float

class RiskBlock(BaseModel):
    level: Literal["low","medium","high"]
    reasons: List[str] = []
    confidence: float
    scrape_age_days: int

class FeasibilityBlock(BaseModel):
    ok: bool
    reasons: List[str] = []

class ScorePayload(BaseModel):
    schema_version: str
    weights_version: Optional[str] = None
    norm_stats_id: str
    company_id: str
    score: float
    subscores: Dict[str, float]
    contributions: List[Contribution]
    reason_text: str
    warnings: List[str] = []
    calc_ts: str
    flags: Dict[str, list] = {}      # kept for b/w compat
    risk: Optional[RiskBlock] = None
    feasibility: Optional[FeasibilityBlock] = None
    deterministic_hash: str

class ErrorDetail(BaseModel):
    errors: List[str]
