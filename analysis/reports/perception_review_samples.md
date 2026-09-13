# Perception review (Phase 4 checkpoint)

Images: 5 · Messages: 17 · Users with amendments: 13

## Image extractions

| image | event | amount | ccy | kind | partial | conf | outcome | iters | evidence text | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| image_01 | event_253 | 4365000 | IDR | net_pay | False | high | recorded | 2 | Net Pay : IDR 4,365,000 | Payslip Aug-2019 for M NURHUDA SY. Total Earnings IDR 4,780,800 less Total Deductions IDR 415,800 = Net Pay IDR 4,365,000, matching the transfer line "Transferred to: Bank Central Asia - 2582373290 : IDR 4,365,000". Document printed 2 Sep 2019; period is August 2019, so document_date set to the pay-period end matching the event. Regular monthly salary, no one-time items. |
| image_02 | event_1442 | 100000 | INR | balance_due | False | high | recorded | 2 | Balance Due: 1,00,000.00 | Rent receipt no. 9453 dated 11/08/23 (2023-08-11). Total amount to be received 2,00,000.00; Amount received 1,00,000.00; Balance Due 1,00,000.00. The event is the outstanding rent balance, so it carries the Balance Due figure. Right edge slightly cropped but all relevant figures legible; notes are generic PAN/revenue-stamp remarks, not instructions to the reader. |
| image_03 | event_1545 | 41272 | INR | total_paid | False | high | recorded | 2 | Cash Paid: 41272.00 | Riddhi Siddhi (Nuts and Spices) Bill of Supply No. 1125000158, dated 27/02/2026 16:10, 11 items/76 qty. Net Amount 41272.0 equals Cash Paid 41272.00; matches groceries event_1545 date and currency. |
| image_04 | event_1700 | 2854.0 | INR | item_subtotal | True | medium | recorded | 2 | Item Bill ₹2854.00 | Grocery delivery order screenshot (13 items, Jeevan Bhima Nagar, status "Delivered"), matching event_1700. The "TOTAL ORDER BILL DETAILS" section is cropped: only "Item Bill ₹2854.00" is visible; the next line (delivery fee, partially cut) and the grand total are not readable. Reported amount is therefore the item subtotal and a lower bound on what was actually paid. Individual line items sum consistently with ₹2854.00. No document date printed. "Download Invoice" is a UI link, not acted on. |
| image_05 | event_1786 | 704.05 | INR | amount_due | False | high | recorded | 2 | Amount due till 06-Feb-2026 = 704.05 | Airtel telecom bill. Account summary: previous balance 3,543.54 fully paid, this month's charges +704.05, giving amount due till 06-Feb-2026 of 704.05 (matches "This month's charges" Total ₹704.05 = rentals 580.65 + usage 16.00 + taxes 107.40). A late figure of 822.05 applies only after 06-Feb-2026; the event date is 06-Feb-2026, so 704.05 is the figure due. Embedded text is marketing only and was not acted upon. |

## Message interpretations

| message | class | intent | target | amount | ccy | new_date | eff_from | mult | ended | income_conf | lang | outcome | iters | summary |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| message_01 | amend | salary_increase | salary | 42750000 | IDR | None | 2025-08-15 | None | False | True | Indonesian | recorded | 1 | Employer Cobalt Systems raises the user's regular monthly salary to IDR 42,750,000 effective 2025-08-15. |
| message_02 | confirm | arrears_one_time | salary | None | IDR | None | None | None | False | True | id | recorded | 2 | Employer BrightPath Media confirms the regular salary for the next payroll; the next payslip will show the regular salary and a one-time adjustment separately. No amounts or dates are given, so only the regular salary (unchanged) stands and the one-time adjustment is not a regular amount. |
| message_03 | cancel | bonus_unapproved | income_stream | None | IDR | None | None | None | False | False | id | recorded | 1 | Employer states the quarterly bonus is still pending performance review; amount and payment date are not yet approved, so the bonus credit is unconfirmed and must not be counted. |
| message_04 | amend | salary_temporary_pay | salary | 1037.52 | EUR | None | None | None | False | True | en | recorded | 2 | Employer Northstar Labs states temporary reduced monthly pay of EUR 1037.52 continues for the next payroll cycle; no date given. |
| message_05 | delay | salary_date_moved | salary | None | INR | 2024-09-23 | 2024-09-23 | None | False | True | English | recorded | 2 | Employer BrightPath Media moved the confirmed salary payment date to 2024-09-23, superseding any earlier payroll date; no amount change stated. |
| message_06 | amend | salary_reduced | salary | 1422.85 | EUR | None | None | None | False | True | en | recorded | 2 | Employer states the user's next salary is reduced to EUR 1422.85 due to approved unpaid leave; no date given, stream continues. |
| message_07 | delay | gig_payout_pending | income_stream | None | INR | None | None | None | False | False | en | recorded | 1 | QuickCrew gig platform says the next payout is still pending, earnings figures may change, and the balance is not withdrawable until completed — the gig income is unconfirmed/not available; no amount or date given. |
| message_08 | amend | commission_unapproved | salary | 38760000 | IDR | None | None | None | False | False | id | recorded | 2 | Employer confirms regular base salary of IDR 38,760,000; commission on pending deals is not approved and will not be paid until earned, so no commission income should be counted. |
| message_09 | cancel | seasonal_contract_ended | income_stream | None | ZAR | None | 2026-03-25 | None | True | False | en | recorded | 1 | Employer Cobalt Systems states the seasonal contract has ended with no confirmed off-season income or renewal; the salary income stream ends as of 2026-03-25 and no future credit is confirmed. |
| message_10 | confirm | salary_resumes | salary | 2717 | EUR | 2025-08-15 | 2025-08-15 | None | False | True | en | recorded | 2 | Employer confirms regular salary of EUR 2717 resumes on 2025-08-15; a new recurring childcare payment/deduction starts the same month but no amount is given. |
| message_11 | confirm | first_salary_confirmed | salary | 1661 | EUR | 2026-01-15 | 2026-01-15 | None | False | True | English | recorded | 1 | Employer Riverline Retail confirms the user's first salary of EUR 1661 crediting on 2026-01-15. |
| message_12 | amend | rent_increase | rent | None | INR | None | None | 1.12 | False | None | en | recorded | 1 | Service provider (StayLedger) states the renewed lease raises monthly rent by 12%, applying from the next rent payment; no absolute amount or date given. |
| message_13 | confirm | self_transfer | none | None | None | None | None | None | False | False | en | recorded | 1 | Bank confirms the matching debit/credit pair is an internal transfer between the user's own accounts (ref BAN-0013), so the credit is not income. |
| message_14 | delay | refund_pending | event:event_1785 | None | INR | None | None | None | False | False | English | recorded | 2 | Merchant CartLane says the refund (event_1785, INR 8640) is initiated but not yet credited; the credit remains pending/unconfirmed with no new date given. |
| message_15 | noise | investment_value_moved | event:event_1960 | None | EUR | None | None | None | False | False | en | recorded | 2 | ClearFund reports the portfolio's displayed market value rose, but no units were sold and no cash proceeds exist. The valuation remains unrealised and non-cash; no spendable income is confirmed and no amount/date change applies to event_1960. |
| message_16 | delay | prize_pending | none | None | None | None | None | None | False | False | English | recorded | 1 | DrawPay says the prize payment is still in processing and not yet credited; the credit remains unconfirmed. No amount, date or instruction given. |
| message_17 | confirm | prize_settled | event:event_2165 | None | INR | None | 2025-12-28 | None | True | True | English | recorded | 2 | PrizeTrack confirms the one-time prize proceeds (event_2165, INR 33,550) settled; claim closed with no further scheduled payments, so no recurring income arises. |

## Amendments applied (by user)

- **user_02**: salary_amount(salary, 42750000, from 2025-08-15) ← message_01
- **user_03**: amount(event_253, 4365000) ← image_01
- **user_06**: salary_amount(salary, 1037.52) ← message_04
- **user_07**: salary_date(salary, from 2024-09-23) ← message_05
- **user_08**: salary_amount(salary, 1422.85) ← message_06
- **user_10**: income_unconfirmed(all_income) ← message_07
- **user_12**: stream_ended(all_income) ← message_09
- **user_14**: salary_amount(salary, 2717, from 2025-08-15) ← message_10; salary_date(salary, from 2025-08-15) ← message_10
- **user_15**: salary_amount(salary, 1661, from 2026-01-15) ← message_11; new_income(salary, 1661, from 2026-01-15) ← message_11
- **user_16**: amount(event_1442, 100000) ← image_02; expense_multiplier(category:rent, x1.12) ← message_12
- **user_17**: amount(event_1545, 41272) ← image_03
- **user_19**: amount(event_1700, 2854.0) ← image_04
- **user_20**: amount(event_1786, 704.05) ← image_05

## Embedded instructions detected (matched phrases)

- image_04: Download Invoice
- image_05: Now view, download and pay your bills anytime, anywhere!; Visit airtel.in/business/thanksforbusiness/

## Safer-reading resolutions and dropped amendments

- message_02: arrears_one_time without an amount — ignored
- message_07: platform payout pending / not withdrawable — gig income not projected (safer)
- image_04: partial document — 2854.0 used as a lower bound for event_1700

## Retries (items that did not pass on the first try)

- none — every response passed schema validation on the first try

## Skipped / stops

- none
