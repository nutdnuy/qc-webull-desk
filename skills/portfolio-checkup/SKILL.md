---
name: portfolio-checkup
description: Check how concentrated and how diversified a portfolio is, reading holdings read-only from the user's Webull account or from a list or screenshot. Use when the user runs "/portfolio-checkup" or asks "เช็กพอร์ตให้หน่อย", "พอร์ตกระจายความเสี่ยงพอไหม", "พอร์ตกระจุกตัวไหม", "ถือหุ้นเยอะไปไหม", "วิเคราะห์พอร์ต", "check my portfolio", "is my portfolio too concentrated", "am I diversified". Measures weights, sector exposure and effective number of holdings with the bundled calculator and flags what crosses adjustable thresholds.
metadata:
  version: "0.1.0"
  author: QuantCorner
---

# Portfolio checkup

Answer "where is this portfolio concentrated, and what am I really exposed to".
It describes the portfolio. It does not say what to buy or sell.

Read `references/desk-rules.md` first and run its connection gate.

## Get the holdings

Use the first source that works, and tell the user which one was used.

1. **Webull account (read-only).** `get_account_list`, then for the account the
   user picks: `get_account_positions` and `get_account_balance`. With more than
   one account, ask which, or whether to combine them.
2. **A list the user types or a screenshot.** Read symbol and market value for
   each line. Repeat the list back and ask the user to confirm before analysing.
   Never guess a value that is hard to read.

Account data is private. Use it only for this analysis. Do not send it to web
search, and do not write account numbers into the report.

## Enrich

- Sector for each stock: `get_company_profile`. For an ETF use `get_fund_brief`
  and label its sector "ETF: " plus its category; do not look through to its
  holdings unless the user asks, and then use `get_fund_holdings` for the top names only.
- Current price check with `get_stock_snapshot` when positions came from a list.
- Next earnings date for the five largest holdings: `get_stock_earnings_calendar`.

## Calculate

Write `holdings.json` as described at the top of `scripts/portfolio.py`
(`market_value` and `cost_basis` in one currency), then run:

```bash
python3 scripts/portfolio.py holdings.json --out metrics.json
```

The thresholds are rules of thumb, not standards. Tell the user they can change
them, and use theirs if they give any. Use the script's numbers as they are.

## Read the result

Cover five things, each in two or three sentences with its number:

1. **Single names:** the largest holding and the three largest together.
2. **Effective number of holdings:** what it means in plain words (a portfolio
   of ten names can behave like three).
3. **Sectors:** the largest sector, and holdings that move together although
   they sit in different sectors (for example several large technology names
   plus a Nasdaq ETF). Say this is a judgement, not a calculated correlation.
4. **Cash:** its share, without calling it too much or too little.
5. **Events ahead:** earnings dates of the largest holdings in the next 30 days.

A crossed threshold is a prompt to think. It is not an instruction to trade.
Concentration can be a deliberate choice; ask rather than assume.

## Deliver

Chat: the single most important observation first, then the five points.

Report:

- KPIs: total value, holdings, largest weight, top three weight, effective holdings, cash weight.
- `bars` of weights by holding (largest first, ten at most, the rest summed as "Others"); `highlight` the largest.
- `bars` of weights by sector.
- `table` of holdings: symbol, sector, value, weight, unrealised percent where cost is known.
- `table` of checks: what, observed, threshold, crossed (words "yes" or "no").
- `list` "Questions to ask yourself".
- `limits`: the script's notes; values are as of the stated time; other accounts and assets are not included.

Source lines name "Webull account, read-only" or "User-provided list". Close
with the reminder line from desk rules, section 8.
