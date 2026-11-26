---
name: earnings-check
description: Review a US-listed company's latest quarter against expectations and its own trend, from Webull data. Use when the user runs "/earnings-check" or asks "งบไตรมาสล่าสุดเป็นยังไง", "งบออกแล้วดีไหม", "สรุปงบ NVDA", "กำไรโตไหม", "งบดีกว่าคาดไหม", "how were the earnings", "did they beat", "summarise the latest quarter". Compares reported EPS with the analyst estimate, shows revenue, margin and cash flow over recent quarters, and lists what to watch next.
metadata:
  version: "0.1.0"
  author: QuantCorner
---

# Earnings check

Answer "how did the latest quarter go, against what was expected and against
the company's own past".

Read `references/desk-rules.md` first and run its connection gate.

## Collect

1. `get_stock_earnings_calendar`: report dates, and for past quarters the
   reported and estimated EPS and revenue (`eps_actual`, `eps_est`, `rev_actual`,
   `rev_est`). If it gives a next report date within seven days, say the figures
   below are about to be replaced; if it gives none, say the next date is not provided.
2. `get_income_statement`, `get_cash_flow`, `get_balance_sheet` with `type`
   QUARTERLY, `count` 8.
3. `get_financial_indicators` with `type` QUARTERLY, `count` 8.
4. `get_stock_forecast_eps`: estimates for coming periods.
5. `get_financial_alert` if offered.
6. `get_stock_snapshot`: price now.
7. Optional context by web search: the company's own release or the filing in
   `get_stock_filings`. Link it and date it. Management's words are quoted, not paraphrased into facts.

## Work out

- **Against expectations:** reported EPS and revenue minus their estimates, in
  currency and percent of the estimate, from the earnings calendar. If the tool
  gives no estimate for that quarter, say the comparison cannot be made. Do not
  look one up from memory.
- **Against itself:** revenue, net income and operating cash flow against the
  same quarter a year earlier, and the direction over eight quarters. Compare
  like with like: same fiscal quarter, because many businesses are seasonal.
- **Quality:** operating cash flow next to net income; a large or growing gap
  is worth one sentence. Margin now against the eight-quarter range.
- **Balance sheet:** cash and debt direction, in one line.

Keep "beat" and "missed" as statements about the estimate only. They say
nothing about whether the stock goes up.

## Deliver

Chat: the answer in two sentences, then the three comparisons.

Report:

- KPIs: revenue, change on the year, EPS reported, EPS estimate, net margin, report date.
- `bars` of quarterly revenue (eight quarters), `highlight` the latest.
- `table` of the eight quarters: revenue, net income, net margin, operating cash flow.
- `table` of EPS and revenue: estimate, reported, difference, for each quarter the calendar returns.
- `list` "What to watch next" with the next report date.
- `limits`: provider figures may differ from the filing through restatements
  and definitions; adjusted (non-GAAP) and reported EPS are not the same thing,
  so say which the tool returned or that it does not say.

Close with the reminder line from desk rules, section 8.
