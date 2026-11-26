---
name: morning-brief
description: Morning page for a Thai investor in US markets, built around the user's own holdings and Webull watchlists. Use when the user runs "/morning-brief" or asks "สรุปข่าวเช้า", "เมื่อคืนตลาดเป็นไง", "มีอะไรกระทบหุ้นที่ถือไหม", "สรุปตลาดเมื่อคืน หุ้น NVDA TSLA", "morning brief", "what happened overnight", "any news on my stocks". Covers the overnight session, moves in the user's names, sectors, and this week's earnings and dividend dates, timed in Bangkok time.
metadata:
  version: "0.1.0"
  author: QuantCorner
---

# Morning brief

Answer "what happened overnight, and does any of it touch what I hold or
follow", in a page that reads well on a phone in two minutes.

Read `references/desk-rules.md` first and run its connection gate.

## Whose names

In this order, stopping at the first that gives a list:

1. Symbols the user typed in the request.
2. Holdings from `get_account_positions`, if account tools are connected.
3. Watchlists from `get_watchlists` and `get_watchlist_instruments`; ask which list when there are several.
4. None of these: do the market part only and say how to add names next time.

Keep at most fifteen names; say which were left out and why (smallest weights first).

## Collect

1. Market: `get_stock_snapshot` for SPY, QQQ, DIA, IWM (`US_ETF`). Read
   `trade_status` and the timestamp; say whether the figures are from a closed
   session, pre-market or live.
2. Sectors: `get_market_sectors`, `period` D1.
3. Movers: `get_gainers_losers` (`rank_type` DAY_1, both directions, top 5) and `get_most_active`.
4. The user's names: `get_stock_snapshot` in batches, split by `US_STOCK` and `US_ETF`.
5. Calendar for the user's names: `get_stock_earnings_calendar` and
   `get_stock_dividend_calendar`; keep events in the next seven days.
6. News by web search for: the market overall, and each of the user's names
   that moved more than 3 percent or reports this week. Two items at most per
   name, from a named publisher, each with link and publication time. If web
   search is off, say so and leave the news part out. Do not write news from memory.

## Write

- **Top line:** what the session was, in one sentence, with index moves as signed percentages.
- **Your names:** sorted by size of move. One line each: move, and the reason
  only if a linked news item supports it. If no reason was found, say "no
  reported reason found". Never invent a cause for a price move.
- **Sectors:** the two strongest and two weakest, by the tool's figures.
- **This week:** earnings and ex-dividend dates for the user's names, in Bangkok
  time, noting when a US evening release falls on the next Thai morning.
- **Not covered:** names with no data, and parts skipped.

Times: convert to ICT and write the date, because the US session spans two Thai
calendar days.

## Deliver

Chat: the top line and the three largest moves in the user's names.

Report:

- KPIs: the four index ETFs with signed change.
- `table` "Your names": symbol, price, change percent, note.
- `bars` of sector changes (signed), `highlight` the strongest.
- `table` "This week": date in ICT, symbol, event.
- `list` of news items as "publisher, time, headline, link".
- `limits`: quotes may be delayed by the minutes the tool states; a move and a
  headline on the same day do not prove one caused the other.

To make this a habit, the user can schedule the prompt in their host; the desk
does not schedule anything itself. Close with the reminder line from desk rules, section 8.
