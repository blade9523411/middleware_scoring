from __future__ import annotations
from pydantic import BaseModel, Field, AwareDatetime, field_validator
from typing import Literal
import re

class Digital(BaseModel):
    pagespeed: int = Field(ge=0, le=100)
    crm_flag: bool
    ecom_flag: bool

class Ops(BaseModel):
    employees: int = Field(ge=0, le=200_000)
    locations: int = Field(ge=0, le=10_000)
    services_count: int = Field(ge=0, le=10_000)

class InfoFlow(BaseModel):
    daily_docs_est: int = Field(ge=0, le=10_000_000)

class Market(BaseModel):
    competitor_density: int = Field(ge=0, le=10_000)
    industry_growth_pct: float = Field(ge=-100.0, le=100.0)
    rivalry_index: float = Field(ge=0.0, le=1.0)

class Budget(BaseModel):
    revenue_est_usd: float = Field(ge=0.0, le=1.0e13)

class Meta(BaseModel):
    scrape_ts: AwareDatetime
    source_confidence: float = Field(ge=0.0, le=1.0)

class CompanyV1(BaseModel):
    model_version: Literal["company_schema@1.0.0"] = "company_schema@1.0.0"
    company_id: str = Field(min_length=1, max_length=200)
    domain: str
    digital: Digital
    ops: Ops
    info_flow: InfoFlow
    market: Market
    budget: Budget
    meta: Meta

    @field_validator("domain")
    @classmethod
    def domain_format(cls, v: str) -> str:
        if not re.match(r"^[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", v):
            raise ValueError("invalid domain")
        return v
