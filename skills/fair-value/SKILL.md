---
name: fair-value
description: Estimate what a US-listed company may be worth from its cash flows, in three cases with a sensitivity grid and a reverse check, using Webull data and the bundled calculator. Use when the user runs "/fair-value" or asks "หุ้นนี้ควรมีมูลค่าเท่าไหร่", "ราคานี้แพงไปไหม", "ทำ DCF ให้หน่อย", "มูลค่าที่เหมาะสมของ AAPL", "ตลาดคาดการเติบโตไว้เท่าไร", "what is this stock worth", "run a DCF", "is the price justified", "what growth is priced in".
metadata:
  version: "0.1.0"
  author: QuantCorner
---

# Fair value

Answer "what do the cash flows suggest this business is worth, and what would
have to be true for today's price to make sense". The output is a range that
depends on stated assumptions. It is never a price target.

Read `references/desk-rules.md` first and run its connection gate.

## When this method does not fit

Stop and say so, then offer `/stock-card` or `/stock-debate`:

- free cash flow is negative or swings in sign over the last five years;
- banks, insurers and other financials, where free cash flow is not meaningful;
- an ETF or a fund.

## Collect

1. `get_cash_flow` ANNUAL, `count` 5: operating cash flow and capital expenditure.
   Free cash flow = operating cash flow minus capital expenditure. Show both lines.
2. `get_balance_sheet` ANNUAL, `count` 1: debt and cash. Net debt = total debt
   minus cash and short-term investments. Negative means net cash.
3. `get_stock_snapshot`: price and `total_shares`.
4. `get_income_statement` ANNUAL, `count` 5 and `get_stock_forecast_eps`: growth context only.

## Agree the assumptions

Show the five-year free cash flow history and its growth, then propose three
cases and ask the user to confirm or change them before calculating.

- `base_fcf`: the latest year, or the three-year average when one year is unusual. Say which and why.
- Growth for years 1 to 5 and 6 to 10: anchored on the company's own history and
  on analyst growth where the tool gives it. Bear below the history, bull above.
- Terminal growth: at or below long-run nominal growth of the economy. Above 3
  percent needs a reason in words.
- Discount rate: the return the user requires. Offer 8 to 11 percent as a
  starting range for a large US company and let the user choose. Do not present
  a rate as a fact.

Label every one of these as an assumption in chat and in the report.

## Calculate

Write `inputs.json` as described at the top of `scripts/dcf.py`, keeping money
and share count in the same scale, then run:

```bash
python3 scripts/dcf.py inputs.json --out result.json
```

Use the script's numbers as they are. Do not adjust them by hand. If the script
reports an error, fix the input and say what was wrong.

## Deliver

Chat: the range from bear to bull, where today's price sits in it, and the
implied growth from the reverse check, in three sentences.

Report:

- KPIs: price, bear, base, bull value per share, implied growth, terminal share of base value.
- `bars` of value per share for the three cases and the price; `highlight` the price.
- `table` of assumptions by case.
- `table` sensitivity: discount rate down the side, terminal growth across.
- `bars` of free cash flow for the five history years.
- `text` "What would have to be true": the reverse check in words, compared with the history.
- `limits`: the script's notes, plus that a small change in the discount rate moves the result a lot.

Close with the reminder line from desk rules, section 8.
