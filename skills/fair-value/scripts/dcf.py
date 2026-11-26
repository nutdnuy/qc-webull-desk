#!/usr/bin/env python3
"""Two-stage discounted cash flow with three cases, a sensitivity grid and a
reverse check. Stdlib only.

Usage: python3 dcf.py inputs.json [--out result.json]

Input (money in one currency and one scale, for example USD million):
{
  "symbol": "AAPL", "currency": "USD", "scale": "million",
  "price": 355.58, "shares_outstanding": 14532.2, "net_debt": -35000,
  "base_fcf": 108000, "years": 10,
  "cases": {
    "bear": {"growth_1_5": 0.03, "growth_6_10": 0.02, "terminal_growth": 0.02, "discount_rate": 0.10},
    "base": {"growth_1_5": 0.07, "growth_6_10": 0.04, "terminal_growth": 0.025, "discount_rate": 0.09},
    "bull": {"growth_1_5": 0.11, "growth_6_10": 0.06, "terminal_growth": 0.03, "discount_rate": 0.085}
  }
}
`shares_outstanding` uses the same scale as the money. Every growth and discount
figure is an assumption supplied by the user or stated as such; none is data.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CASES = ("bear", "base", "bull")
KEYS = ("growth_1_5", "growth_6_10", "terminal_growth", "discount_rate")


class InputError(ValueError):
    pass


def number(value, where: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        raise InputError(f"{where}: {value!r} is not a number")
    if out != out or abs(out) == float("inf"):
        raise InputError(f"{where}: not finite")
    return out


def value_per_share(fcf: float, g1: float, g2: float, gt: float, r: float, years: int,
                    net_debt: float, shares: float) -> dict:
    if r <= gt:
        raise InputError(f"discount rate {r} must be above terminal growth {gt}")
    if r <= 0:
        raise InputError("discount rate must be positive")
    half = years // 2
    flow, pv = fcf, 0.0
    flows = []
    for year in range(1, years + 1):
        flow *= 1 + (g1 if year <= half else g2)
        pv += flow / (1 + r) ** year
        flows.append(flow)
    terminal = flows[-1] * (1 + gt) / (r - gt)
    pv_terminal = terminal / (1 + r) ** years
    enterprise = pv + pv_terminal
    equity = enterprise - net_debt
    return {"enterprise_value": enterprise, "equity_value": equity, "per_share": equity / shares,
            "pv_explicit": pv, "pv_terminal": pv_terminal,
            "terminal_share": pv_terminal / enterprise if enterprise else None,
            "final_year_fcf": flows[-1]}


def implied_growth(price: float, fcf: float, gt: float, r: float, years: int, net_debt: float, shares: float):
    """Constant growth over the explicit period that makes value equal price."""
    def gap(g: float) -> float:
        return value_per_share(fcf, g, g, gt, r, years, net_debt, shares)["per_share"] - price

    lo, hi = -0.50, 1.00
    if gap(lo) > 0 or gap(hi) < 0:
        return None
    for _ in range(80):
        mid = (lo + hi) / 2
        if gap(mid) > 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def run(data: dict) -> dict:
    price = number(data.get("price"), "price")
    shares = number(data.get("shares_outstanding"), "shares_outstanding")
    fcf = number(data.get("base_fcf"), "base_fcf")
    net_debt = number(data.get("net_debt", 0), "net_debt")
    years = int(data.get("years", 10))
    if price <= 0 or shares <= 0:
        raise InputError("price and shares_outstanding must be positive")
    if fcf <= 0:
        raise InputError("base_fcf must be positive; a company with negative free cash flow needs another method")
    if not 4 <= years <= 20:
        raise InputError("years must be between 4 and 20")
    cases_in = data.get("cases") or {}
    cases = {}
    for name in CASES:
        if name not in cases_in:
            raise InputError(f"cases.{name} is missing")
        a = {k: number(cases_in[name].get(k), f"cases.{name}.{k}") for k in KEYS}
        res = value_per_share(fcf, a["growth_1_5"], a["growth_6_10"], a["terminal_growth"], a["discount_rate"],
                              years, net_debt, shares)
        res["assumptions"] = a
        res["gap_to_price"] = res["per_share"] / price - 1
        cases[name] = res
    base = cases["base"]["assumptions"]
    grid_in = data.get("sensitivity") or {}
    rates = [number(v, "sensitivity.discount_rates") for v in grid_in.get("discount_rates", [])] or \
        [round(base["discount_rate"] + d, 4) for d in (-0.01, -0.005, 0, 0.005, 0.01)]
    growths = [number(v, "sensitivity.terminal_growths") for v in grid_in.get("terminal_growths", [])] or \
        [round(base["terminal_growth"] + d, 4) for d in (-0.005, 0, 0.005)]
    grid = []
    for r in rates:
        row = []
        for gt in growths:
            row.append(None if r <= gt else value_per_share(
                fcf, base["growth_1_5"], base["growth_6_10"], gt, r, years, net_debt, shares)["per_share"])
        grid.append(row)
    implied = implied_growth(price, fcf, base["terminal_growth"], base["discount_rate"], years, net_debt, shares)
    notes = ["Free cash flow grows at growth_1_5 in the first half of the period and growth_6_10 in the second.",
             "Terminal value uses the Gordon growth formula on the final-year cash flow.",
             "Cash flows are discounted at year end. Net debt is subtracted once, at today's value.",
             "The result moves a great deal with the discount rate and terminal growth; read the grid, not one number."]
    if cases["base"]["terminal_share"] and cases["base"]["terminal_share"] > 0.75:
        notes.append("More than 75 percent of the base value comes from the terminal value.")
    return {"symbol": data.get("symbol"), "currency": data.get("currency", "USD"), "scale": data.get("scale"),
            "price": price, "years": years, "cases": cases,
            "sensitivity": {"discount_rates": rates, "terminal_growths": growths, "per_share": grid},
            "reverse": {"implied_constant_growth": implied,
                        "meaning": "Constant yearly growth in free cash flow over the explicit period that makes "
                                   "the base-case value equal today's price."},
            "notes": notes}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("inputs", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        result = run(json.loads(args.inputs.read_text(encoding="utf-8")))
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
