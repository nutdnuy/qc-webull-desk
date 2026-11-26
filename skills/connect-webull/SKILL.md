---
name: connect-webull
description: Connect the user's Webull account to this desk, or help someone who has no Webull account yet. Use when the user runs "/connect-webull" or asks "เชื่อมต่อ Webull ยังไง", "ต่อ Webull กับ Claude", "ยังไม่มีบัญชี Webull", "เปิดบัญชี Webull ยังไง", "ขอลิงก์เปิดบัญชี", "Webull MCP ใช้ยังไง", "how do I connect Webull", "I don't have a Webull account", "how do I open a Webull account", and whenever another workflow finds that Webull tools are missing.
metadata:
  version: "0.1.0"
  author: QuantCorner
---

# Connect Webull

Read `references/desk-rules.md` first. Sections 2, 3 and 4 are the procedure;
this skill only adds the order and the check at the end.

## Steps

1. **Detect.** Look for Webull tools in this session. If they are present, skip
   to step 4 and say the connection already works.
2. **Ask once** whether the user has a Webull account (desk rules, section 2).
3. **Guide.**
   - Has an account: give the connection steps (section 3). Recommend the
     view-only mode. No referral link.
   - No account: give the partner block (section 4) in the user's language,
     link and disclosure together, once. Then say what happens next: open the
     account on Webull's page, finish identity checks there, then return and
     connect with the steps in section 3.
   - Wants a sample first: describe what a report contains and offer the
     example in the plugin's `examples/` folder. Mark anything invented as
     *Illustrative, not data*.
4. **Smoke test** after the user says they connected. Call `get_stock_snapshot`
   for `AAPL` in `US_STOCK`. Report one of:
   - works: show the price, its time in ICT and `trade_status`;
   - tool missing: the connector is not enabled in this conversation;
   - authorisation error: the sign-in did not finish or has expired;
   - empty or entitlement error: the account lacks that market data.
   Then check the account tools with `get_account_list`. If they fail but market
   data works, say the desk can do everything except `/portfolio-checkup` and
   the holdings part of `/morning-brief`.
5. **Next step.** Offer `/start`, or the workflow the user came from.

## Boundaries

- Never ask for, accept or type a password, PIN or one-time code.
- Never open an account, accept terms or submit a form for the user.
- Do not quote promotions, fees or approval times from memory. Point to Webull's page.
- Do not invent an MCP server address or a setup step. If the page has changed,
  say so and send the user to it.
- The desk stays read-only. If the user asks to place an order, say they do
  that in the Webull app.
