---
name: dca-plan
description: Plan regular monthly investing with the bundled calculator: what a monthly amount may grow to, or what monthly amount a goal needs, across stated return and step-up assumptions. Use when the user runs "/dca-plan" or asks "DCA เดือนละเท่าไหร่ดี", "ลงทุนเดือนละ 10,000 อีก 15 ปีจะมีเท่าไหร่", "อยากมี 5 ล้านต้องออมเดือนละเท่าไร", "วางแผน DCA", "แผนลงทุนรายเดือน", "how much should I invest each month", "what will my monthly investing grow to", "plan my DCA".
metadata:
  version: "0.1.0"
  author: QuantCorner
---

# DCA plan

Answer "if I invest this much each month, where might I end up" or "what
monthly amount does my goal need". The output is arithmetic on assumptions the
user can see and change. It is not a forecast and not a recommendation of what
to invest in.

Read `references/desk-rules.md` first. This workflow does not need Webull data,
so skip the connection gate unless the user asks for the optional part below.

## Ask, in one message

1. The goal amount, or the monthly amount, or both.
2. How many years.
3. What is already invested towards this goal (zero is fine).
4. Is the goal in today's money? (Default yes: the calculator then raises the
   target by inflation.)

Do not ask for income, debts or anything else. If the user offers more, use
only what the calculation needs.

## Assumptions

State them before calculating and let the user change any of them.

- Returns: three yearly rates, after fees. Default 4, 6 and 8 percent. These are
  round numbers to show sensitivity. They are not what any market, fund or
  product is expected to return, and the desk does not claim to know that.
- Inflation: default 2 percent a year. For a Thai goal the user may prefer a
  figure from the Bank of Thailand; if they ask, find it by web search and link it.
- Step-up: raising the monthly amount each year by 0, 5 or 10 percent.

## Calculate

Write `plan.json` as described at the top of `scripts/dca.py`, then run:

```bash
python3 scripts/dca.py plan.json --out result.json
```

Use the script's numbers as they are.

## Read the result

- With a monthly amount: the range of end values across the three returns, in
  nominal terms and in today's money, and how much of it is money paid in.
- With a goal: the first-year monthly amount needed under each return, and how
  a yearly step-up lowers the starting amount.
- With both: under which assumptions the goal is reached.
- One paragraph on what the grid hides: returns do not arrive evenly, a fall
  near the end hurts far more than one near the start, and the plan assumes the
  user keeps paying in through falls.

Do not name a product, fund or stock to put the money in. If the user asks
what to invest in, say that is a separate question and offer `/etf-compare`.

## Optional, only if the user asks

"What would this have looked like in the past with ETF X": that is a backtest,
not this plan. Offer `/event-study` for simple questions and say plainly that a
past path is one sample.

## Deliver

Chat: the answer to the user's question in one sentence with the range, then the assumptions.

Report:

- KPIs: years, monthly amount or goal, inflation assumed, the range of outcomes.
- `table` grid: returns down the side, step-ups across; cells are the end value
  in today's money, or the required first-year monthly amount.
- `bars` of end value by return assumption at zero step-up, `highlight` the middle one.
- `bars` of money paid in against growth for the middle case.
- `text` "What this plan assumes" and `text` "What the grid hides".
- Every figure's `source` is "Calculation on user inputs and stated assumptions",
  `period` the plan length, `unit` the currency.
- `limits`: the script's notes.

Close with the reminder line from desk rules, section 8.
