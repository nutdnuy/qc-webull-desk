---
name: market-pulse
description: Read today's US market from Webull's ranking and sector tools. Use when the user runs "/market-pulse" or asks "วันนี้ตลาดเป็นยังไง", "หุ้นอะไรขึ้นแรง", "หุ้นอะไรลงแรง", "กลุ่มไหนนำตลาด", "หุ้นทำนิวไฮ", "วอลุ่มเข้าตัวไหน", "what is the market doing", "top gainers", "top losers", "most active", "new 52-week highs". Shows breadth by sector, gainers and losers, most active names and 52-week highs and lows, with the session time stated.
metadata:
  version: "0.1.0"
  author: QuantCorner
---

# Market pulse

Answer "what is the US market doing right now, and how broad is the move".

Read `references/desk-rules.md` first and run its connection gate.

## Collect

1. `get_stock_snapshot` for SPY, QQQ, DIA, IWM (`US_ETF`): level, change,
   `trade_status`, timestamp.
2. `get_market_sectors` with `period` D1, then D5, sorted by change. The
   response gives advancing, declining and unchanged counts per sector.
3. `get_gainers_losers`, `rank_type` DAY_1: top 10 with `direction` DESC, then
   top 10 with ASC. Use PRE_MARKET or AFTER_MARKET when the regular session is closed.
4. `get_most_active`: top 10.
5. `get_52_week_high_low`: counts and leading names for new highs and new lows.
6. If the user asks about one sector, `get_market_sectors_detail` for it.

## Work out

- **Breadth:** total advancing against declining across sectors, and how many
  sectors rose. An index that is up while most stocks fell is a narrow move; say so.
- **Size effect:** large-cap (SPY) against small-cap (IWM) change.
- **Leaders and laggards:** the three strongest and weakest sectors, one day and five days.
- **Movers:** for gainers and losers, flag tiny companies. A 40 percent move in a
  micro-cap says little about the market; show market value beside each name.

Describe; do not explain. Give a reason for a move only when a linked, dated
news item supports it. Ranking lists are not ideas to buy. Say this once, in
plain words, where the lists appear.

## Deliver

Chat: the session in two sentences (direction, breadth), then leaders and laggards.

Report:

- KPIs: the four index ETFs with signed change, advancers, decliners.
- `bars` of one-day sector change (signed), `highlight` the strongest.
- `table` of sectors: one-day change, five-day change, advancing, declining.
- `table` of gainers and `table` of losers: symbol, name, change percent, market value.
- `table` of most active.
- `text` "Breadth" with the counts.
- `limits`: sector groups follow the provider's classification, which differs
  from the eleven GICS sectors; rankings change by the minute; delayed by the
  minutes the tool states.

Close with the reminder line from desk rules, section 8.
