from __future__ import annotations
from typing import Dict, List

def _phrase_d(d: float, pagespeed_scaled: float, crm: bool, ecom: bool) -> str:
    if d < 0.6: return ""
    bits = []
    if pagespeed_scaled >= 0.7: bits.append("fast site")
    if crm: bits.append("CRM")
    if ecom: bits.append("e-commerce")
    inner = ", ".join(bits) if bits else "solid digital signals"
    return f"High digital maturity ({inner}). "

def _phrase_i(i: float) -> str:
    return "Strong document volume. " if i >= 0.6 else ""

def _phrase_m(m: float) -> str:
    return "Market conditions favorable (growth outpacing rivalry). " if m >= 0.6 else ""

def _phrase_b(b: float) -> str:
    if b >= 0.7: return "Budget strong. "
    if b >= 0.4: return "Budget moderate. "
    return ""

def build_reason(subs: Dict[str, float], rec: dict) -> str:
    d = subs["D"]; i = subs["I"]; m = subs["M"]; b = subs["B"]
    parts = [
        _phrase_d(d, rec["norm"]["pagespeed_scaled"], rec["digital"]["crm_flag"], rec["digital"]["ecom_flag"]),
        _phrase_i(i),
        _phrase_m(m),
        _phrase_b(b),
    ]
    text = "".join(p for p in parts if p)
    return text.strip() or "Limited signals; score driven by mixed inputs."
