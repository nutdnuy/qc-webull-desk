---
name: stock-card
description: One-page card that introduces a US-listed company or ETF from Webull data. Use when the user runs "/stock-card" or asks "หุ้นตัวนี้คือใคร", "ขอข้อมูลหุ้น NVDA", "ทำความรู้จักหุ้น", "บริษัทนี้ทำอะไร", "สรุปหุ้นตัวนี้ให้หน่อย", "tell me about this stock", "who is this company", "give me a snapshot of AAPL". Covers what the company does, price against its 52-week range, valuation and profitability, analyst view, peers and the next earnings date.
metadata:
  version: "0.1.0"
  author: QuantCorner
---

# Stock card

Answer "who is this company and where does it stand today" on one page.

Read `references/desk-rules.md` first and run its connection gate.

## Inputs

One symbol. If the user gives a company name, resolve it with `get_instruments`
and confirm the symbol when more than one matches. For an ETF, say that
`/etf-compare` suits it better and continue only with the parts that apply.

## Collect

Call these for the symbol; skip any the host does not offer and say which.

1. `get_company_profile`: business, sector, industry.
2. `get_stock_snapshot`: price, change, 52-week high and low, P/E, P/B, P/S, yield, market value.
3. `get_financial_indicators` with `type` ANNUAL, `count` 5: margins, ROE, ROA, debt to assets.
4. `get_income_statement` with `type` ANNUAL, `count` 5: revenue and net income.
5. `get_analyst_rating` and `get_analyst_target_price`.
6. `get_stock_industry_comparison`: peers. If the group holds only tiny
   companies or empty values, leave the peer table out and say why.
7. `get_stock_earnings_calendar`: the latest report, with reported and
   estimated EPS, and the next report date when the tool gives one.

## Work out

- Position in the 52-week range: (price minus low) divided by (high minus low).
- Revenue and net income change over the years returned. Name the fiscal years.
- Gap between price and the analyst mean target, with the number of analysts if given.
  Call it what analysts published, not what the stock is worth.
- Two or three plain observations that the figures support, and one open question.

Do not rate the stock. Do not say cheap or expensive without the comparison
that shows it (own history or the named peers).

## Deliver

Chat: three to five sentences that answer first, then the key figures with dates.

Report (`render_report.py`, contract in desk rules section 7):

- KPIs: price, 52-week position, market value, P/E, net margin, latest or next report date.
- `bars` of revenue by fiscal year; `highlight` the latest year.
- `table` of peers: company, market value, P/E, and the sort measure used.
- `table` of analyst view: ratings count by bucket, mean, high and low target.
- `text` "What the data shows" and `list` "Open questions".
- `limits`: provider data may lag filings; ratios follow the provider's definitions.

Close with the reminder line from desk rules, section 8.
