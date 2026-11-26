---
name: etf-compare
description: Compare US-listed ETFs for one theme or index from Webull fund data. Use when the user runs "/etf-compare" or asks "ETF ตัวไหนดี", "VOO กับ SPY ต่างกันยังไง", "อยากลงทุน S&P 500 ซื้อ ETF ไหน", "ETF เซมิคอนดักเตอร์มีตัวไหนบ้าง", "เทียบ QQQ กับ QQQM", "which ETF should I look at", "compare these ETFs", "ETFs for a theme". Compares cost, size, holdings overlap and concentration, returns over matching periods and distributions. It does not pick one.
metadata:
  version: "0.1.0"
  author: QuantCorner
---

# ETF compare

Answer "these ETFs sound alike; how do they actually differ".

Read `references/desk-rules.md` first and run its connection gate.

## Candidates

- The user names two to five ETFs: use those.
- The user names a theme or index: propose three to five well-known ETFs for
  it, say they are candidates the user should confirm, and check each exists
  with `get_instruments` (`category` US_STOCK, `sub_category` ETF) before going
  on. Drop any the tool does not return and say so. Do not include leveraged or
  inverse ETFs unless the user asks; if they do, explain in one line that those
  reset daily and are not built for holding over long periods.

## Collect, for each ETF

1. `get_fund_brief`: issuer, inception, objective, expense ratio, assets.
2. `get_fund_performance`: returns by period.
3. `get_fund_holdings`: top holdings and their weights; `get_fund_allocation`: sector and country.
4. `get_fund_dividends`: distributions.
5. `get_fund_rating` if offered.
6. `get_stock_snapshot` (`US_ETF`): price, volume, yield.
7. `get_stock_bars` (`US_ETF`, `timespan` W, `count` 156) for a shared-period line.

If a field is missing for one ETF, leave that cell as "not provided". Do not
fill it from memory.

## Work out

- **Cost:** expense ratio, and what the difference costs per 100,000 units of
  currency per year. That is a multiplication; do it with code or state it as approximate.
- **What is inside:** weight of the top ten, number of holdings, and overlap,
  meaning the names two ETFs share within their top holdings and the smaller of
  the two weights summed. Say the overlap covers top holdings only.
- **Returns:** only over periods every ETF has. A fund launched in 2023 has no
  five-year return; do not compare it on one.
- **Size and trading:** assets and average volume. Small and thinly traded
  funds can have wider spreads.
- **Income:** yield and how often it pays.
- **For a Thai investor:** these are US-listed and priced in dollars, so the
  baht return also depends on the exchange rate; US dividends to non-US
  investors are subject to US withholding tax. State both as facts to check
  with the broker and a tax adviser, not as advice.

Lay out the trade-offs. Do not rank the ETFs or name a winner. Past return
gets one line in the table, not the headline.

## Deliver

Chat: the two or three differences that matter most, in plain words.

Report:

- `table` side by side: issuer, inception, expense ratio, assets, holdings count, top-ten weight, yield.
- `table` of returns over shared periods.
- `bars` of expense ratio, `highlight` the lowest.
- `table` of overlap between each pair.
- `line` of weekly closes rebased to 100 at the first shared week (rebase with code).
- `list` "Questions that decide it" (holding period, need for income, cost sensitivity).
- `limits`: fund data may lag the issuer's own page; holdings change; the issuer's fact sheet is the source to check before acting.

Close with the reminder line from desk rules, section 8.
