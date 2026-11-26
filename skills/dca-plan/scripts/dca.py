#!/usr/bin/env python3
"""Monthly investing plan: what a monthly amount may grow to, or what monthly
amount a goal needs, under stated return assumptions. Stdlib only.

Usage: python3 dca.py plan.json [--out result.json]

Input:
{
  "currency": "THB", "years": 15, "initial": 100000,
  "monthly": 10000,            # give this, or goal_amount, or both
  "goal_amount": 5000000,      # in today's money when goal_in_todays_money is true
  "goal_in_todays_money": true,
  "inflation_pct": 2.0,
  "returns_pct": [4, 6, 8],    # yearly return assumptions, after fees
  "step_ups_pct": [0, 5, 10]   # yearly increase of the monthly amount
}
Every return and inflation figure is an assumption. Nothing here is a forecast.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


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


def future_value(initial: float, monthly: float, years: int, yearly_return: float, step_up: float) -> tuple[float, float]:
    """End-of-month contributions, monthly compounding at the geometric monthly rate."""
    rate = (1 + yearly_return) ** (1 / 12) - 1
    balance, paid, amount = initial, initial, monthly
    for month in range(1, years * 12 + 1):
        balance = balance * (1 + rate) + amount
        paid += amount
        if month % 12 == 0:
            amount *= 1 + step_up
    return balance, paid


def required_monthly(goal: float, initial: float, years: int, yearly_return: float, step_up: float) -> float:
    if future_value(initial, 0.0, years, yearly_return, step_up)[0] >= goal:
        return 0.0
    lo, hi = 0.0, goal
    for _ in range(80):
        mid = (lo + hi) / 2
        if future_value(initial, mid, years, yearly_return, step_up)[0] >= goal:
            hi = mid
        else:
            lo = mid
    return hi


def plan(data: dict) -> dict:
    years = int(number(data.get("years"), "years", 1))
    if years > 60:
        raise InputError("years must be 60 or fewer")
    initial = number(data.get("initial", 0), "initial", 0)
    inflation = number(data.get("inflation_pct", 2.0), "inflation_pct", -5) / 100
    returns = [number(v, "returns_pct", -50) / 100 for v in data.get("returns_pct", [4, 6, 8])]
    steps = [number(v, "step_ups_pct", 0) / 100 for v in data.get("step_ups_pct", [0, 5, 10])]
    if not returns or not steps:
        raise InputError("returns_pct and step_ups_pct need at least one value each")
    monthly = data.get("monthly")
    goal = data.get("goal_amount")
    if monthly is None and goal is None:
        raise InputError("give monthly, goal_amount, or both")
    deflator = (1 + inflation) ** years
    out = {"currency": data.get("currency", "THB"), "years": years, "initial": initial,
           "inflation_pct": inflation * 100, "returns_pct": [r * 100 for r in returns],
           "step_ups_pct": [s * 100 for s in steps]}
    if monthly is not None:
        monthly = number(monthly, "monthly", 0)
        grid = []
        for r in returns:
            row = []
            for s in steps:
                value, paid = future_value(initial, monthly, years, r, s)
                row.append({"end_value": value, "end_value_todays_money": value / deflator,
                            "paid_in": paid, "growth": value - paid})
            grid.append(row)
        out["projection"] = {"monthly": monthly, "grid": grid}
    if goal is not None:
        goal = number(goal, "goal_amount", 1)
        todays = bool(data.get("goal_in_todays_money", True))
        target = goal * deflator if todays else goal
        grid = [[required_monthly(target, initial, years, r, s) for s in steps] for r in returns]
        out["goal"] = {"goal_amount": goal, "goal_in_todays_money": todays, "target_at_end": target,
                       "required_first_year_monthly": grid}
        if monthly is not None:
            out["goal"]["reached"] = [[cell["end_value"] >= target for cell in row] for row in out["projection"]["grid"]]
    out["notes"] = ["Rows are the yearly return assumptions; columns are the yearly step-up of the monthly amount.",
                    "Contributions are made at each month end. Returns are constant; real markets are not.",
                    "A constant return hides the order of good and bad years, which matters most near the end.",
                    "Taxes, fees beyond those in the return assumption, and currency moves are not included."]
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("plan", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        result = plan(json.loads(args.plan.read_text(encoding="utf-8")))
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
