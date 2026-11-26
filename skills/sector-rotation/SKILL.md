---
name: sector-rotation
description: Place the eleven US sector ETFs on a relative-rotation map against the S&P 500, from Webull weekly prices and the bundled calculator. Use when the user runs "/sector-rotation" or asks "เงินไหลไปกลุ่มไหน", "กลุ่มไหนนำตลาด", "sector rotation", "กลุ่มไหนกำลังแข็งแรง", "ทำ RRG ให้หน่อย", "which sectors are leading", "which sectors are lagging", "relative rotation". Also works for any group of symbols against any benchmark.
metadata:
  version: "0.1.0"
  author: QuantCorner
---

# Sector rotation

Answer "which sectors have been stronger or weaker than the market lately, and
in which direction are they moving".

Read `references/desk-rules.md` first and run its connection gate.

## Universe

Default: benchmark SPY and the eleven Select Sector SPDR ETFs.

| Symbol | Sector | Symbol | Sector |
|---|---|---|---|
| XLK | Technology | XLV | Health care |
| XLF | Financials | XLY | Consumer discretionary |
| XLC | Communication services | XLP | Consumer staples |
| XLI | Industrials | XLE | Energy |
| XLU | Utilities | XLB | Materials |
| XLRE | Real estate | | |

The user may give another group and benchmark (for example country ETFs
against ACWI, or their own holdings against SPY). At least three members.

## Collect

`get_stock_bars` with `category` US_ETF, `timespan` W, `count` 30, at most 20
symbols per call; the benchmark must be in every call or fetched once and
reused. Leave `real_time_required` off so the unfinished week is not included.
If the first row is the current, unfinished week anyway, drop it and say so.

## Calculate

Save the closes to `bars.txt`. Either save the tool response as it came, or
write the compact form (cheaper):

```
# SPY
2026-11-13,754.37
2026-11-20,689.81
# XLK
2026-11-13,170.28
```

Then run:

```bash
python3 scripts/rotation.py bars.txt --benchmark SPY --out rotation.json
```

Check two closes per symbol against the tool response before running. Use the
script's numbers as they are. Members it lists under `skipped` are left out of
the map and named in the report.

## Read the result

- **Leading:** stronger than the benchmark and still gaining.
- **Weakening:** stronger, but losing pace.
- **Lagging:** weaker and still losing.
- **Improving:** weaker, but gaining.

Report members that changed quadrant over the trail (`previous_quadrant`
differs from `quadrant`), and the 4-week and 12-week relative returns that sit
behind the picture. Note how tightly the members cluster around 100: when all
are close to the centre there is little rotation to speak of.

The method is an RRG-style approximation from weekly closes. Say this in the
report; do not call it RRG without the qualifier. A quadrant describes recent
weeks and does not forecast the next ones.

## Deliver

Chat: which sectors lead and lag, and the one that changed most, in three sentences.

Report:

- KPIs: number of members in each quadrant, as-of week.
- `scatter` with `centre` [100, 100], `x_label` "Relative strength", `y_label`
  "Momentum", `quadrants` ["Improving", "Leading", "Lagging", "Weakening"];
  `highlight` the member furthest into Leading.
- `table`: symbol, sector, quadrant, previous quadrant, strength, momentum,
  relative return 4 weeks, relative return 12 weeks (signed percentages).
- `bars` of 12-week relative return (signed).
- `limits`: the script's notes; sector ETFs are weighted by company size, so
  one or two giants can drive a sector.

Close with the reminder line from desk rules, section 8.
