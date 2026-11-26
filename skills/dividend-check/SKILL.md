---
name: dividend-check
description: Check a US-listed stock's dividend from Webull data: how much it pays, when, and whether earnings and cash flow cover it. Also screens high-yield names with the same checks. Use when the user runs "/dividend-check" or asks "หุ้นปันผลตัวนี้จ่ายไหวไหม", "ปันผลยั่งยืนไหม", "หุ้นปันผลสูงมีตัวไหน", "XD วันไหน", "ปันผล KO เท่าไหร่", "is this dividend safe", "high dividend stocks", "when is the ex-dividend date".
metadata:
  version: "0.1.0"
  author: QuantCorner
---

# Dividend check

Answer "what does this dividend pay, and can the business afford it". A high
yield is often a falling price, so the check matters more than the yield.

Read `references/desk-rules.md` first and run its connection gate.

## Two modes

- **One stock** (default): the checks below for the symbol the user names.
- **Screen:** `get_high_dividend` (`sort_by` YIELD, top 20). Remove names with a
  market value under 2 billion USD unless the user wants them, then run the
  short form of the checks on the ten largest that remain. Say that a ranking
  by yield is a list to examine, not a list to buy.

## Collect

1. `get_stock_snapshot`: price, `yield`, P/E, market value.
2. `get_stock_dividend_calendar`: declared amount, ex-dividend date, pay date, history.
3. `get_income_statement` ANNUAL `count` 5: net income, shares, EPS.
4. `get_cash_flow` ANNUAL `count` 5: operating cash flow, capital expenditure, dividends paid.
5. `get_balance_sheet` ANNUAL `count` 2: debt and cash.
6. `get_financial_indicators` ANNUAL `count` 5.
7. `get_company_profile`: sector, because the right measure differs by sector.

## Checks

1. **Earnings cover:** dividends per share divided by EPS, for each of five
   years. Above 100 percent means the company paid out more than it earned that year.
2. **Cash cover:** dividends paid divided by free cash flow (operating cash flow
   minus capital expenditure). This is the stricter test.
3. **Record:** has the dividend per share risen, held or been cut over the years returned?
4. **Balance sheet:** net debt direction while the dividend was paid.
5. **Where the yield comes from:** compare today's yield with the price's place
   in its 52-week range. A yield that is high because the price fell hard is a
   different thing from one that is high because the payout grew.

Sector notes: for REITs, payout against net income is misleading; say the usual
measure is funds from operations, which these tools may not provide, and that
the cover check is therefore incomplete. For banks, free cash flow is not
meaningful; use earnings cover only.

Report what each check shows. Do not label the dividend "safe" or "unsafe";
describe the cover and the trend and let the user conclude.

For a Thai investor: dividends on US shares are subject to US withholding tax
for non-US investors, and the yield shown is before tax. State it as a fact to
confirm with the broker, not as tax advice.

## Deliver

Chat: yield, the two cover ratios for the latest year, and the trend, in three sentences.

Report:

- KPIs: yield, dividend per share (last twelve months), earnings cover, cash cover, next ex-dividend date in ICT.
- `bars` of dividend per share by year, `highlight` the latest.
- `table` by year: EPS, dividend per share, payout percent, free cash flow, dividends paid, cash cover percent.
- `table` of upcoming and recent dividend dates.
- Screen mode: one `table` of the names with yield, market value, the two cover ratios and sector.
- `limits`: provider yields may be trailing or forward (say which if the tool
  tells you, or that it does not); special dividends distort a single year; a
  record of payments is not a promise of future ones.

Close with the reminder line from desk rules, section 8.
