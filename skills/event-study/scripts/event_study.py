#!/usr/bin/env python3
"""What one symbol did after a kind of day, compared with every day. Stdlib only.

Usage:
    python3 event_study.py bars.txt --symbol SPY --event move --threshold -3
    python3 event_study.py bars.txt --symbol SPY --event streak --days 3 --direction down
    python3 event_study.py bars.txt --symbol SPY --event dates --dates 2025-04-03,2026-11-20
Options: --horizons 5,10,20,60  --gap 5  --out result.json

`bars.txt` holds daily closes (formats in bars_io.py).
Events:
    move    a one-day close-to-close change at or beyond --threshold percent
            (negative threshold = falls, positive = rises)
    streak  --days closes in a row in --direction (up or down)
    dates   the listed dates; a date with no bar uses the next trading day
`--gap` drops an event that starts within that many trading days of the previous
one, so one episode is not counted many times.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bars_io import BarsError, load_series  # noqa: E402


def find_events(rows, event: str, threshold: float, days: int, direction: str, dates) -> list[int]:
    closes = [c for _, c in rows]
    if event == "move":
        if threshold == 0:
            raise BarsError("--threshold cannot be zero")
        out = []
        for i in range(1, len(closes)):
            change = (closes[i] / closes[i - 1] - 1) * 100
            if (threshold < 0 and change <= threshold) or (threshold > 0 and change >= threshold):
                out.append(i)
        return out
    if event == "streak":
        if days < 2:
            raise BarsError("--days must be at least 2")
        if direction not in ("up", "down"):
            raise BarsError("--direction must be up or down")
        out = []
        for i in range(days, len(closes)):
            steps = [closes[j] - closes[j - 1] for j in range(i - days + 1, i + 1)]
            if all(s > 0 for s in steps) if direction == "up" else all(s < 0 for s in steps):
                out.append(i)
        return out
    if event == "dates":
        if not dates:
            raise BarsError("--dates is empty")
        index = [d for d, _ in rows]
        out = []
        for day in dates:
            hit = next((i for i, d in enumerate(index) if d >= day), None)
            if hit is not None:
                out.append(hit)
        return sorted(set(out))
    raise BarsError("--event must be move, streak or dates")


def describe(returns: list[float]) -> dict:
    if not returns:
        return {"n": 0}
    return {"n": len(returns), "mean": statistics.fmean(returns), "median": statistics.median(returns),
            "win_rate": sum(1 for r in returns if r > 0) / len(returns), "best": max(returns), "worst": min(returns)}


def study(rows, event: str, threshold: float = -3.0, days: int = 3, direction: str = "down",
          dates=None, horizons=(5, 10, 20, 60), gap: int = 5) -> dict:
    if len(rows) < 60:
        raise BarsError(f"{len(rows)} bars is too short; use at least 60 daily closes")
    closes = [c for _, c in rows]
    found = find_events(rows, event, threshold, days, direction, dates)
    kept, last = [], None
    for i in found:
        if last is None or i - last > gap:
            kept.append(i)
            last = i
    table = []
    for h in horizons:
        after = [(closes[i + h] / closes[i] - 1) for i in kept if i + h < len(closes)]
        baseline = [(closes[i + h] / closes[i] - 1) for i in range(len(closes) - h)]
        table.append({"horizon_days": h, "after_event": describe(after), "all_days": describe(baseline)})
    complete = min((row["after_event"]["n"] for row in table), default=0)
    notes = ["Returns are close-to-close price changes from the event day's close. Dividends are not added.",
             "The all-days row uses overlapping windows; it is a reference level, not an independent sample.",
             "A past pattern describes this sample. It is not a forecast and not a trading rule.",
             "Costs, spreads and taxes are not included."]
    if complete < 20:
        notes.insert(0, f"Only {complete} events have a full window. That is too few to tell a pattern from chance.")
    return {"first_bar": rows[0][0], "last_bar": rows[-1][0], "bars": len(rows),
            "event": {"type": event, "threshold_pct": threshold if event == "move" else None,
                      "days": days if event == "streak" else None,
                      "direction": direction if event == "streak" else None, "gap_days": gap},
            "events_found": len(found), "events_used": len(kept),
            "event_dates": [rows[i][0] for i in kept], "results": table, "notes": notes}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("bars", type=Path)
    parser.add_argument("--symbol")
    parser.add_argument("--event", required=True, choices=("move", "streak", "dates"))
    parser.add_argument("--threshold", type=float, default=-3.0)
    parser.add_argument("--days", type=int, default=3)
    parser.add_argument("--direction", default="down")
    parser.add_argument("--dates", default="")
    parser.add_argument("--horizons", default="5,10,20,60")
    parser.add_argument("--gap", type=int, default=5)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        series = load_series(args.bars)
        symbol = (args.symbol or next(iter(series))).upper()
        if symbol not in series:
            raise BarsError(f"{symbol} is not in the file")
        horizons = tuple(int(h) for h in args.horizons.split(",") if h.strip())
        if not horizons or min(horizons) < 1:
            raise BarsError("--horizons must be positive whole numbers")
        dates = [d.strip() for d in args.dates.split(",") if d.strip()]
        result = study(series[symbol], args.event, args.threshold, args.days, args.direction, dates, horizons, args.gap)
        result["symbol"] = symbol
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
