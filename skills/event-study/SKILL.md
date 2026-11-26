---
name: event-study
description: Show what a US stock or ETF did after a kind of day (a sharp fall or rise, a run of up or down days, or dates the user lists) and compare it with ordinary days, from Webull daily prices and the bundled calculator. Use when the user runs "/event-study" or asks "หลังร่วงแรงแบบนี้มักเป็นยังไง", "ลง 3 วันติดแล้วมักเด้งไหม", "หลัง Fed ลดดอกเบี้ยตลาดเป็นยังไง", "สถิติย้อนหลัง", "what usually happens after a 3% drop", "after three down days", "historical odds after this event".
metadata:
  version: "0.1.0"
  author: QuantCorner
---

# Event study

Answer "after days like this one, what did the price do next, and was that any
different from an ordinary day". The honest answer is often "not clearly"; say
so when the numbers say so.

Read `references/desk-rules.md` first and run its connection gate.

## Define the event before looking

Agree the definition with the user, then keep it. Changing the definition after
seeing the result until something looks good is how false patterns are made;
if the user wants to try several, report all of them.

| Event | Flag | Example |
|---|---|---|
| One-day move | `--event move --threshold -3` | closes down 3 percent or more |
| Streak | `--event streak --days 3 --direction down` | three lower closes in a row |
| Listed dates | `--event dates --dates 2025-04-03,2026-11-20` | Fed decisions, earnings days |

For listed dates, the user supplies them or they come from a named, linked
source (for example the Federal Reserve's calendar). Do not list dates from memory.

## Collect

`get_stock_bars` with `timespan` D and `count` 1200 (about 4.7 years, the most
the tool gives), the right `category`, `real_time_required` off. Say plainly
that the sample covers only this period and which market conditions it contained.

## Calculate

Save the closes to `bars.txt`, either the tool response as it came or the
compact form:

```
# SPY
2026-11-24,712.10
2026-11-25,716.70
```

Check the first, last and two middle closes against the tool response. Then run, for example:

```bash
python3 scripts/event_study.py bars.txt --symbol SPY --event move --threshold -3 --out study.json
```

`--horizons 5,10,20,60` and `--gap 5` are the defaults. Use the script's
numbers as they are.

## Read the result

For each horizon compare **after the event** with **all days**: mean, median,
share of positive outcomes, best and worst.

- Lead with the number of events. Under 20 complete windows, say first that the
  sample is too small to separate a pattern from chance, and keep saying it.
- A higher win rate with a similar or worse worst case is not a free lunch;
  show the worst case next to the win rate every time.
- Mean and median far apart means a few outliers carry the mean.
- Markets rose over most multi-year samples, so "positive after the event" is
  only interesting if it differs from all days.
- Never turn the result into a rule ("buy after three down days").

## Deliver

Chat: number of events, the comparison at one horizon the user cares about, and the main caveat.

Report:

- KPIs: events used, sample start and end, bars, win rate after event and for all days at 20 days.
- `table`: horizon, n, mean, median, win rate, best, worst, for events and for all days (signed percentages).
- `bars` of median return by horizon after the event; a second `bars` for all days.
- `table` of event dates (the most recent twenty).
- `limits`: the script's notes, the sample period, and that prices are adjusted by the provider.

Close with the reminder line from desk rules, section 8.
