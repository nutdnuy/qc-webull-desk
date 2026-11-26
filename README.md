# QuantCorner Desk for Webull

**โต๊ะวิจัยการลงทุนส่วนตัวบน Claude ที่ใช้ข้อมูลจากบัญชี Webull ของคุณเอง**
**A personal research desk in Claude, built on your own Webull connection.**

12 เวิร์กโฟลว์สำหรับหุ้นและ ETF สหรัฐฯ ตั้งแต่ทำความรู้จักหุ้น เช็กงบ ประเมินมูลค่า เช็กพอร์ต ไปจนถึงอ่านภาวะตลาดและวางแผนลงทุนรายเดือน ตัวเลขทุกตัวบอกแหล่งที่มาและวันที่ และทุกเวิร์กโฟลว์จบด้วยรายงาน 1 หน้าที่เก็บไว้ได้ การตัดสินใจเป็นของคุณเสมอ

ปลั๊กอินนี้จัดทำโดย QuantCorner ไม่ใช่ผลิตภัณฑ์ของ Webull

[ภาษาไทย](#ภาษาไทย) | [English](#english)

---

## ภาษาไทย

### เริ่มใช้งาน

1. ติดตั้งปลั๊กอิน แล้วเปิด **Code execution** ในการตั้งค่า
   - Claude Code: พิมพ์คำสั่งนี้

     ```
     /plugin install qc-webull-desk --marketplace nutdnuy/qc-webull-desk
     ```
   - Claude แอปเดสก์ท็อปหรือเว็บ: ดาวน์โหลดไฟล์ [`dist/qc-webull-desk.plugin`](dist/qc-webull-desk.plugin) แล้วอัปโหลดในหน้าปลั๊กอิน
2. เชื่อมต่อ Webull กับ Claude ตามหน้า [Webull Agentic](https://www.webull.co.th/agentic) แนะนำให้เลือกโหมดดูข้อมูลเท่านั้น
3. พิมพ์ `/start` เพื่อดูเมนู หรือถามเป็นภาษาธรรมดาได้เลย

ลองพิมพ์: "ทำความรู้จักหุ้น NVDA" หรือ "เช็กพอร์ตให้หน่อย" หรือ "เมื่อคืนตลาดเป็นยังไง"

### ยังไม่มีบัญชี Webull

เดสก์นี้อ่านข้อมูลผ่านการเชื่อมต่อ Webull ของคุณเอง จึงต้องมีบัญชี Webull ก่อนจึงจะดึงข้อมูลจริงได้

เปิดบัญชีได้ที่ <https://www.webull.co.th/k/QuantCorner>

ลิงก์นี้เป็นลิงก์แนะนำของ QuantCorner หากเปิดบัญชีผ่านลิงก์นี้ QuantCorner อาจได้รับผลตอบแทนจากการแนะนำ โดยคุณไม่เสียค่าใช้จ่ายเพิ่ม

เดสก์นี้ใช้ได้กับบัญชี Webull ทุกบัญชี ไม่ว่าจะเปิดผ่านลิงก์ใด เงื่อนไขและโปรโมชันเป็นไปตามที่ Webull ประกาศบนหน้าเว็บของ Webull

### เวิร์กโฟลว์ทั้งหมด

#### เข้าใจหุ้นและ ETF

| คำสั่ง | ตอบคำถาม | สิ่งที่ได้ |
| --- | --- | --- |
| `/stock-card` | หุ้นตัวนี้คือใคร ตอนนี้อยู่ตรงไหน | การ์ดสรุป 1 หน้า ราคา ตัวเลขสำคัญ มุมมองนักวิเคราะห์ คู่แข่ง |
| `/earnings-check` | งบไตรมาสล่าสุดเทียบกับที่คาดเป็นอย่างไร | รายงานเทียบ EPS กับประมาณการ และแนวโน้ม 8 ไตรมาส |
| `/fair-value` | ตามกระแสเงินสด หุ้นนี้ควรมีมูลค่าเท่าไร | 3 กรณี ตารางความอ่อนไหว และการเติบโตที่ราคาปัจจุบันสะท้อนอยู่ |
| `/stock-debate` | หลักฐานฝั่งซื้อเพิ่ม ถือ และลด มีอะไรบ้าง | หน้าเทียบ 3 มุมด้วยมาตรฐานเดียวกัน ไม่ชี้คำตอบ |
| `/etf-compare` | ETF ธีมเดียวกันต่างกันตรงไหน | ตารางเทียบค่าธรรมเนียม ไส้ใน การทับซ้อน และผลตอบแทนช่วงเดียวกัน |
| `/dividend-check` | ปันผลนี้จ่ายไหวไหม | อัตราจ่ายเทียบกำไรและกระแสเงินสด 5 ปี |

#### ดูแลพอร์ต

| คำสั่ง | ตอบคำถาม | สิ่งที่ได้ |
| --- | --- | --- |
| `/portfolio-checkup` | พอร์ตกระจุกตัวตรงไหน | อ่านพอร์ตจาก Webull แบบดูอย่างเดียว น้ำหนักรายตัว รายกลุ่ม และจำนวนหุ้นเทียบเท่า |
| `/morning-brief` | เช้านี้มีอะไรเกี่ยวกับหุ้นที่ถือและที่ติดตาม | หน้าสรุปอ่านบนมือถือ เวลาไทยทุกรายการ |

#### อ่านภาวะตลาด

| คำสั่ง | ตอบคำถาม | สิ่งที่ได้ |
| --- | --- | --- |
| `/market-pulse` | วันนี้ตลาดสหรัฐฯ เป็นอย่างไร | ความกว้างของตลาด กลุ่มนำ กลุ่มตาม หุ้นเคลื่อนไหวมาก |
| `/sector-rotation` | 11 กลุ่มอุตสาหกรรมอยู่ช่วงไหนเทียบ S&P 500 | แผนที่ 4 ช่อง พร้อมผลตอบแทนเทียบตลาด 4 และ 12 สัปดาห์ |
| `/event-study` | หลังวันแบบนี้ ราคาเคยเคลื่อนไหวอย่างไร | ตารางเทียบกับวันทั่วไป พร้อมจำนวนเหตุการณ์และกรณีแย่ที่สุด |

#### วางแผน

| คำสั่ง | ตอบคำถาม | สิ่งที่ได้ |
| --- | --- | --- |
| `/dca-plan` | ลงทุนรายเดือนเท่าไร ถึงเป้าเมื่อไร | ตารางสถานการณ์ภายใต้สมมติฐานที่ระบุไว้ชัด |

`/connect-webull` ช่วยเชื่อมต่อบัญชีและทดสอบว่าข้อมูลมาถูกต้อง

### หลักการทำงาน

- **ข้อมูลจากบัญชีของคุณ** ดึงราคา งบการเงิน มุมมองนักวิเคราะห์ ข้อมูล ETF และพอร์ต ผ่าน Webull MCP ไม่ได้เดาจากความจำของ AI
- **บอกที่มาทุกตัวเลข** ทุกกราฟและตารางมีแหล่งข้อมูล ช่วงเวลา และหน่วย ถ้าหาไม่พบจะบอกตรง ๆ
- **คำนวณด้วยสคริปต์** งานที่ต้องคำนวณใช้เครื่องคำนวณที่มากับปลั๊กอิน ใส่ข้อมูลเดิมได้ผลเดิม
- **ดูอย่างเดียว** เดสก์นี้ไม่ส่ง แก้ไข หรือยกเลิกคำสั่งซื้อขาย
- **คุณตัดสินใจเอง** ทุกเวิร์กโฟลว์วางหลักฐานและข้อจำกัดให้เห็น ไม่บอกว่าควรซื้อหรือขาย

### ขอบเขตข้อมูล

- ครอบคลุมหุ้นและ ETF สหรัฐฯ ตามที่เครื่องมือของ Webull ให้บริการ ณ วันที่ 26 พฤศจิกายน 2026 หุ้นไทยยังไม่มีในเครื่องมือข้อมูลตลาดชุดนี้
- ข่าวใช้ Web search ถ้าปิดอยู่ ส่วนข่าวจะถูกข้าม ไม่เขียนจากความจำ
- ถ้าไม่มี Code execution จะได้คำตอบในแชต ไม่มีไฟล์รายงาน

### ข้อควรทราบ

เนื้อหาจากปลั๊กอินนี้เป็นข้อมูลและผลการวิเคราะห์เพื่อประกอบการตัดสินใจของคุณเอง ไม่ใช่คำแนะนำการลงทุนหรือการชักชวนให้ซื้อขายหลักทรัพย์ ผลลัพธ์จาก AI อาจผิดพลาดหรือตกหล่น ควรตรวจตัวเลขกับแหล่งข้อมูลต้นทางก่อนตัดสินใจ การลงทุนมีความเสี่ยง ผลการดำเนินงานในอดีตไม่ได้ยืนยันผลในอนาคต

มูลค่าที่ประเมิน คะแนน และสถิติย้อนหลังที่ได้จากเวิร์กโฟลว์เหล่านี้เป็นผลจากแบบจำลองและสมมติฐานที่ระบุไว้ ไม่ใช่บทวิเคราะห์หรือคำแนะนำของ Webull หรือ QuantCorner

---

## English

### Get started

1. Install the plugin and turn on **Code execution**.
   - Claude Code:

     ```
     /plugin install qc-webull-desk --marketplace nutdnuy/qc-webull-desk
     ```
   - Claude desktop or web: download [`dist/qc-webull-desk.plugin`](dist/qc-webull-desk.plugin) and upload it on the plugins page.
2. Connect Webull to Claude from the [Webull Agentic](https://www.webull.co.th/agentic) page. The view-only mode is enough.
3. Type `/start`, or just ask in plain language.

### No Webull account yet

The desk reads data through your own Webull connection, so live data needs a Webull account.

You can open one at <https://www.webull.co.th/k/QuantCorner>

This is QuantCorner's referral link. If you open an account through it, QuantCorner may receive a referral benefit, at no extra cost to you. The desk works with any Webull account, however it was opened.

ลิงก์นี้เป็นลิงก์แนะนำของ QuantCorner หากเปิดบัญชีผ่านลิงก์นี้ QuantCorner อาจได้รับผลตอบแทนจากการแนะนำ โดยคุณไม่เสียค่าใช้จ่ายเพิ่ม

### Workflows

| Command | Answers | You get |
| --- | --- | --- |
| `/stock-card` | Who is this company and where does it stand? | A one-page card: price, key figures, analyst view, peers |
| `/earnings-check` | How did the latest quarter go against expectations? | EPS against the estimate and an eight-quarter trend |
| `/fair-value` | What do the cash flows suggest it is worth? | Three cases, a sensitivity grid and the growth today's price implies |
| `/stock-debate` | What supports adding, holding or trimming? | Three cases held to one standard, with no verdict |
| `/etf-compare` | How do ETFs for one theme differ? | Cost, holdings, overlap and returns over shared periods |
| `/dividend-check` | Can the business afford this dividend? | Payout against earnings and cash flow over five years |
| `/portfolio-checkup` | Where is my portfolio concentrated? | Read-only from Webull: weights, sectors, effective holdings |
| `/morning-brief` | What matters this morning for my names? | A phone-friendly page, timed in Bangkok time |
| `/market-pulse` | What is the US market doing today? | Breadth, leading and lagging groups, movers |
| `/sector-rotation` | Where do the eleven sectors sit against the S&P 500? | A four-quadrant map with 4 and 12 week relative returns |
| `/event-study` | What did the price do after days like this? | A comparison with ordinary days, with sample size and worst case |
| `/dca-plan` | How might a monthly amount grow, or what does a goal need? | A scenario grid on stated assumptions |

`/connect-webull` helps with the connection and tests that data arrives.

### How it works

- Data comes from your own Webull connection (Webull MCP), not from the model's memory.
- Every chart and table states its source, period and unit.
- Calculations run in bundled scripts, so the same inputs give the same result.
- Read-only: the desk never places, changes or cancels an order.
- Coverage is US stocks and ETFs as served by Webull's tools on 26 November 2026.

### For maintainers

- `partner.json` holds the referral link and its disclosure. Change it there.
- `shared/` holds the rules, the report renderer and the price reader that every skill uses.
- `python3 tools/build.py` copies them into each skill, checks the plugin and writes `dist/qc-webull-desk.plugin`.
- `python3 -m unittest discover -s tests` runs the tests.

### Important

Content produced by this plugin is general information and analysis for your own consideration. It is not investment advice or a solicitation. AI output can contain errors or omissions, so check figures against original sources before acting. Investing carries risk. Past performance does not indicate future results.

Valuations, scores and historical statistics from these workflows are outputs of models and stated assumptions. They are not research or recommendations from Webull or QuantCorner.

Independent plugin by QuantCorner. Not a Webull product. MIT licence; see `LICENSE` and `NOTICE.md`.
