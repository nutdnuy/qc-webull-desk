#!/usr/bin/env python3
"""Read closing prices into {SYMBOL: [(date, close), ...]}, oldest first. Stdlib only.

Accepted inputs:
1. Compact text, the cheapest to write by hand:
       # SPY
       2026-11-13,754.37
       2026-11-20,689.81
2. The Webull get_stock_bars payload saved as it came:
       {"result": [{"symbol": "SPY", "result": [{"time": "2026-11-25T05:00:00.000+0000", "close": "716.70"}]}]}
3. Plain JSON: {"SPY": [["2026-11-13", 754.37]]} or {"SPY": [{"date": "2026-11-13", "close": 754.37}]}

Generated copy: edit shared/bars_io.py and run tools/build.py.
"""
from __future__ import annotations

import json
from pathlib import Path


class BarsError(ValueError):
    pass


def _clean(symbol: str, rows) -> list[tuple[str, float]]:
    seen: dict[str, float] = {}
    for row in rows:
        if isinstance(row, dict):
            day, close = row.get("date") or row.get("time"), row.get("close")
        else:
            day, close = row[0], row[1]
        day = str(day)[:10]
        if len(day) != 10 or day[4] != "-" or day[7] != "-":
            raise BarsError(f"{symbol}: {day!r} is not a YYYY-MM-DD date")
        try:
            value = float(close)
        except (TypeError, ValueError):
            raise BarsError(f"{symbol} {day}: close {close!r} is not a number")
        if not value > 0:
            raise BarsError(f"{symbol} {day}: close must be positive")
        seen[day] = value
    if not seen:
        raise BarsError(f"{symbol}: no bars")
    return sorted(seen.items())


def _from_text(text: str) -> dict[str, list]:
    out: dict[str, list] = {}
    symbol = None
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            symbol = line.lstrip("#").strip().upper()
            if not symbol:
                raise BarsError(f"line {n}: symbol is missing after #")
            out.setdefault(symbol, [])
            continue
        if symbol is None:
            raise BarsError(f"line {n}: put '# SYMBOL' before the first row")
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 2:
            raise BarsError(f"line {n}: expected date,close")
        out[symbol].append((parts[0], parts[1]))
    return out


def _from_json(data) -> dict[str, list]:
    if isinstance(data, dict) and isinstance(data.get("result"), list):
        data = data["result"]
    if isinstance(data, dict) and isinstance(data.get("series"), dict):
        data = data["series"]
    if isinstance(data, list):
        out = {}
        for block in data:
            if not isinstance(block, dict) or "symbol" not in block or not isinstance(block.get("result"), list):
                raise BarsError("expected a list of {symbol, result: [bars]} blocks")
            out[str(block["symbol"]).upper()] = block["result"]
        return out
    if isinstance(data, dict):
        return {str(k).upper(): v for k, v in data.items()}
    raise BarsError("unrecognised bars JSON")


def load_series(path: Path) -> dict[str, list[tuple[str, float]]]:
    text = Path(path).read_text(encoding="utf-8")
    stripped = text.lstrip()
    raw = _from_json(json.loads(text)) if stripped[:1] in "{[" else _from_text(text)
    if not raw:
        raise BarsError("no series found")
    return {symbol: _clean(symbol, rows) for symbol, rows in raw.items()}
