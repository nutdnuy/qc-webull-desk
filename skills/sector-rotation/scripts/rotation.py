#!/usr/bin/env python3
"""Relative rotation of a group of ETFs against a benchmark. Stdlib only.

Usage: python3 rotation.py bars.txt --benchmark SPY [--window 12] [--momentum 4] [--trail 4] [--out result.json]

`bars.txt` holds weekly closes for the benchmark and every member (formats in bars_io.py).

Method (stated so it can be checked; this is an RRG-style approximation, not the
proprietary JdK RS-Ratio and RS-Momentum formulas):
    rs        = member close / benchmark close
    strength  = 100 * rs / average(rs over `window` weeks)
    momentum  = 100 * strength / average(strength over `momentum` weeks)
Leading: strength >= 100 and momentum >= 100. Weakening: strength >= 100, momentum < 100.
Lagging: both below 100. Improving: strength < 100, momentum >= 100.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bars_io import BarsError, load_series  # noqa: E402


def mean(values) -> float:
    return sum(values) / len(values)


def quadrant(strength: float, momentum: float) -> str:
    if strength >= 100:
        return "Leading" if momentum >= 100 else "Weakening"
    return "Improving" if momentum >= 100 else "Lagging"


def rotate(series: dict, benchmark: str, window: int = 12, momentum: int = 4, trail: int = 4) -> dict:
    benchmark = benchmark.upper()
    if benchmark not in series:
        raise BarsError(f"benchmark {benchmark} is not in the file")
    if window < 2 or momentum < 2 or trail < 1:
        raise BarsError("window and momentum must be at least 2, trail at least 1")
    need = window + momentum + trail - 1
    bench = dict(series[benchmark])
    members, skipped = [], []
    for symbol, rows in sorted(series.items()):
        if symbol == benchmark:
            continue
        dates = [d for d, _ in rows if d in bench]
        if len(dates) < need:
            skipped.append({"symbol": symbol, "reason": f"{len(dates)} shared weeks, {need} needed"})
            continue
        own = dict(rows)
        rs = [own[d] / bench[d] for d in dates]
        strength = [100 * rs[i] / mean(rs[i - window + 1:i + 1]) for i in range(window - 1, len(rs))]
        mom = [100 * strength[i] / mean(strength[i - momentum + 1:i + 1]) for i in range(momentum - 1, len(strength))]
        strength = strength[momentum - 1:]
        used = dates[window + momentum - 2:]
        path = [{"date": d, "strength": s, "momentum": m} for d, s, m in zip(used, strength, mom)][-trail:]

        def relative(weeks: int):
            if len(dates) <= weeks:
                return None
            a, b = dates[-1], dates[-1 - weeks]
            return (own[a] / own[b]) - (bench[a] / bench[b])

        members.append({"symbol": symbol, "as_of": used[-1], "strength": strength[-1], "momentum": mom[-1],
                        "quadrant": quadrant(strength[-1], mom[-1]),
                        "previous_quadrant": quadrant(path[0]["strength"], path[0]["momentum"]),
                        "relative_return_4w": relative(4), "relative_return_12w": relative(12), "trail": path})
    if not members:
        raise BarsError("no member has enough history")
    members.sort(key=lambda m: (-m["strength"], -m["momentum"]))
    groups = {name: [m["symbol"] for m in members if m["quadrant"] == name]
              for name in ("Leading", "Weakening", "Lagging", "Improving")}
    return {"benchmark": benchmark, "as_of": max(m["as_of"] for m in members), "window_weeks": window,
            "momentum_weeks": momentum, "members": members, "quadrants": groups, "skipped": skipped,
            "notes": ["RRG-style approximation from weekly closes; it is not the proprietary JdK calculation.",
                      "Relative return is the member's return minus the benchmark's over the same weeks.",
                      "A quadrant describes the recent past. It does not predict the next move."]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("bars", type=Path)
    parser.add_argument("--benchmark", default="SPY")
    parser.add_argument("--window", type=int, default=12)
    parser.add_argument("--momentum", type=int, default=4)
    parser.add_argument("--trail", type=int, default=4)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        result = rotate(load_series(args.bars), args.benchmark, args.window, args.momentum, args.trail)
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
