---
name: stock-debate
description: Lay out the evidence for adding to, holding and trimming one US-listed stock, side by side and with equal care, from Webull data. Use when the user runs "/stock-debate" or asks "ควรซื้อเพิ่ม ถือ หรือขาย", "ขายดีไหม", "ถือต่อดีไหม", "ติดดอยทำไงดี", "ช่วยคิดหน่อยว่าควรทำอะไรกับหุ้นนี้", "should I buy more, hold or sell", "help me think through this position". Gives no verdict; it shows what would support each choice and what would change the picture.
metadata:
  version: "0.1.0"
  author: QuantCorner
---

# Stock debate

Help the user think through a position they hold or are considering. The page
gives three cases the same space and the same standard of evidence. It does not
choose between them.

Read `references/desk-rules.md` first and run its connection gate.

## Ask first, briefly

One question if it is not already known: does the user hold it, and what is the
time frame (months or years)? If account tools are connected and the user
agrees, read the position with `get_account_positions` for its weight and cost.
Do not ask why they bought it; do not judge the entry price.

## Collect

1. `get_stock_snapshot`: price, 52-week range, valuation ratios.
2. `get_financial_indicators` and `get_income_statement`, ANNUAL `count` 5 and QUARTERLY `count` 5.
3. `get_analyst_rating`, `get_analyst_target_price`, `get_stock_forecast_eps`.
4. `get_stock_industry_comparison`: peers.
5. `get_stock_earnings_calendar`: next report date.
6. `get_stock_capital_flow` if offered.
7. `get_stock_bars`, `timespan` W, `count` 52: the path of the price over a year.
8. Optional web search for the two or three most recent material news items. Link and date each.

## Build the three cases

For each of **adding**, **holding** and **trimming**, write three to five
points. Every point is one observable fact with its number and date, followed
by why it bears on that case. Rules:

- The same fact may appear in two cases with different readings. Say so.
- No case is built from opinion alone. If a case has less evidence, say that the
  evidence is thinner; do not pad it.
- Do not score or rank the cases. Do not total the points.
- Sunk cost is not evidence. The price paid does not change what the company is
  worth; it matters only for tax and for how the user feels. Say this once,
  kindly, if the user mentions being under water.

Then write **What would change the picture**: three to five specific things to
watch, each tied to a date or a number (the next report on a given date, a
margin level, a debt level).

Then **What only you can answer**: position size against the whole portfolio,
time frame, need for the cash, ability to sit through a fall. These are
questions, not advice.

## Deliver

Chat: one sentence on what the evidence is most divided about, then the three
cases in short form.

Report:

- KPIs: price, 52-week position, P/E, gap to analyst mean target, next earnings date, position weight if known.
- `columns` with the three cases, in the order adding, holding, trimming.
- `line` of 52 weekly closes.
- `list` "What would change the picture" and `list` "What only you can answer".
- `limits`: the cases are built from provider data on the stated date; none is a recommendation.

Close with the reminder line from desk rules, section 8.
