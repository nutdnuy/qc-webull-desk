---
name: start
description: Front door of QuantCorner Desk for Webull. Use when the user runs "/start", is new to the plugin, or asks what it can do or which command to use, for example "เริ่มต้นใช้งาน", "ปลั๊กอินนี้ทำอะไรได้บ้าง", "มีคำสั่งอะไรบ้าง", "ใช้คำสั่งไหนดี", "what can this plugin do", "show me the menu", "help me get started". Checks the Webull connection, guides people without a Webull account, shows the twelve workflows and routes the user to one.
metadata:
  version: "0.1.0"
  author: QuantCorner
---

# Start

Get a new user to the right workflow in under a minute. Do no research here and
give no view on any security.

Read `references/desk-rules.md` first. It holds the connection gate, the partner
block and the voice rules.

## If the user already named a task

Do not show the menu. Say in one line which workflow fits, run the connection
gate, then follow that workflow's own skill.

## Otherwise

Reply in the user's language; Thai if they only typed `/start`.

1. **One line of welcome.** The desk reads data from the user's own Webull
   connection, does the legwork and shows the evidence. The decision stays with
   the user.
2. **Connection gate** (desk rules, section 2). Report the result in one line:
   connected, or what is missing. A user without a Webull account gets the
   partner block once, with its disclosure, then the connection steps.
3. **The menu** below, one line per workflow.
4. **One question** with the host's question tool: "วันนี้อยากเริ่มจากเรื่องไหน" /
   "What would you like to start with?" with four choices: ทำความรู้จักหุ้นหรือ ETF
   / Understand a stock or ETF; เช็กพอร์ตของฉัน / Check my portfolio; ดูภาวะตลาด /
   Read the market; วางแผนลงทุนรายเดือน / Plan monthly investing.
5. Narrow to one workflow, give one copy-ready example prompt with the user's
   details filled in, and offer to run it now.

## Menu

Thai:

**เข้าใจหุ้นและ ETF**
- `/stock-card` หุ้นตัวนี้คือใคร ราคาและตัวเลขสำคัญเป็นอย่างไร ได้การ์ดสรุป 1 หน้า
- `/earnings-check` งบไตรมาสล่าสุดเทียบกับที่ตลาดคาด ได้รายงาน 1 หน้า
- `/fair-value` ตามกระแสเงินสด หุ้นนี้ควรมีมูลค่าเท่าไร ได้ 3 กรณีและตารางความอ่อนไหว
- `/stock-debate` หลักฐานฝั่งซื้อเพิ่ม ถือ และลด มีอะไรบ้าง ได้หน้าเทียบ 3 มุม
- `/etf-compare` ETF ธีมเดียวกันต่างกันตรงไหน ได้ตารางเทียบ
- `/dividend-check` ปันผลของหุ้นนี้มาจากไหน และจ่ายไหวไหม ได้หน้าเช็กปันผล

**ดูแลพอร์ต**
- `/portfolio-checkup` พอร์ตกระจุกตัวตรงไหน อ่านจากบัญชี Webull ของคุณแบบดูอย่างเดียว
- `/morning-brief` เช้านี้มีอะไรเกี่ยวกับหุ้นที่ถือและที่ติดตาม ได้หน้าสรุปอ่านบนมือถือ

**อ่านภาวะตลาด**
- `/market-pulse` วันนี้ตลาดสหรัฐฯ เคลื่อนไหวอย่างไร กลุ่มไหนนำ กลุ่มไหนตาม
- `/sector-rotation` 11 กลุ่มอุตสาหกรรมอยู่ช่วงไหนเทียบ S&P 500
- `/event-study` หลังวันแบบนี้ ราคาเคยเคลื่อนไหวอย่างไร เทียบกับวันทั่วไป

**วางแผน**
- `/dca-plan` ลงทุนรายเดือนเท่าไร ถึงเป้าเมื่อไร ภายใต้สมมติฐานที่ระบุไว้ชัด

English:

**Understand a stock or ETF**
- `/stock-card` who the company is, with price and key figures, on one page
- `/earnings-check` the latest quarter against what analysts expected
- `/fair-value` what the cash flows suggest it is worth, in three cases
- `/stock-debate` the evidence for adding, holding and trimming, side by side
- `/etf-compare` how ETFs for one theme differ
- `/dividend-check` where a dividend comes from and whether it is covered

**Look after a portfolio**
- `/portfolio-checkup` where the portfolio is concentrated, read-only from the user's Webull account
- `/morning-brief` what matters this morning for holdings and watchlists

**Read the market**
- `/market-pulse` how the US market moved today and which groups led
- `/sector-rotation` where the eleven sectors sit against the S&P 500
- `/event-study` what a price did after a kind of day, against ordinary days

**Plan**
- `/dca-plan` how a monthly amount may grow, or what a goal needs, under stated assumptions

## Routing

| The user wants to | Workflow |
|---|---|
| get to know a company or ticker | `/stock-card` |
| know how the last quarter went | `/earnings-check` |
| know what a stock may be worth | `/fair-value` |
| think through buying more, holding or selling | `/stock-debate` |
| choose between ETFs | `/etf-compare` |
| judge a dividend | `/dividend-check` |
| check concentration in their holdings | `/portfolio-checkup` |
| catch up before the day starts | `/morning-brief` |
| see today's movers and sectors | `/market-pulse` |
| see which sectors lead or lag | `/sector-rotation` |
| test "what usually happens after X" | `/event-study` |
| plan a monthly amount or a goal | `/dca-plan` |
| connect Webull or open an account | `/connect-webull` |

If nothing fits, say so and help in chat. Do not force a workflow.

## Good to know, only when relevant

- Market data covers US shares and US ETFs. Thai (SET) shares are not served by
  the Webull market-data tools at the time of writing.
- Reports need code execution. Without it the answer comes in chat only.
- The desk never places an order.

Close with the one-line reminder from desk rules, section 8.
