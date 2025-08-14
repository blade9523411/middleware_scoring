from __future__ import annotations
import math

def z(x: float, mean: float, std: float) -> float:
    if std == 0:
        return 0.0
    return (x - mean) / std

def clip(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

def unit_from_z(zv: float) -> float:
    """Map z in [-3,3] to [0,1]."""
    return (zv + 3.0) / 6.0

def log10p(x: float) -> float:
    return math.log10(x + 1.0)

def pagespeed_scaled(ps: int) -> float:
    return max(0.0, min(1.0, ps / 100.0))
