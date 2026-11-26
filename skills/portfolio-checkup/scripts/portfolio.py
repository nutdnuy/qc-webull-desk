#!/usr/bin/env python3
"""Concentration and diversification measures for one portfolio. Stdlib only.

Usage: python3 portfolio.py holdings.json [--out metrics.json]

Input:
{
  "as_of": "26 Nov 2026, 16:00 ICT", "currency": "USD", "cash": 1200.0,
  "positions": [
    {"symbol": "AAPL", "market_value": 3555.8, "cost_basis": 2900.0, "sector": "Technology", "type": "stock"}
  ],
  "thresholds": {"single_position": 0.20}
}
`cost_basis`, `sector` and `type` are optional. Thresholds are rules of thumb the
user may change; they are not a standard and not a recommendation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULTS = {"single_position": 0.20, "top_three": 0.50, "single_sector": 0.40,
            "effective_holdings_min": 8.0, "cash_max": 0.30}


class InputError(ValueError):
    pass


def number(value, where: str, minimum: float | None = None) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        raise InputError(f"{where}: {value!r} is not a number")
    if out != out or abs(out) == float("inf"):
        raise InputError(f"{where}: not finite")
    if minimum is not None and out < minimum:
        raise InputError(f"{where}: must be at least {minimum}")
    return out


def analyse(data: dict) -> dict:
    rows = data.get("positions") or []
    if not rows:
        raise InputError("positions is empty")
    limits = dict(DEFAULTS)
    for key, value in (data.get("thresholds") or {}).items():
        if key not in DEFAULTS:
            raise InputError(f"unknown threshold {key!r}")
        limits[key] = number(value, f"thresholds.{key}", 0)
    cash = number(data.get("cash", 0), "cash", 0)
    merged: dict[str, dict] = {}
    for n, row in enumerate(rows):
        symbol = str(row.get("symbol", "")).strip().upper()
        if not symbol:
            raise InputError(f"position {n}: symbol is missing")
        value = number(row.get("market_value"), f"{symbol}.market_value", 0)
        slot = merged.setdefault(symbol, {"symbol": symbol, "market_value": 0.0, "cost_basis": None,
                                          "sector": str(row.get("sector") or "Unclassified"),
                                          "type": str(row.get("type") or "stock")})
        slot["market_value"] += value
        if row.get("cost_basis") is not None:
            slot["cost_basis"] = (slot["cost_basis"] or 0.0) + number(row["cost_basis"], f"{symbol}.cost_basis", 0)
    invested = sum(p["market_value"] for p in merged.values())
    total = invested + cash
    if total <= 0:
        raise InputError("total value is zero")
    positions = sorted(merged.values(), key=lambda p: -p["market_value"])
    for p in positions:
        p["weight"] = p["market_value"] / total
        if p["cost_basis"]:
            p["unrealised"] = p["market_value"] - p["cost_basis"]
            p["unrealised_pct"] = p["unrealised"] / p["cost_basis"]
    weights = [p["weight"] for p in positions]
    invested_weights = [p["market_value"] / invested for p in positions] if invested else []
    hhi = sum(w * w for w in invested_weights)
    sectors: dict[str, float] = {}
    for p in positions:
        sectors[p["sector"]] = sectors.get(p["sector"], 0.0) + p["weight"]
    sector_rows = sorted(({"sector": k, "weight": v} for k, v in sectors.items()), key=lambda r: -r["weight"])
    known_cost = [p for p in positions if p["cost_basis"]]
    summary = {
        "total_value": total, "invested_value": invested, "cash": cash, "cash_weight": cash / total,
        "holdings": len(positions), "largest_weight": weights[0], "top_three_weight": sum(weights[:3]),
        "top_five_weight": sum(weights[:5]), "hhi_invested": hhi,
        "effective_holdings": (1 / hhi) if hhi else 0.0,
        "largest_sector": sector_rows[0]["sector"], "largest_sector_weight": sector_rows[0]["weight"],
        "unclassified_weight": sectors.get("Unclassified", 0.0),
    }
    if known_cost:
        cost = sum(p["cost_basis"] for p in known_cost)
        summary["unrealised"] = sum(p["unrealised"] for p in known_cost)
        summary["unrealised_pct"] = summary["unrealised"] / cost
        summary["cost_coverage"] = sum(p["weight"] for p in known_cost)
    checks = [
        ("single_position", summary["largest_weight"], ">", f"largest holding {positions[0]['symbol']}"),
        ("top_three", summary["top_three_weight"], ">", "three largest holdings together"),
        ("single_sector", summary["largest_sector_weight"], ">", f"largest sector {sector_rows[0]['sector']}"),
        ("effective_holdings_min", summary["effective_holdings"], "<", "effective number of holdings"),
        ("cash_max", summary["cash_weight"], ">", "cash"),
    ]
    flags = []
    for key, observed, sign, what in checks:
        limit = limits[key]
        crossed = observed > limit if sign == ">" else observed < limit
        flags.append({"check": key, "what": what, "observed": observed, "threshold": limit,
                      "comparison": sign, "crossed": crossed})
    notes = ["Weights use total value including cash; HHI and effective holdings use invested value only.",
             "An ETF counts as one holding here although it holds many companies.",
             "Thresholds are adjustable rules of thumb, not standards or advice."]
    if summary["unclassified_weight"] > 0:
        notes.append("Some holdings have no sector, so the sector view is incomplete.")
    return {"as_of": data.get("as_of"), "currency": data.get("currency", "USD"), "summary": summary,
            "positions": positions, "sectors": sector_rows, "flags": flags, "thresholds": limits, "notes": notes}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("holdings", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        result = analyse(json.loads(args.holdings.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
