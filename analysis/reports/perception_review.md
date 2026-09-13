# Perception review (Phase 4 checkpoint)

Images: 11 · Messages: 198 · Users with amendments: 136

## Image extractions

| image | event | amount | ccy | kind | partial | conf | outcome | iters | evidence text | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| image_06 | event_3051 | 1995 | INR | total_paid | False | high | recorded | 2 | Total ... 1995.00 — "One Thousand And Nine Hundred And Ninety-Five Rupees And Zero Paisa Only" | Blink Commerce (Grofers) GST tax invoice, 5 line items plus delivery charges, CGST 47.49 + SGST 47.49, grand total row visible at 1995.00 and confirmed by amount in words. No invoice date printed in the visible portion; event date 2026-01-06 unverified by document. No instructions addressed to the reader. |
| image_07 | event_3231 | 8528.1 | INR | total_paid | False | high | recorded | 2 | Total : 8528.10 | Tax invoice from Nagarjuna 1984 KMR, Bangalore, stamped PAID. SubTotal 8122.00 + SGST 2.50% 203.05 + CGST 2.50% 203.05 = Total 8528.10. A rounded "Grand Total (RS) : 8528" also appears; per rules the precise figure 8528.10 is used. Bill date 29-10-2025 matches the event date; full receipt visible, not cropped. |
| image_08 | event_4535 | 15339 | INR | total_paid | False | high | recorded | 2 | Total Amount Received ₹ 15,339.00 | Maintenance receipt (Inv 6455) with line items 13,880.00 + 1,050.00 + 409.00 = 15,339.00, matching the Total Amount Received. Charge date 24-07-2026 matches event date; due date 30-08-2026. Paid online via paytm, convenience fee Rs 0.00. |
| image_09 | event_5170 | 723.0 | INR | total_paid | False | high | recorded | 2 | Total Amount Received ₹ 723.00 | Water bill receipt (Jan–March 2026), invoice 6320, charge date 07-06-2026 matching the event date; due date 02-07-2026. Charged Amount and Amount lines both 723.00, confirmed in words "Rupees Seven Hundred Twenty Three Only". Convenience fee Rs 0.00, paid online via paytm/Indian Bank. Document complete; no embedded instructions. |
| image_10 | event_6033 | 79679.26 | INR | balance_due | False | high | recorded | 2 | Balance Due ₹79,679.26 | Grocery tax invoice with 22 line items; Sub Total 72,045.00 plus CGST/SGST (1,513.13 + 1,513.13 + 2,304.00 + 2,304.00) gives Total ₹79,679.26, matching Balance Due and the words "Indian Rupee Seventy-Nine Thousand Six Hundred Seventy-Nine and Twenty-Six Paise Only". No invoice date visible in the captured portion. Only note is "Thanks for your business." — no instructions to the reader. |
| image_11 | event_6859 | 3650 | INR | balance_due | False | high | recorded | 2 | Balance: 3650.00 | Jeevan Hospital provisional bill dated 19-Jan-2023, matching event_6859 (hospital bill payable, INR, 2023-01-19). Total Bill Amount 3650.00, Amount Payable 3650.00, Amount Paid 0.00, Balance 3650.00 — the full amount is still outstanding, so the event should carry 3650.00 INR. The detailed breakup continues beyond the visible page, but the grand total block is fully visible, so the figure is not a lower bound. |
| image_12 | event_7307 | 33.5 | USD | total_paid | False | high | recorded | 2 | Total: $33.50 | CityCab Service taxi receipt, trip #CC-8923, 01/10/2025 21:45 (DD/MM/YYYY, consistent with event_date 2025-10-01). Subtotal $33.50 (ride $28.50 + airport surcharge $5.00), tax $0.00, Total $33.50. Cash paid $40.00 with $6.50 change, so net amount paid is $33.50. Full receipt visible; no embedded instructions. Document currency USD matches event currency; home currency INR conversion not performed. |
| image_13 | event_7941 | 2298 | INR | total_paid | False | high | recorded | 2 | Total paid ₹2,298 (Incl. taxes and delivery) | Order confirmation for two tote bags (₹699 + ₹1,599 = item total ₹2,298; delivery free). Grand total "Total paid ₹2,298" visible, matching the shopping expense event_7941. No date printed on the document. |
| image_14 | event_9421 | 4543 | INR | total_paid | False | high | recorded | 2 | TOTAL 4543 00 | Handwritten pharmacy bill. Line items (1500, 724, 796, 550, 303, 670) sum to 4543, matching the printed TOTAL line, so the grand total is present despite the cropped header/footer. No date printed on the visible portion; amounts in Rs. (INR), consistent with the linked event's currency. |
| image_15 | event_9806 | 9968 | INR | total_paid | False | high | recorded | 2 | Grand Total ... Total(Incl Taxes) 9,968.00 | IndiGo (InterGlobe Aviation) air ticket GST invoice, DEL→BLR, dated 07-Jun-2026, matching event_9806. Grand total incl. taxes INR 9,968.00 (air travel 9,580.00 + airport charges 388.00). |
| image_16 | event_10521 | 393.22 | INR | total_paid | False | high | recorded | 2 | Total 393.22 | EV charging invoice, Krishnagiri station, charge point 1110, CCS2. Energy 12.58 kWh at 26.49/kWh = 333.24 plus CGST 9% 29.99 and SGST 9% 29.99 = Total 393.22, paid by WALLET. Amount in words confirms "Three Hundred and Ninety Three Rupees And Twenty Two Paise Only". Charged on 03/09/2026 (DD/MM/YYYY) matches the event date 2026-09-03. No embedded instructions. |

## Message interpretations

| message | class | intent | target | amount | ccy | new_date | eff_from | mult | ended | income_conf | lang | outcome | iters | summary |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| message_18 | confirm | invoice_confirmed | income_stream | 30780000 | IDR | 2025-08-15 | 2025-08-15 | None | False | True | Indonesian | recorded | 1 | InvoiceFlow confirms a client-approved invoice of IDR 30,780,000 settling on 2025-08-15; other submitted invoices remain pending and are not confirmed income. |
| message_19 | delay | gig_payout_pending | income_stream | None | None | None | None | None | False | False | English | recorded | 1 | TaskLoop gig payout is pending and not withdrawable; displayed weekly earnings may change, so the credit is unconfirmed. No amount or date given. |
| message_20 | amend | arrears_one_time | salary | 1452 | EUR | None | None | None | False | True | English | recorded | 1 | Employer confirms regular salary of EUR 1452 for the next payroll, plus a separate one-time arrears adjustment of EUR 653.40 which is not regular income; only EUR 1452 should be treated as recurring salary. |
| message_21 | cancel | seasonal_contract_ended | income_stream | None | ZAR | None | 2025-10-27 | None | True | False | en | recorded | 1 | Riverline Retail states the user's seasonal contract has ended with no confirmed off-season income or renewal; the salary stream from this employer ends as of 2025-10-27. |
| message_22 | confirm | first_salary_confirmed | salary | 54120 | ZAR | 2025-02-15 | 2025-02-15 | None | False | True | en | recorded | 2 | Employer BrightPath Media confirms a first salary of ZAR 54,120 crediting on 2025-02-15. |
| message_23 | confirm | self_transfer | none | None | INR | None | None | None | False | False | en | recorded | 1 | Bank confirms the matching debit and credit (ref BAN-0023) are a transfer between the user's own accounts, so the credit is not income; both entries stay in history. No amounts or dates given. |
| message_24 | confirm | invoice_confirmed | income_stream | 196000 | INR | 2024-12-15 | 2024-12-15 | None | False | True | English | recorded | 1 | InvoiceLane confirms one approved invoice of INR 196,000 settling 2024-12-15; other invoices remain pending and unconfirmed. |
| message_25 | delay | refund_pending | event:event_3230 | None | INR | None | None | None | False | False | English | recorded | 2 | Merchant says the pending refund (event_3230, INR 12,960) has been initiated but not yet credited; the credit remains unconfirmed with no new date given. |
| message_26 | amend | salary_increase | salary | 2988 | USD | None | 2026-07-15 | None | False | True | English | recorded | 1 | Employer Northstar Labs payroll confirms the regular monthly salary rises to USD 2988 effective 2026-07-15. |
| message_27 | amend | arrears_one_time | salary | 21090000 | IDR | None | None | None | False | True | Indonesian | recorded | 1 | Employer confirms regular salary of IDR 21,090,000 for the next payroll, plus a separate one-time arrears adjustment of IDR 9,490,500 which is not part of regular income; only the regular amount is reported. |
| message_28 | confirm | prize_settled | event:event_3491 | None | EUR | None | 2025-08-06 | None | True | True | English | recorded | 2 | Rewards desk confirms the one-time prize proceeds (EUR 405.35, event_3491) have settled; claim closed with no further scheduled payments, so no recurring income going forward. |
| message_29 | confirm | first_salary_confirmed | salary | 1760 | EUR | 2024-06-15 | 2024-06-15 | None | False | True | en | recorded | 2 | New employer BrightPath Media confirms first salary of EUR 1760 crediting on 2024-06-15. |
| message_30 | amend | household_income_ended | salary | 148000 | INR | None | None | None | True | True | en | recorded | 1 | Employer states one household employment has ended; remaining confirmed monthly household salary is INR 148,000 going forward. |
| message_31 | confirm | first_salary_confirmed | salary | 32870000 | IDR | 2024-09-15 | 2024-09-15 | None | False | True | id | recorded | 1 | HarborWorks payroll confirms the first salary from the new employer of IDR 32,870,000 payable on 2024-09-15; normal bank processing time may apply. |
| message_32 | confirm | first_salary_confirmed | salary | 115000 | INR | 2025-02-15 | 2025-02-15 | None | False | True | English | recorded | 1 | Employer Riverline Retail confirms the user's first salary of INR 115,000 crediting on 2025-02-15. |
| message_33 | amend | salary_increase | salary | 17290000 | IDR | None | 2026-07-15 | None | False | True | id | recorded | 1 | Employer payroll (Northstar Labs) confirms monthly salary raised to IDR 17,290,000 effective 2026-07-15. |
| message_34 | delay | gig_payout_pending | income_stream | None | IDR | None | None | None | False | False | id | recorded | 1 | RideGrid platform says the next payout is still pending; weekly earnings may still change and the balance is not withdrawable until the payout completes. Gig income unconfirmed; no amounts or dates given. |
| message_35 | confirm | receipt_reference | event:event_4535 | None | INR | None | 2026-07-24 | None | False | None | English | recorded | 3 | Service provider confirms the property maintenance payment (event_4535) was received on 2026-07-24 and points to a receipt that carries the final INR amount and original due date. No amount is stated in the message, and the referenced receipt image is not available, so no figure can be extracted. |
| message_36 | amend | salary_temporary_pay | salary | 31464000 | IDR | None | None | None | False | True | Indonesian | recorded | 2 | Employer Greenfield Foods states the user's temporary monthly salary is IDR 31,464,000 and that this lower amount still applies to the next payroll; it is the amount currently scheduled for that pay period. |
| message_37 | amend | household_income_ended | salary | 126000 | INR | None | 2025-08-05 | None | True | True | en | recorded | 1 | Employer states one household employment record ended; remaining confirmed monthly household salary going forward is INR 126,000, effective from the message date 2025-08-05. |
| message_38 | confirm | first_salary_confirmed | salary | 69000 | INR | 2024-06-15 | 2024-06-15 | None | False | True | English | recorded | 1 | Employer HarborWorks confirms the user's first salary of INR 69,000 from the new employer, payable on 2024-06-15. |
| message_39 | delay | refund_pending | event:event_4994 | None | USD | None | None | None | False | False | English | recorded | 2 | Merchant says the pending refund (event_4994, USD 230.40) has been initiated but not yet credited; completion typically within ten business days, so the credit remains unconfirmed. |
| message_40 | amend | salary_increase | salary | 42460 | ZAR | None | 2026-07-15 | None | False | True | English | recorded | 1 | Employer Northstar Labs confirms regular monthly salary raised to ZAR 42,460 effective 2026-07-15. |
| message_41 | noise | self_transfer | none | None | None | None | None | None | False | False | en | recorded | 1 | Bank clarifies a matching debit/credit pair is a self-transfer between the user's own accounts; not income, no ledger amount change. |
| message_42 | amend | household_income_ended | salary | 25840000 | IDR | None | 2024-11-29 | None | True | True | Indonesian | recorded | 1 | Employer reports one household income stream has ended; remaining confirmed monthly salary is IDR 25,840,000, with the ended income excluded from future forecasts. |
| message_43 | delay | gig_payout_pending | income_stream | None | None | None | None | None | False | False | en | recorded | 1 | WorkDash gig platform states the next payout is pending, earnings may change, and the balance is not withdrawable until completed — the credit is unconfirmed; no amount or date given. |
| message_44 | amend | salary_reduced | salary | 530.4 | USD | None | None | None | False | True | English | recorded | 2 | Employer Northstar Labs states the user's next salary is reduced to USD 530.40 due to approved unpaid leave; a one-off reduction, not a permanent change. |
| message_45 | cancel | seasonal_contract_ended | income_stream | None | ZAR | None | 2024-02-28 | None | True | False | English | recorded | 1 | Employer Greenfield Foods states the user's seasonal contract has ended with no confirmed off-season income or renewal; the seasonal salary stream ends as of 2024-02-28. |
| message_46 | confirm | invoice_confirmed | income_stream | 2112 | USD | 2025-08-15 | 2025-08-15 | None | False | True | en | recorded | 1 | One invoice of USD 2112 approved and settling 2025-08-15; other submitted invoices remain pending and unconfirmed. |
| message_47 | delay | foreign_refund_pending | none | None | None | None | None | None | False | False | English | recorded | 1 | Merchant UrbanCart says a foreign-currency refund (order ref MER-0047) is still processing and the INR credit amount may vary with the settlement-date exchange rate; no amount or date confirmed, so the credit is unconfirmed. |
| message_48 | delay | bonus_unapproved | income_stream | None | ZAR | None | None | None | False | False | English | recorded | 1 | Employer states the quarterly bonus amount and payment date are not yet approved, pending final performance review; no regular pay change and no confirmed credit. |
| message_49 | confirm | invoice_confirmed | income_stream | 116000 | INR | 2026-04-15 | 2026-04-15 | None | False | True | en | recorded | 1 | A service provider confirms one approved invoice of INR 116,000 settling on 2026-04-15; other submitted invoices remain unapproved and should not be counted. |
| message_50 | delay | salary_date_moved | salary | None | USD | 2025-02-23 | 2025-02-23 | None | False | True | English | recorded | 2 | Employer Riverline Retail moved the confirmed salary payment date to 2025-02-23, superseding the date in an earlier update (no earlier message is on file). No amount is stated, so the existing salary amount is unchanged; the credit remains confirmed. |
| message_51 | amend | rent_increase | rent | None | EUR | None | None | 1.12 | False | None | en | recorded | 1 | RentNest reports the renewed lease raises monthly rent by 12% (multiplier 1.12), applying from the next rent payment; no explicit new amount or date given. |
| message_52 | noise | investment_value_moved | event:event_6532 | None | INR | None | None | None | False | False | English | recorded | 2 | PocketVest notice: portfolio market value rose but remains unrealized — no units sold, no cash proceeds. No spendable income; event_6532 stays non-cash/unrealized with no stated new figure. |
| message_53 | confirm | foreign_salary_confirmed | salary | 696 | USD | 2025-05-15 | 2025-05-15 | None | False | True | Indonesian | recorded | 1 | Employer Greenfield Foods confirms a salary of USD 696 for 2025-05-15; the amount received in the home currency (IDR) depends on the settlement-date exchange rate. |
| message_54 | confirm | first_salary_confirmed | salary | 18700 | ZAR | 2026-07-15 | 2026-07-15 | None | False | True | en | recorded | 1 | Employer Cedar Health payroll confirms the user's first salary of ZAR 18,700 crediting on 2026-07-15. |
| message_55 | amend | rent_increase | rent | None | INR | None | None | 1.12 | False | None | en | recorded | 1 | RentTrack says the renewed lease raises monthly rent by 12% (multiplier 1.12), applying from the next rent payment. No explicit amount or date given. |
| message_56 | confirm | invoice_confirmed | income_stream | 26180 | ZAR | 2025-08-15 | 2025-08-15 | None | False | True | en | recorded | 1 | One invoice of ZAR 26,180 is approved and settling 2025-08-15; other invoices remain pending and unconfirmed. |
| message_57 | cancel | employment_ended | salary | None | ZAR | None | 2026-04-04 | None | True | False | English | recorded | 1 | Employer Northstar Labs states the user's employment has ended and no regular salary payments are scheduled after the final settlement; salary income stream ends as of 2026-04-04. Final settlement details to follow separately (no amount given). |
| message_58 | amend | commission_unapproved | salary | 3072 | USD | None | None | None | False | False | en | recorded | 1 | Employer confirms base salary of USD 3072; commission on open deals is unapproved/pending and must not be counted as income. |
| message_59 | delay | refund_pending | event:event_7186 | None | INR | None | None | None | False | False | English | recorded | 2 | Merchant says the pending INR 8,880 refund (event_7186) has been initiated but not yet credited; completion may take up to ten business days, so the credit remains unconfirmed with no firm date. |
| message_60 | amend | commission_unapproved | salary | 158000 | INR | None | None | None | False | False | English | recorded | 1 | Employer confirms base salary of INR 158,000 but states commission on open deals is unapproved and excluded from payout; only the base salary should count as regular income. |
| message_61 | amend | rent_increase | rent | None | USD | None | None | 1.12 | False | None | en | recorded | 1 | Service provider (StayLedger) states the renewed lease raises monthly rent by 12%, effective from the next rent payment; no explicit amount or date given. |
| message_62 | confirm | arrears_one_time | salary | 1752 | USD | None | None | None | False | True | en | recorded | 1 | Employer confirms regular salary of USD 1752 for the next payroll, plus a separate one-time arrears adjustment of USD 788.40 which is not regular income; report USD 1752 only. |
| message_63 | confirm | salary_resumes | salary | 62000 | INR | 2025-05-15 | 2025-05-15 | None | False | True | en | recorded | 2 | Employer confirms regular salary of INR 62,000 resumes on 2025-05-15. A new recurring childcare payment (an expense, no amount given) begins the same month; no figures to record for it. |
| message_64 | noise | other | none | None | None | None | None | None | False | None |  | unresolvable | 3 |  [unresolvable: The message only points to a receipt for the final amount ("The receipt has the final amount. Order ref MER-0064."), but no receipt image is available (inspect_image on MER-0064 returns an error) and the linked ledger row event_7941 has a blank amount. No amount can be read from the evidence, so the expense figure cannot be determined.] |
| message_65 | amend | salary_temporary_pay | salary | 8618400 | IDR | None | None | None | False | True | id | recorded | 2 | Payroll states the temporary lower monthly salary of IDR 8,618,400 continues and is what is scheduled for the next payroll period. |
| message_66 | confirm | salary_resumes | salary | 251000 | INR | 2026-01-15 | 2026-01-15 | None | False | True | English | recorded | 2 | Employer confirms regular salary of INR 251,000 resumes on 2026-01-15. A mention of a new recurring childcare payment and future deduction changes carries no amounts, so nothing further is recorded. |
| message_67 | noise | scam_or_instruction | none | None | None | None | None | None | False | False | en | recorded | 1 | Advance-fee prize scam solicitation demanding release/processing charges; no verifiable income or ledger fact. No credit confirmed. |
| message_68 | confirm | invoice_confirmed | income_stream | 13420 | ZAR | 2026-07-15 | 2026-07-15 | None | False | True | en | recorded | 1 | One invoice of ZAR 13,420 approved, settling 2026-07-15; other invoices remain unapproved and should not be counted. |
| message_69 | confirm | failed_debit_retry | event:event_8575 | 166 | EUR | None | None | None | False | None | en | recorded | 2 | Bank confirms the EUR 166 utility bill debit failed and remains outstanding; another debit attempt will be made, so the obligation still stands. |
| message_70 | amend | commission_unapproved | salary | 49280 | ZAR | None | None | None | False | False | English | recorded | 1 | Employer confirms regular base salary of ZAR 49,280; commission on open deals remains unapproved and must not be counted as income. |
| message_71 | delay | prize_pending | none | None | None | None | None | None | False | False | English | recorded | 1 | WinPoint says a prize payment is still processing and has not been credited; the credit is unconfirmed. No amount, date, or regular income change stated. |
| message_72 | confirm | invoice_confirmed | income_stream | 924 | EUR | 2024-12-15 | 2024-12-15 | None | False | True | English | recorded | 1 | ProjectPay confirms one approved invoice of EUR 924 settling 2024-12-15; other submitted invoices remain pending and should not be counted. |
| message_73 | delay | salary_date_moved | salary | None | INR | 2025-05-23 | 2025-05-23 | None | False | True | English | recorded | 2 | Employer Cobalt Systems confirms the salary payment date has moved to 2025-05-23, superseding the date in an earlier update. No amount is stated; no change to the salary amount or stream. The advisory sentence about paying bills around payday is an instruction to the user and was not acted upon. |
| message_74 | confirm | foreign_salary_confirmed | salary | 1804 | EUR | 2025-08-15 | 2025-08-15 | None | False | True | en | recorded | 2 | Employer confirms a foreign-currency salary of EUR 1804 payable 2025-08-15; the ZAR amount received depends on the settlement-date conversion rate. |
| message_75 | confirm | prize_settled | event:event_9420 | None | INR | None | None | None | True | True | en | recorded | 2 | ClaimDesk confirms the one-time prize proceeds (event_9420, INR 139,700) have settled into the account; no recurring payments follow, so this is not regular income. |
| message_76 | confirm | invoice_confirmed | income_stream | 1419 | EUR | 2026-04-15 | 2026-04-15 | None | False | True | English | recorded | 1 | WorkPort reports one client-approved invoice of EUR 1419 settling 2026-04-15; other invoices remain pending and should not be counted. |
| message_77 | amend | salary_temporary_pay | salary | 164880 | INR | None | None | None | False | True | English | recorded | 1 | Employer Cobalt Systems states the user's temporary monthly pay is INR 164,880 and that this reduced amount continues for the next payroll cycle; no dates given. |
| message_78 | amend | commission_unapproved | salary | 35860 | ZAR | None | None | None | False | False | en | recorded | 1 | Employer confirms regular base salary of ZAR 35,860; commission on open deals remains unapproved and must not be counted as income until marked earned. |
| message_79 | noise | investment_value_moved | event:event_9805 | None | INR | None | None | None | False | False | en | recorded | 2 | Broker notes the portfolio's displayed market value rose and will keep fluctuating; unrealized, non-cash valuation movement with no amount, date or realizable credit stated. No change to spendable income. |
| message_80 | confirm | first_salary_confirmed | salary | 1815 | EUR | 2024-12-15 | 2024-12-15 | None | False | True | English | recorded | 1 | Employer HarborWorks confirms the user's first salary of EUR 1815 on 2024-12-15; no instructions or one-time adjustments. |
| message_81 | confirm | first_salary_confirmed | salary | 2123 | EUR | 2025-05-15 | 2025-05-15 | None | False | True | en | recorded | 2 | Employer Greenfield Foods confirms the user's first salary of EUR 2123, approved and scheduled for 2025-05-15, pending bank processing of the payroll file. |
| message_82 | amend | commission_unapproved | salary | 33440 | ZAR | None | None | None | False | False | English | recorded | 2 | Employer confirms regular base salary of ZAR 33,440; commission on open deals remains unapproved and must not be counted as income. |
| message_83 | confirm | invoice_confirmed | income_stream | 16720 | ZAR | 2025-08-15 | 2025-08-15 | None | False | True | English | recorded | 1 | WorkPort confirms one client-approved invoice of ZAR 16,720 settling on 2025-08-15; other submitted invoices remain unapproved and should not be counted. |
| message_84 | cancel | employment_ended | salary | None | IDR | None | 2026-04-01 | None | True | False | id | recorded | 1 | HarborWorks states the user's employment has ended; no regular salary payments are scheduled after the final settlement (details to follow separately). Salary income stream ends as of 2026-04-01. |
| message_85 | confirm | first_salary_confirmed | salary | 627 | EUR | 2024-06-15 | 2024-06-15 | None | False | True | en | recorded | 2 | Employer BrightPath Media confirms the user's first salary of EUR 627 crediting on 2024-06-15. |
| message_86 | confirm | foreign_salary_confirmed | income_stream | 1296 | USD | 2026-09-15 | 2026-09-15 | None | False | True | en | recorded | 2 | Account update confirms a foreign-currency salary credit of USD 1296 on 2026-09-15, converted at the settlement-day exchange rate (home currency INR). The same message references an EV charging wallet charge at Charge Point 1110 on 2026-09-03 whose final INR amount is only stated to be on a receipt; no receipt image was supplied, so no amount is reported for event_10521. No instructions addressed to the reader. |
| message_87 | amend | salary_reduced | salary | 148200 | INR | None | None | None | False | True | English | recorded | 2 | Employer states the user's next salary is reduced to INR 148,200 due to approved unpaid leave; a one-off reduction, no date given. |
| message_88 | confirm | prize_settled | event:event_10699 | None | INR | None | 2024-08-30 | None | True | True | en | recorded | 2 | One-time prize proceeds (event_10699, INR 32,450) have settled; the claim is closed with no further scheduled payments, so this is not a recurring income stream. |
| message_89 | amend | salary_increase | salary | 1188 | EUR | None | 2026-07-15 | None | False | True | English | recorded | 1 | Employer Northstar Labs confirms regular monthly salary raised to EUR 1188 effective 2026-07-15. |
| message_90 | amend | arrears_one_time | salary | 759 | EUR | None | None | None | False | True | English | recorded | 1 | Employer confirms regular salary of EUR 759 for the next payroll, plus a separate one-time arrears adjustment of EUR 341.55 which is not regular income; report EUR 759 only. |
| message_91 | confirm | salary_resumes | salary | 176000 | INR | 2025-05-15 | 2025-05-15 | None | False | True | English | recorded | 2 | Employer Cobalt Systems confirms the user's regular salary of INR 176,000 resumes on 2025-05-15. A new recurring childcare deduction/payment starts the same month but no amount is given, so nothing is recorded for it. |
| message_92 | confirm | investment_sale_settled | event:event_11129 | None | IDR | None | None | None | False | True | id | recorded | 2 | Arbor Invest confirms the investment sale proceeds have settled into the cash account with no pending proceeds; confirms the one-time credit on event_11129 (IDR 13,062,500). No recurring income implied. |
| message_93 | confirm | invoice_confirmed | income_stream | 15390000 | IDR | 2025-08-15 | 2025-08-15 | None | False | True | id | recorded | 1 | ProjectPay: client approved one invoice of IDR 15,390,000 settling 2025-08-15; other submitted invoices remain pending approval and are not confirmed income. |
| message_94 | delay | gig_payout_pending | income_stream | None | None | None | None | None | False | False | id | recorded | 1 | TaskSprint says the next gig payout is still pending; weekly earnings may change and the balance is not withdrawable until the payout completes. No amount or date given; income unconfirmed. |
| message_95 | confirm | foreign_salary_confirmed | salary | 748 | EUR | 2025-11-15 | 2025-11-15 | None | False | True | en | recorded | 1 | Employer confirms a foreign-currency salary of EUR 748 payable 2025-11-15; the ZAR amount received depends on the settlement-date exchange rate. |
| message_96 | confirm | invoice_confirmed | income_stream | 152000 | INR | 2026-07-15 | 2026-07-15 | None | False | True | en | recorded | 1 | ClientDesk confirms one approved invoice of INR 152,000 settling 2026-07-15; other invoices remain unapproved and should not be counted. |
| message_97 | confirm | salary_resumes | salary | 50160 | ZAR | 2024-09-15 | 2024-09-15 | None | False | True | en | recorded | 2 | Employer confirms regular salary of ZAR 50,160 resumes on 2024-09-15; a new recurring childcare payment also begins that month (no amount given). |
| message_98 | delay | bonus_unapproved | income_stream | None | ZAR | None | None | None | False | False | English | recorded | 1 | Employer states the quarterly bonus amount and payment date are not yet approved, pending final performance review; the bonus is unconfirmed income and no regular amount or date changes. |
| message_99 | confirm | prize_settled | event:event_11925 | None | USD | None | 2026-03-28 | None | True | True | English | recorded | 2 | Prize proceeds (USD 561, event_11925) have settled into the account; the claim is closed with no further scheduled payments, so this one-time windfall is confirmed and not recurring. |
| message_100 | amend | salary_temporary_pay | salary | 2177.28 | USD | None | None | None | False | True | English | recorded | 2 | Employer BrightPath Media states a temporary reduced monthly pay of USD 2177.28 which continues for the next payroll cycle; no date given. |
| message_101 | delay | salary_date_moved | salary | None | USD | 2025-05-23 | 2025-05-23 | None | False | True | en | recorded | 2 | Employer Cobalt Systems confirms the salary payment date has moved to 2025-05-23, superseding the earlier payroll date; no amount change stated. |
| message_102 | amend | salary_reduced | salary | 1193.4 | USD | None | None | None | False | True | en | recorded | 2 | Employer states the user's next salary is reduced to USD 1193.40 due to approved unpaid leave; a one-off reduction, no date given. |
| message_103 | cancel | seasonal_contract_ended | salary | None | IDR | None | 2024-03-06 | None | True | False | id | recorded | 1 | HarborWorks says the user's seasonal contract has ended; no off-season income or contract extension is confirmed, so the salary stream ends as of 2024-03-06 with no future amount. |
| message_104 | amend | salary_increase | salary | 828 | USD | None | 2026-07-15 | None | False | True | en | recorded | 1 | Employer Riverline Retail confirms the user's regular monthly salary rises to USD 828 effective 2026-07-15. |
| message_105 | amend | rent_increase | rent | None | INR | None | None | 1.12 | False | None | en | recorded | 1 | HomePortal reports a renewed lease raising monthly rent by 12% (multiplier 1.12), effective from the next rent payment; no explicit amount or date given. |
| message_106 | confirm | duplicate_charge_dispute_open | event:event_12709 | None | EUR | None | None | None | False | False | en | recorded | 2 | Bank states the duplicate card charge dispute (ref BAN-0106) on event_12709 remains open and no reversal/credit has been posted; the 134.75 EUR debit stands for now. |
| message_107 | confirm | first_salary_confirmed | salary | 31900 | ZAR | 2025-02-15 | 2025-02-15 | None | False | True | English | recorded | 1 | HarborWorks payroll confirms the user's first salary of ZAR 31,900 crediting on 2025-02-15. |
| message_108 | confirm | investment_sale_settled | event:event_13032 | None | INR | None | None | None | False | True | English | recorded | 2 | ClearFund confirms the investment sale proceeds (event_13032, INR 53,350) have settled in the cash account with nothing pending; one-time credit, no regular amount implied. |
| message_109 | confirm | invoice_confirmed | income_stream | 2040 | USD | 2024-12-15 | 2024-12-15 | None | False | True | en | recorded | 1 | InvoiceFlow confirms one client-approved invoice of USD 2040 settling 2024-12-15; other submitted invoices remain unapproved and unconfirmed. |
| message_110 | confirm | prize_settled | event:event_13207 | None | ZAR | None | 2025-05-04 | None | True | True | en | recorded | 2 | One-time prize proceeds (ZAR 8228, event_13207) confirmed settled; claim closed with no further payments, so no recurring income going forward. |
| message_111 | confirm | first_salary_confirmed | salary | 864 | USD | 2026-07-15 | 2026-07-15 | None | False | True | English | recorded | 1 | Employer Cobalt Systems confirms the user's first salary of USD 864 crediting on 2026-07-15. |
| message_112 | confirm | arrears_one_time | salary | 258000 | INR | None | None | None | False | True | English | recorded | 1 | Employer confirms regular salary of INR 258,000 for the next payroll, plus a separate one-time arrears adjustment of INR 116,100 which is not regular income; only the regular 258,000 is reported. |
| message_113 | confirm | salary_resumes | salary | 1529 | EUR | 2026-04-15 | 2026-04-15 | None | False | True | en | recorded | 2 | Employer confirms regular salary of EUR 1529 resumes on 2026-04-15. A new recurring childcare payment/deduction is mentioned but no amount is given, so nothing is recorded for it. |
| message_114 | confirm | investment_sale_settled | event:event_13663 | 19602 | ZAR | None | 2024-05-31 | None | False | True | en | recorded | 2 | StackWealth confirms the investment sale proceeds (ZAR 19,602, event_13663) have settled in the cash account with nothing further pending; one-time credit, not regular income. |
| message_115 | amend | salary_reduced | salary | 893.75 | EUR | None | None | None | False | True | en | recorded | 1 | Employer Riverline Retail states the user's next salary is reduced to EUR 893.75 due to approved unpaid leave; a one-off reduction to the next payment, not a permanent change. |
| message_116 | confirm | first_salary_confirmed | salary | 46170000 | IDR | 2024-09-15 | 2024-09-15 | None | False | True | Indonesian | recorded | 1 | Payroll team of new employer Northstar Labs confirms first salary of IDR 46,170,000 on 2024-09-15; usual bank processing time may apply. |
| message_117 | confirm | reimbursement_not_salary | event:event_14026 | None | ZAR | None | 2025-02-01 | None | True | True | English | recorded | 2 | Employer confirms the ZAR 818.40 credit on 2025-02-01 is a one-time work-expense reimbursement, not regular salary; the claim is closed with no further reimbursements scheduled. No recurring income implied. |
| message_118 | delay | foreign_charge_pending | none | None | None | None | None | None | False | None | en | recorded | 1 | Merchant ShopNest says order MER-0118 was charged in a foreign currency; the final home-currency (USD) amount is not yet fixed and will be set by the bank's rate at settlement. No amount or date given. |
| message_119 | amend | household_income_ended | salary | 1628 | EUR | None | None | None | True | True | English | recorded | 1 | Employer (Cedar Health payroll) states one household employment record has ended; the remaining confirmed monthly household salary going forward is EUR 1628. No dates given. A generic instruction about removing ended income was present and is quoted, not acted on. |
| message_120 | confirm | salary_resumes | salary | 84000 | INR | 2025-05-15 | 2025-05-15 | None | False | True | en | recorded | 2 | Employer confirms regular salary of INR 84,000 resumes on 2025-05-15; a mention of a new recurring childcare payment carries no amount, so nothing is recorded for it. |
| message_121 | confirm | duplicate_charge_dispute_open | event:event_14399 | None | ZAR | None | None | None | False | False | English | recorded | 2 | Bank confirms the duplicate card charge dispute (ref BAN-0121) is still open; no reversal/credit has been posted, so the ZAR 1617 debit stands for now. |
| message_122 | amend | salary_temporary_pay | salary | 23940000 | IDR | None | None | None | False | True | id | recorded | 1 | HarborWorks payroll confirms the temporary lower monthly salary of IDR 23,940,000 continues and is the amount scheduled for the next payroll period. |
| message_123 | delay | gig_payout_pending | income_stream | None | None | None | None | None | False | False | en | recorded | 1 | ShiftPay gig platform payout is pending and not withdrawable; displayed weekly earnings may change, so the credit is unconfirmed. No amount or date given. |
| message_124 | confirm | first_salary_confirmed | salary | 1672 | EUR | 2024-06-15 | 2024-06-15 | None | False | True | English | recorded | 2 | Employer confirms the user's first salary of EUR 1672 from Riverline Retail, payable 2024-06-15. |
| message_125 | confirm | first_salary_confirmed | salary | 26790000 | IDR | 2025-11-15 | 2025-11-15 | None | False | True | id | recorded | 1 | HarborWorks confirms the user's first salary of IDR 26,790,000 scheduled for 2025-11-15; payroll approved and submitted for processing. |
| message_126 | amend | salary_increase | salary | 29070000 | IDR | None | 2026-07-15 | None | False | True | id | recorded | 1 | Payroll team of Cedar Health confirms the user's monthly salary rises to IDR 29,070,000 effective 2026-07-15, visible on the next payslip. |
| message_127 | amend | arrears_one_time | salary | 30400000 | IDR | None | None | None | False | True | Indonesian | recorded | 1 | Employer confirms regular salary of IDR 30,400,000 for the next payroll, plus a one-time arrears adjustment of IDR 13,680,000 shown separately; only the regular amount is reported. |
| message_128 | amend | commission_unapproved | salary | 44270000 | IDR | None | 2025-02-01 | None | False | False | id | recorded | 1 | Employer confirms regular base salary of IDR 44,270,000; commission from pending deals is not approved and must not be counted as income until earned. |
| message_129 | cancel | employment_ended | salary | None | INR | None | 2026-04-03 | None | True | False | English | recorded | 1 | Employer Cedar Health states the user's employment has ended and no regular salary payments are scheduled after the final settlement; salary income stream ends as of 2026-04-03. Final settlement details to follow separately (no amount given). |
| message_130 | confirm | invoice_confirmed | income_stream | 2340 | USD | 2024-12-15 | 2024-12-15 | None | False | True | en | recorded | 1 | InvoiceFlow confirms one approved invoice of USD 2340 settling 2024-12-15; other submitted invoices remain unapproved and should not be counted. |
| message_131 | delay | salary_date_moved | salary | None | ZAR | 2025-05-23 | 2025-05-23 | None | False | True | en | recorded | 2 | Employer BrightPath Media confirms the salary payment date has moved to 2025-05-23, superseding any earlier payroll date. No amount is stated, so the regular salary amount is unchanged and the income remains confirmed. |
| message_132 | amend | salary_reduced | salary | 137150 | INR | None | None | None | False | True | English | recorded | 1 | Employer Greenfield Foods states the user's next salary only is reduced to INR 137,150 due to approved unpaid leave; a one-off reduction, not a new regular amount. |
| message_133 | delay | foreign_refund_pending | none | None | None | None | None | None | False | False | English | recorded | 1 | CartLane says a foreign-currency refund (order MER-0133) is still processing; the home-currency credit amount is unknown until settlement and may vary with the exchange rate, so the credit is not confirmed. |
| message_134 | delay | prize_pending | none | None | None | None | None | None | False | False | id | recorded | 1 | WinPoint says the user's verified prize claim is still being processed and the payment has not reached the account; no amount or date given, so the prize credit remains unconfirmed. |
| message_135 | amend | self_transfer | none | None | None | None | None | None | False | False | en | recorded | 1 | Bank clarifies that a matching debit/credit pair (ref BAN-0135) is a transfer between two accounts held by the same user, so the credit is not new income; both entries stay visible in history. |
| message_136 | confirm | two_card_minimums | none | None | ZAR | None | None | None | False | None | en | recorded | 1 | Bank confirms two distinct card minimum payments are due this month on separate accounts; paying one does not clear the other. No amounts or dates stated. |
| message_137 | confirm | foreign_salary_confirmed | salary | 1284 | USD | 2025-11-15 | 2025-11-15 | None | False | True | English | recorded | 1 | Employer confirms a foreign-currency salary of USD 1284 payable 2025-11-15; the INR amount received depends on the settlement-date conversion rate. |
| message_138 | amend | salary_temporary_pay | salary | 1924.56 | EUR | None | None | None | False | True | English | recorded | 2 | Employer Riverline Retail states a temporary reduced monthly pay of EUR 1924.56 continues for the next payroll cycle; no date given. |
| message_139 | amend | commission_unapproved | salary | 847 | EUR | None | None | None | False | False | English | recorded | 1 | Employer confirms base salary of EUR 847; commission on open deals is unapproved/pending and must not be counted as income. |
| message_140 | amend | salary_reduced | salary | 1731.6 | USD | None | None | None | False | True | en | recorded | 2 | Employer states the user's next salary is reduced to USD 1731.60 due to approved unpaid leave; a one-off reduction, no date given. |
| message_141 | confirm | invoice_confirmed | income_stream | 2376 | EUR | 2024-12-15 | 2024-12-15 | None | False | True | en | recorded | 1 | FreelanceHub reports one client-approved invoice of EUR 2376 settling 2024-12-15; other invoices remain pending and unconfirmed. |
| message_142 | noise | scam_or_instruction | none | None | None | None | None | None | False | False | Indonesian | recorded | 1 | Advance-fee prize scam: claims a cash prize and demands payment of a release/processing fee. No verifiable income; instructions not acted on. |
| message_143 | confirm | first_salary_confirmed | salary | 59000 | INR | 2026-07-15 | 2026-07-15 | None | False | True | en | recorded | 2 | Employer Northstar Labs confirms the user's first salary of INR 59,000 crediting on 2026-07-15. |
| message_144 | delay | bonus_unapproved | income_stream | None | ZAR | None | None | None | False | False | en | recorded | 1 | Employer states the quarterly bonus amount and payment date are not yet approved, pending performance review; bonus is unconfirmed income and no regular amount changes. |
| message_145 | delay | foreign_charge_pending | none | None | None | None | None | None | False | None | id | recorded | 1 | CartLane says the charge (order ref MER-0145) is in a foreign currency; the final home-currency amount will only be confirmed by the bank when the transaction settles at the then-current exchange rate. No amount or date given — foreign charge pending. |
| message_146 | delay | foreign_refund_pending | none | None | None | None | None | None | False | False | en | recorded | 1 | Merchant BrightBasket says a foreign-currency refund (order MER-0146) is still processing; the home-currency credit amount is not yet determined and depends on the settlement-date rate, so the credit is unconfirmed. |
| message_147 | amend | rent_increase | rent | None | EUR | None | None | 1.12 | False | None | English | recorded | 1 | Landlord/service provider HomePortal states rent rises 12% (multiplier 1.12) starting with the next rent payment; no explicit amount or date given. |
| message_148 | amend | salary_reduced | salary | 31889 | ZAR | None | None | None | False | True | English | recorded | 1 | Employer HarborWorks states the user's next salary is reduced to ZAR 31,889 due to approved unpaid leave; a one-off reduction, not a permanent pay change. |
| message_149 | confirm | first_salary_confirmed | salary | 145000 | INR | 2024-09-15 | 2024-09-15 | None | False | True | English | recorded | 1 | Employer BrightPath Media confirms the user's first salary of INR 145,000 from the new employer, payable on 2024-09-15. |
| message_150 | confirm | reimbursement_not_salary | event:event_17401 | None | EUR | None | None | None | True | True | en | recorded | 2 | Employer confirms the EUR 83.16 credit on 2025-02-03 is a one-time work-expense reimbursement, not salary; the claim is closed with no further reimbursements scheduled, so it must not be treated as recurring income. |
| message_151 | amend | salary_increase | salary | 627 | EUR | None | 2026-07-15 | None | False | True | English | recorded | 1 | Employer HarborWorks confirms regular monthly salary rises to EUR 627 effective 2026-07-15. |
| message_152 | delay | refund_pending | event:event_17662 | None | EUR | None | None | None | False | False | en | recorded | 2 | Merchant says the EUR 65.12 refund (event_17662) has been initiated but not yet credited; completion may take up to ten business days, so the credit remains pending/unconfirmed with no firm date. |
| message_153 | amend | salary_temporary_pay | salary | 1750.32 | EUR | None | None | None | False | True | en | recorded | 2 | Employer Cedar Health states the user's temporary reduced monthly pay of EUR 1750.32 continues for the next payroll cycle; no date given. |
| message_154 | delay | salary_date_moved | salary | None | INR | 2025-08-23 | 2025-08-23 | None | False | True | en | recorded | 2 | Employer Northstar Labs confirms the salary payment date has moved to 2025-08-23, superseding any earlier payroll date. No amount change is stated; the credit remains confirmed. |
| message_155 | amend | salary_reduced | salary | 1222.65 | EUR | None | None | None | False | True | en | recorded | 1 | HarborWorks payroll states the user's next salary is reduced to EUR 1222.65 due to approved unpaid leave; a one-off reduction, not a permanent change. |
| message_156 | confirm | first_salary_confirmed | salary | 38190000 | IDR | 2025-11-15 | 2025-11-15 | None | False | True | id | recorded | 2 | Cedar Health confirms the user's first salary of IDR 38,190,000 scheduled for 2025-11-15; payroll approved and sent for processing. |
| message_157 | confirm | duplicate_charge_dispute_open | event:event_18269 | None | INR | None | None | None | False | False | English | recorded | 2 | Bank states the duplicate card charge dispute (event_18269, INR 8800) is still open and no reversal/credit has been posted, so the refund is not confirmed. |
| message_158 | delay | gig_payout_pending | income_stream | None | IDR | None | None | None | False | False | id | recorded | 1 | ShiftPay platform payout is still pending; weekly earnings may change and the balance cannot be withdrawn until payment status is complete, so the gig income is unconfirmed. |
| message_159 | amend | bonus_unapproved | income_stream | None | IDR | None | None | None | False | False | Indonesian | recorded | 1 | Employer HarborWorks states the quarterly bonus is still pending performance review; final amount and payment date are not yet approved, so the bonus credit is unconfirmed. No regular salary change. |
| message_160 | cancel | seasonal_contract_ended | income_stream | None | IDR | None | 2026-03-26 | None | True | False | id | recorded | 1 | Northstar Labs payroll says the seasonal contract has ended; no off-season income or contract extension is confirmed, so the salary stream stops with no future amount confirmed. |
| message_161 | confirm | two_card_minimums | none | None | INR | None | None | None | False | None | en | recorded | 2 | Bank states two separate card accounts each have their own minimum payment due this month; paying one does not clear the other. No amounts or dates given. |
| message_162 | confirm | first_salary_confirmed | salary | 2024 | EUR | 2026-01-15 | 2026-01-15 | None | False | True | en | recorded | 2 | Employer BrightPath Media confirms the user's first salary of EUR 2024 crediting on 2026-01-15. |
| message_163 | noise | investment_value_moved | event:event_19182 | None | IDR | None | None | None | False | False | id | recorded | 2 | Nova Securities reports the portfolio valuation has declined; the investment has not been sold and there is no cash transaction, so no cash effect on the ledger. Valuation remains unrealized and market-dependent; no amount stated. |
| message_164 | confirm | duplicate_charge_dispute_open | event:event_19334 | None | USD | None | None | None | False | False | en | recorded | 2 | Bank states the duplicate card charge dispute (event_19334, USD 145.80) remains open and no reversal credit has been posted yet, so no refund can be counted. |
| message_165 | delay | salary_date_moved | salary | None | IDR | 2025-02-23 | 2025-02-23 | None | False | True | id | recorded | 2 | Employer Greenfield Foods confirms the salary is now expected on 2025-02-23, superseding the previously notified payroll date; no amount stated. |
| message_166 | cancel | seasonal_contract_ended | income_stream | None | None | None | 2025-12-30 | None | True | False | en | recorded | 1 | HarborWorks says the seasonal contract has ended as of 2025-12-30 with no confirmed off-season income or renewal, so the seasonal income stream stops and no future credit is confirmed. |
| message_167 | delay | foreign_refund_pending | none | None | None | None | None | None | False | False | en | recorded | 1 | Merchant BrightBasket says a foreign-currency refund (order ref MER-0167) is still processing; the home-currency credit amount is unknown and rate-dependent, so the credit is unconfirmed. |
| message_168 | delay | gig_payout_pending | income_stream | None | ZAR | None | None | None | False | False | English | recorded | 1 | QuickCrew gig platform states the next payout is still pending and not withdrawable; amounts may change, so the credit is unconfirmed. No amount or date given. |
| message_169 | amend | salary_increase | salary | 2424 | USD | None | 2026-07-15 | None | False | True | English | recorded | 1 | Employer Cobalt Systems confirms a regular monthly salary increase to USD 2424 effective 2026-07-15. |
| message_170 | confirm | salary_resumes | salary | 1914 | EUR | 2026-04-15 | 2026-04-15 | None | False | True | en | recorded | 1 | Employer confirms regular salary of EUR 1914 resumes on 2026-04-15; a new recurring childcare deduction/payment begins the same month but no amount is given. |
| message_171 | amend | salary_temporary_pay | salary | 1346.4 | EUR | None | None | None | False | True | English | recorded | 1 | Employer HarborWorks states the user's temporary reduced monthly pay of EUR 1346.40 continues for the next payroll cycle; no date given. |
| message_172 | delay | refund_pending | event:event_20379 | None | INR | None | None | None | False | False | English | recorded | 2 | Merchant states the ₹9,440 refund (event_20379) is initiated but not yet credited; completion may take up to ten business days, so the credit remains unconfirmed/pending. |
| message_173 | confirm | invoice_confirmed | income_stream | 35200 | ZAR | 2026-01-15 | 2026-01-15 | None | False | True | en | recorded | 1 | ClientDesk confirms one approved invoice of ZAR 35,200 settling on 2026-01-15; other submitted invoices remain unapproved and should not be counted. |
| message_174 | confirm | reimbursement_not_salary | event:event_20615 | None | IDR | None | None | None | True | False | id | recorded | 2 | The employer states the recent credit (event_20615, IDR 2,166,000) is a one-time reimbursement of prior work expenses, not regular salary; the claim is closed with no further reimbursements scheduled. No regular income amount or date changes. |
| message_175 | amend | rent_increase | rent | None | IDR | None | None | 1.12 | False | None | id | recorded | 1 | Lease renewal raises monthly rent by 12% (multiplier 1.12), effective from the next rent payment; no explicit new amount or date given. |
| message_176 | amend | arrears_one_time | salary | 260000 | INR | None | None | None | False | True | English | recorded | 1 | Employer confirms regular salary of INR 260,000 going forward, plus a separate one-time arrears adjustment of INR 117,000 which is not regular income and is excluded. |
| message_177 | delay | bonus_unapproved | income_stream | None | INR | None | None | None | False | False | English | recorded | 1 | Employer says the quarterly bonus is unapproved: neither amount nor payment date confirmed, so the bonus credit must not be counted as income. |
| message_178 | confirm | first_salary_confirmed | salary | 30400000 | IDR | 2026-04-15 | 2026-04-15 | None | False | True | Indonesian | recorded | 1 | Northstar Labs confirms the user's first salary of IDR 30,400,000 with a confirmed credit date of 2026-04-15. |
| message_179 | confirm | failed_debit_retry | event:event_21101 | 73 | EUR | None | None | None | False | None | English | recorded | 2 | Bank confirms the EUR 73 utility bill debit failed and remains outstanding; a further debit attempt will be made, so the obligation still stands. |
| message_180 | amend | household_income_ended | income_stream | 2827 | EUR | None | None | None | True | True | English | recorded | 1 | One household employment income has ended; the remaining confirmed monthly salary going forward is EUR 2827. |
| message_181 | confirm | first_salary_confirmed | salary | 2772 | EUR | 2024-06-15 | 2024-06-15 | None | False | True | English | recorded | 1 | Cobalt Systems confirms the user's first salary of EUR 2772 crediting on 2024-06-15. |
| message_182 | confirm | first_salary_confirmed | salary | 16910000 | IDR | 2025-11-15 | 2025-11-15 | None | False | True | id | recorded | 2 | Northstar Labs confirms the user's first salary of IDR 16,910,000 scheduled for 2025-11-15; payroll has approved and submitted the payment for processing. |
| message_183 | confirm | duplicate_charge_dispute_open | event:event_21582 | None | EUR | None | None | None | False | False | en | recorded | 2 | Bank states the duplicate card charge dispute (ref BAN-0183) for event_21582 is still open and no reversal/credit has been posted, so the charge stands and no refund credit is confirmed. |
| message_184 | delay | foreign_refund_pending | none | None | None | None | None | None | False | False | English | recorded | 1 | MarketDock says a foreign-currency refund (order MER-0184) is still processing; the home-currency credit amount is not final and depends on the settlement-date rate, so the credit is unconfirmed. |
| message_185 | noise | investment_value_moved | event:event_21785 | None | IDR | None | None | None | False | None | id | recorded | 2 | PocketVest reports the displayed portfolio valuation has fallen; no sale and no cash transaction occurred, so this is a non-cash valuation movement with no amount or date given. No effect on spendable income. |
| message_186 | cancel | seasonal_contract_ended | income_stream | None | IDR | None | 2026-03-26 | None | True | False | Indonesian | recorded | 1 | BrightPath Media payroll says the seasonal contract has ended; no off-season income or contract extension is confirmed, so the salary stream ends as of 2026-03-26. |
| message_187 | amend | household_income_ended | income_stream | 912 | USD | None | 2024-11-26 | None | True | True | English | recorded | 2 | Employer reports one household employment record ended; the remaining confirmed regular monthly salary going forward is USD 912, effective from the message date 2024-11-26. |
| message_188 | confirm | first_salary_confirmed | salary | 62000 | INR | 2026-01-15 | 2026-01-15 | None | False | True | en | recorded | 2 | Employer Cobalt Systems confirms the user's first salary of INR 62,000 crediting on 2026-01-15. |
| message_189 | cancel | seasonal_contract_ended | income_stream | None | IDR | None | 2024-02-29 | None | True | False | id | recorded | 1 | Employer Riverline Retail states the seasonal contract has ended; no off-season income or contract extension is confirmed, so the seasonal salary stream ends as of 2024-02-29. |
| message_190 | confirm | first_salary_confirmed | salary | 968 | EUR | 2025-08-15 | 2025-08-15 | None | False | True | English | recorded | 2 | Riverline Retail payroll confirms the user's first salary of EUR 968, approved and scheduled for 2025-08-15 (credit visible once the bank processes the payroll file). |
| message_191 | confirm | foreign_salary_confirmed | salary | 1680 | USD | 2025-11-15 | 2025-11-15 | None | False | True | English | recorded | 1 | Employer confirms a foreign-currency salary of USD 1680 payable 2025-11-15; the INR amount received depends on the settlement-date conversion rate. |
| message_192 | cancel | employment_ended | salary | None | ZAR | None | 2026-03-24 | None | True | False | English | recorded | 1 | Employer Cedar Health states the user's employment has ended and no regular salary payments are scheduled after the final settlement; salary income stream ends as of 2026-03-24. Final settlement details to follow separately (no amount given). |
| message_193 | amend | salary_temporary_pay | salary | 1528.56 | EUR | None | None | None | False | True | English | recorded | 2 | Employer states temporary reduced monthly pay of EUR 1528.56 continues for the next payroll cycle; no date given. |
| message_194 | amend | commission_unapproved | salary | 1548 | USD | None | None | None | False | False | English | recorded | 1 | Employer confirms base salary of USD 1548 going forward; commission on open deals is unapproved/pending and must not be counted as income. |
| message_195 | amend | salary_reduced | salary | 702 | USD | None | None | None | False | True | en | recorded | 1 | Employer states the user's next salary is reduced to USD 702 due to approved unpaid leave; a one-off reduction, not a change to the regular pay level. |
| message_196 | confirm | first_salary_confirmed | salary | 53680 | ZAR | 2024-12-15 | 2024-12-15 | None | False | True | en | recorded | 1 | Employer Cobalt Systems confirms the user's first salary of ZAR 53,680 on 2024-12-15. |
| message_197 | delay | duplicate_charge_dispute_open | event:event_23203 | None | IDR | None | None | None | False | False | id | recorded | 2 | Bank says the duplicate card charge dispute is still open and the reversal funds have not been credited; the reversal credit is not confirmed. |
| message_198 | confirm | failed_debit_retry | event:event_23306 | 192 | EUR | None | None | None | False | None | English | recorded | 2 | Bank confirms the failed EUR 192 utility bill debit (event_23306) remains outstanding and will be retried; the obligation still stands. |
| message_199 | delay | bonus_unapproved | income_stream | None | USD | None | None | None | False | False | English | recorded | 1 | Employer states the quarterly bonus is not yet approved: neither amount nor payment date confirmed, so the bonus credit is unconfirmed. No regular salary change stated. |
| message_200 | confirm | first_salary_confirmed | salary | 214000 | INR | 2024-06-15 | 2024-06-15 | None | False | True | English | recorded | 2 | Riverline Retail payroll confirms the user's first salary of INR 214,000 crediting on 2024-06-15. |
| message_201 | confirm | failed_debit_retry | event:event_23855 | 42 | EUR | None | None | None | False | None | English | recorded | 2 | Bank confirms the failed EUR 42 utility bill debit (event_23855) remains outstanding and will be retried; the obligation stands, no new amount or date given. |
| message_202 | amend | self_transfer | none | None | None | None | None | None | False | False | en | recorded | 1 | Bank confirms a matching debit/credit pair is a transfer between the user's own accounts (ref BAN-0202); the credit is not income. |
| message_203 | amend | household_income_ended | income_stream | 48260000 | IDR | None | 2024-11-23 | None | True | True | id | recorded | 1 | One household income stream has ended; remaining confirmed monthly salary is IDR 48,260,000, effective from the message date. The ended income should be excluded from future forecasts. |
| message_204 | confirm | foreign_salary_confirmed | salary | 1485 | EUR | 2025-05-15 | 2025-05-15 | None | False | True | en | recorded | 1 | Employer confirms a foreign-currency salary of EUR 1485 payable 2025-05-15; the ZAR amount received depends on the settlement-date conversion rate. |
| message_205 | noise | investment_value_moved | event:event_24352 | None | INR | None | None | None | False | None | English | recorded | 2 | Unrealized portfolio valuation moved down; no sale and no cash transaction, so no cash-flow impact on the ledger event. |
| message_206 | cancel | seasonal_contract_ended | income_stream | None | INR | None | 2024-02-28 | None | True | False | English | recorded | 1 | Greenfield Foods states the user's seasonal contract has ended with no confirmed off-season income or renewal; the seasonal salary stream ends as of 2024-02-28 and no future amount is confirmed. |
| message_207 | noise | investment_value_moved | event:event_24534 | None | EUR | None | None | None | False | False | en | recorded | 2 | Unrealized portfolio valuation rose; no units sold and no cash proceeds, so no spendable income. No amount or date given; the valuation remains non-cash/unrealized. |
| message_208 | delay | foreign_charge_pending | none | None | None | None | None | None | False | None | English | recorded | 1 | Merchant CartLane says a recent purchase (order ref MER-0208) was charged in a foreign currency; the final EUR amount is not yet known and will be set by the bank's rate at settlement. No amount or date given. |
| message_209 | delay | prize_pending | none | None | None | None | None | None | False | False | English | recorded | 1 | PrizeLine states the verified prize payment is still processing and has not been credited; the credit remains unconfirmed with no amount or date given. No instructions or fee requests present. |
| message_210 | confirm | first_salary_confirmed | salary | 38280 | ZAR | 2025-11-15 | 2025-11-15 | None | False | True | en | recorded | 2 | Employer Northstar Labs confirms the user's first salary of ZAR 38,280, approved and scheduled for 2025-11-15 (credit visible once the bank processes the payroll file). |
| message_211 | amend | arrears_one_time | salary | 103000 | INR | None | None | None | False | True | English | recorded | 1 | Employer confirms regular salary of INR 103,000 for the next payroll, plus a separate one-time arrears adjustment of INR 46,350 which is not part of regular income. Report regular pay only. |
| message_212 | cancel | bonus_unapproved | income_stream | None | IDR | None | None | None | False | False | id | recorded | 1 | Employer says the quarterly bonus is still pending performance review; final amount and payment date are not approved, so the bonus credit is unconfirmed and must not be counted as income. |
| message_213 | confirm | self_transfer | none | None | IDR | None | None | None | False | False | Indonesian | recorded | 1 | Bank confirms a matching debit and credit were a transfer between two accounts owned by the user (self-transfer, not income); both entries remain visible in history. Ref BAN-0213. |
| message_214 | delay | foreign_refund_pending | none | None | None | None | None | None | False | False | English | recorded | 1 | Merchant says a foreign-currency refund (order ref MER-0214) is still processing; the home-currency (EUR) credit amount is not final and depends on the settlement-date rate, so the credit is unconfirmed. No amount or date given. |
| message_215 | delay | refund_pending | event:event_25342 | None | IDR | None | None | None | False | False | Indonesian | recorded | 2 | UrbanCart says the refund (order ref MER-0215) has been processed but has not yet credited the account; most refunds complete within ten business days. The pending refund credit of IDR 1,444,000 (event_25342) remains unconfirmed with no specific new date. |

## Amendments applied (by user)

- **user_26**: income_unconfirmed(all_income) ← message_18; confirmed_credit(income, 30780000, from 2025-08-15) ← message_18
- **user_27**: income_unconfirmed(all_income) ← message_19
- **user_28**: salary_amount(salary, 1452) ← message_20
- **user_29**: stream_ended(all_income) ← message_21
- **user_32**: salary_amount(salary, 54120, from 2025-02-15) ← message_22; new_income(salary, 54120, from 2025-02-15) ← message_22
- **user_33**: amount(event_3051, 1995) ← image_06
- **user_34**: income_unconfirmed(all_income) ← message_24; confirmed_credit(income, 196000, from 2024-12-15) ← message_24
- **user_35**: amount(event_3231, 8528.1) ← image_07
- **user_36**: salary_amount(salary, 2988, from 2026-07-15) ← message_26
- **user_37**: salary_amount(salary, 21090000) ← message_27
- **user_40**: salary_amount(salary, 1760, from 2024-06-15) ← message_29; new_income(salary, 1760, from 2024-06-15) ← message_29
- **user_42**: stream_ended(income:secondary) ← message_30; salary_cap(salary, 148000) ← message_30
- **user_43**: salary_amount(salary, 32870000, from 2024-09-15) ← message_31; new_income(salary, 32870000, from 2024-09-15) ← message_31
- **user_44**: salary_amount(salary, 115000, from 2025-02-15) ← message_32; new_income(salary, 115000, from 2025-02-15) ← message_32
- **user_45**: salary_amount(salary, 17290000, from 2026-07-15) ← message_33
- **user_47**: income_unconfirmed(all_income) ← message_34
- **user_48**: amount(event_4535, 15339) ← image_08
- **user_49**: salary_amount(salary, 31464000) ← message_36
- **user_50**: stream_ended(income:secondary) ← message_37; salary_cap(salary, 126000) ← message_37
- **user_52**: salary_amount(salary, 69000, from 2024-06-15) ← message_38; new_income(salary, 69000, from 2024-06-15) ← message_38
- **user_54**: salary_amount(salary, 42460, from 2026-07-15) ← message_40
- **user_55**: amount(event_5170, 723.0) ← image_09
- **user_58**: stream_ended(income:secondary) ← message_42; salary_cap(salary, 25840000) ← message_42
- **user_59**: income_unconfirmed(all_income) ← message_43
- **user_60**: salary_amount(salary, 530.4) ← message_44
- **user_61**: stream_ended(all_income) ← message_45
- **user_62**: income_unconfirmed(all_income) ← message_46; confirmed_credit(income, 2112, from 2025-08-15) ← message_46
- **user_64**: amount(event_6033, 79679.26) ← image_10
- **user_66**: income_unconfirmed(all_income) ← message_49; confirmed_credit(income, 116000, from 2026-04-15) ← message_49
- **user_68**: salary_date(salary, from 2025-02-23) ← message_50
- **user_69**: expense_multiplier(category:rent, x1.12) ← message_51
- **user_71**: salary_amount(salary, 11019997.68, from 2025-05-15) ← message_53
- **user_72**: salary_amount(salary, 18700, from 2026-07-15) ← message_54; new_income(salary, 18700, from 2026-07-15) ← message_54
- **user_73**: amount(event_6859, 3650) ← image_11; expense_multiplier(category:rent, x1.12) ← message_55
- **user_74**: income_unconfirmed(all_income) ← message_56; confirmed_credit(income, 26180, from 2025-08-15) ← message_56
- **user_75**: stream_ended(all_income) ← message_57
- **user_78**: amount(event_7307, 33.5) ← image_12
- **user_81**: expense_multiplier(category:rent, x1.12) ← message_61
- **user_82**: salary_amount(salary, 1752) ← message_62
- **user_83**: salary_amount(salary, 62000, from 2025-05-15) ← message_63; salary_date(salary, from 2025-05-15) ← message_63
- **user_84**: amount(event_7941, 2298) ← image_13
- **user_85**: salary_amount(salary, 8618400) ← message_65
- **user_87**: salary_amount(salary, 251000, from 2026-01-15) ← message_66; salary_date(salary, from 2026-01-15) ← message_66
- **user_90**: income_unconfirmed(all_income) ← message_68; confirmed_credit(income, 13420, from 2026-07-15) ← message_68
- **user_94**: income_unconfirmed(all_income) ← message_72; confirmed_credit(income, 924, from 2024-12-15) ← message_72
- **user_95**: salary_date(salary, from 2025-05-23) ← message_73
- **user_98**: salary_amount(salary, 36080, from 2025-08-15) ← message_74
- **user_101**: amount(event_9421, 4543) ← image_14
- **user_102**: income_unconfirmed(all_income) ← message_76; confirmed_credit(income, 1419, from 2026-04-15) ← message_76
- **user_103**: salary_amount(salary, 164880) ← message_77
- **user_105**: amount(event_9806, 9968) ← image_15
- **user_106**: salary_amount(salary, 1815, from 2024-12-15) ← message_80; new_income(salary, 1815, from 2024-12-15) ← message_80
- **user_107**: salary_amount(salary, 2123, from 2025-05-15) ← message_81; new_income(salary, 2123, from 2025-05-15) ← message_81
- **user_110**: income_unconfirmed(all_income) ← message_83; confirmed_credit(income, 16720, from 2025-08-15) ← message_83
- **user_111**: stream_ended(all_income) ← message_84
- **user_112**: salary_amount(salary, 627, from 2024-06-15) ← message_85; new_income(salary, 627, from 2024-06-15) ← message_85
- **user_113**: amount(event_10521, 393.22) ← image_16; salary_amount(salary, 107995.68, from 2026-09-15) ← message_86
- **user_114**: salary_amount(salary, 148200) ← message_87
- **user_117**: salary_amount(salary, 1188, from 2026-07-15) ← message_89
- **user_118**: salary_amount(salary, 759) ← message_90
- **user_119**: salary_amount(salary, 176000, from 2025-05-15) ← message_91; salary_date(salary, from 2025-05-15) ← message_91
- **user_122**: income_unconfirmed(all_income) ← message_93; confirmed_credit(income, 15390000, from 2025-08-15) ← message_93
- **user_123**: income_unconfirmed(all_income) ← message_94
- **user_125**: salary_amount(salary, 14960, from 2025-11-15) ← message_95
- **user_126**: income_unconfirmed(all_income) ← message_96; confirmed_credit(income, 152000, from 2026-07-15) ← message_96
- **user_127**: salary_amount(salary, 50160, from 2024-09-15) ← message_97; salary_date(salary, from 2024-09-15) ← message_97
- **user_130**: salary_amount(salary, 2177.28) ← message_100
- **user_131**: salary_date(salary, from 2025-05-23) ← message_101
- **user_132**: salary_amount(salary, 1193.4) ← message_102
- **user_133**: stream_ended(all_income) ← message_103
- **user_135**: salary_amount(salary, 828, from 2026-07-15) ← message_104
- **user_137**: expense_multiplier(category:rent, x1.12) ← message_105
- **user_140**: salary_amount(salary, 31900, from 2025-02-15) ← message_107; new_income(salary, 31900, from 2025-02-15) ← message_107
- **user_142**: income_unconfirmed(all_income) ← message_109; confirmed_credit(income, 2040, from 2024-12-15) ← message_109
- **user_144**: salary_amount(salary, 864, from 2026-07-15) ← message_111; new_income(salary, 864, from 2026-07-15) ← message_111
- **user_145**: salary_amount(salary, 258000) ← message_112
- **user_147**: salary_amount(salary, 1529, from 2026-04-15) ← message_113; salary_date(salary, from 2026-04-15) ← message_113
- **user_150**: salary_amount(salary, 893.75) ← message_115
- **user_151**: salary_amount(salary, 46170000, from 2024-09-15) ← message_116; new_income(salary, 46170000, from 2024-09-15) ← message_116
- **user_154**: stream_ended(income:secondary) ← message_119; salary_cap(salary, 1628) ← message_119
- **user_155**: salary_amount(salary, 84000, from 2025-05-15) ← message_120; salary_date(salary, from 2025-05-15) ← message_120
- **user_157**: salary_amount(salary, 23940000) ← message_122
- **user_159**: income_unconfirmed(all_income) ← message_123
- **user_160**: salary_amount(salary, 1672, from 2024-06-15) ← message_124; new_income(salary, 1672, from 2024-06-15) ← message_124
- **user_161**: salary_amount(salary, 26790000, from 2025-11-15) ← message_125; new_income(salary, 26790000, from 2025-11-15) ← message_125
- **user_162**: salary_amount(salary, 29070000, from 2026-07-15) ← message_126
- **user_163**: salary_amount(salary, 30400000) ← message_127
- **user_165**: stream_ended(all_income) ← message_129
- **user_166**: income_unconfirmed(all_income) ← message_130; confirmed_credit(income, 2340, from 2024-12-15) ← message_130
- **user_167**: salary_date(salary, from 2025-05-23) ← message_131
- **user_168**: salary_amount(salary, 137150) ← message_132
- **user_173**: salary_amount(salary, 106995.72, from 2025-11-15) ← message_137
- **user_175**: salary_amount(salary, 1924.56) ← message_138
- **user_177**: salary_amount(salary, 1731.6) ← message_140
- **user_178**: income_unconfirmed(all_income) ← message_141; confirmed_credit(income, 2376, from 2024-12-15) ← message_141
- **user_180**: salary_amount(salary, 59000, from 2026-07-15) ← message_143; new_income(salary, 59000, from 2026-07-15) ← message_143
- **user_185**: expense_multiplier(category:rent, x1.12) ← message_147
- **user_186**: salary_amount(salary, 31889) ← message_148
- **user_187**: salary_amount(salary, 145000, from 2024-09-15) ← message_149; new_income(salary, 145000, from 2024-09-15) ← message_149
- **user_189**: salary_amount(salary, 627, from 2026-07-15) ← message_151
- **user_193**: salary_amount(salary, 1750.32) ← message_153
- **user_194**: salary_date(salary, from 2025-08-23) ← message_154
- **user_195**: salary_amount(salary, 1222.65) ← message_155
- **user_197**: salary_amount(salary, 38190000, from 2025-11-15) ← message_156; new_income(salary, 38190000, from 2025-11-15) ← message_156
- **user_199**: income_unconfirmed(all_income) ← message_158
- **user_201**: stream_ended(all_income) ← message_160
- **user_204**: salary_amount(salary, 2024, from 2026-01-15) ← message_162; new_income(salary, 2024, from 2026-01-15) ← message_162
- **user_212**: salary_date(salary, from 2025-02-23) ← message_165
- **user_213**: stream_ended(all_income) ← message_166
- **user_215**: income_unconfirmed(all_income) ← message_168
- **user_216**: salary_amount(salary, 2424, from 2026-07-15) ← message_169
- **user_219**: salary_amount(salary, 1914, from 2026-04-15) ← message_170; salary_date(salary, from 2026-04-15) ← message_170
- **user_220**: salary_amount(salary, 1346.4) ← message_171
- **user_222**: income_unconfirmed(all_income) ← message_173; confirmed_credit(income, 35200, from 2026-01-15) ← message_173
- **user_225**: expense_multiplier(category:rent, x1.12) ← message_175
- **user_226**: salary_amount(salary, 260000) ← message_176
- **user_228**: salary_amount(salary, 30400000, from 2026-04-15) ← message_178; new_income(salary, 30400000, from 2026-04-15) ← message_178
- **user_230**: stream_ended(income:secondary) ← message_180; salary_cap(salary, 2827) ← message_180
- **user_232**: salary_amount(salary, 2772, from 2024-06-15) ← message_181; new_income(salary, 2772, from 2024-06-15) ← message_181
- **user_233**: salary_amount(salary, 16910000, from 2025-11-15) ← message_182; new_income(salary, 16910000, from 2025-11-15) ← message_182
- **user_237**: stream_ended(all_income) ← message_186
- **user_238**: stream_ended(income:secondary) ← message_187; salary_cap(salary, 912) ← message_187
- **user_240**: salary_amount(salary, 62000, from 2026-01-15) ← message_188; new_income(salary, 62000, from 2026-01-15) ← message_188
- **user_241**: stream_ended(all_income) ← message_189
- **user_242**: salary_amount(salary, 968, from 2025-08-15) ← message_190; new_income(salary, 968, from 2025-08-15) ← message_190
- **user_245**: salary_amount(salary, 139994.40, from 2025-11-15) ← message_191
- **user_246**: stream_ended(all_income) ← message_192
- **user_247**: salary_amount(salary, 1528.56) ← message_193
- **user_249**: salary_amount(salary, 702) ← message_195
- **user_250**: salary_amount(salary, 53680, from 2024-12-15) ← message_196; new_income(salary, 53680, from 2024-12-15) ← message_196
- **user_256**: salary_amount(salary, 214000, from 2024-06-15) ← message_200; new_income(salary, 214000, from 2024-06-15) ← message_200
- **user_262**: stream_ended(income:secondary) ← message_203; salary_cap(salary, 48260000) ← message_203
- **user_263**: salary_amount(salary, 29700, from 2025-05-15) ← message_204
- **user_265**: stream_ended(all_income) ← message_206
- **user_269**: salary_amount(salary, 38280, from 2025-11-15) ← message_210; new_income(salary, 38280, from 2025-11-15) ← message_210
- **user_271**: salary_amount(salary, 103000) ← message_211

## Embedded instructions detected (matched phrases)

- image_07: THANK YOU VISIT AGAIN !
- message_50: Please use the revised date for anything you normally pay around payday.
- message_67: Pay the processing charge now to avoid losing the claim; Pay the processing charge now to avoid losing the claim.; Pay the release charge today to receive the funds immediately; Pay the release charge today to receive the funds immediately.
- message_73: Please use the revised date for anything you normally pay around payday.
- message_119: Any income that has ended should be removed from future estimates.
- message_131: Please use the revised date for anything you normally pay around payday.
- message_142: Bayar biaya pemrosesan sekarang agar klaim tidak hangus; Bayar biaya pemrosesan sekarang agar klaim tidak hangus.; Bayar biaya pencairan hari ini agar dana segera diterima; Bayar biaya pencairan hari ini agar dana segera diterima.
- message_154: Please use the revised date for anything you normally pay around payday.
- message_187: Any income that has ended should be removed from future estimates.

## Safer-reading resolutions and dropped amendments

- message_18: only the confirmed invoice is counted; other freelance income unconfirmed (safer)
- message_19: platform payout pending / not withdrawable — gig income not projected (safer)
- message_24: only the confirmed invoice is counted; other freelance income unconfirmed (safer)
- message_30: household income ended — primary stream kept, capped at the stated remaining amount (safer reading)
- message_34: platform payout pending / not withdrawable — gig income not projected (safer)
- message_37: household income ended — primary stream kept, capped at the stated remaining amount (safer reading)
- message_42: household income ended — primary stream kept, capped at the stated remaining amount (safer reading)
- message_43: platform payout pending / not withdrawable — gig income not projected (safer)
- message_46: only the confirmed invoice is counted; other freelance income unconfirmed (safer)
- message_49: only the confirmed invoice is counted; other freelance income unconfirmed (safer)
- message_56: only the confirmed invoice is counted; other freelance income unconfirmed (safer)
- message_64: unresolvable — no amendment applied ( [unresolvable: The message only points to a receipt for the final amount ("The receipt has the final amount. Order ref MER-0064."), but no receipt image is available (inspect_image on MER-0064 returns an error) and the linked ledger row event_7941 has a blank amount. No amount can be read from the evidence, so the expense figure cannot be determined.])
- message_68: only the confirmed invoice is counted; other freelance income unconfirmed (safer)
- message_72: only the confirmed invoice is counted; other freelance income unconfirmed (safer)
- message_76: only the confirmed invoice is counted; other freelance income unconfirmed (safer)
- message_83: only the confirmed invoice is counted; other freelance income unconfirmed (safer)
- message_93: only the confirmed invoice is counted; other freelance income unconfirmed (safer)
- message_94: platform payout pending / not withdrawable — gig income not projected (safer)
- message_96: only the confirmed invoice is counted; other freelance income unconfirmed (safer)
- message_109: only the confirmed invoice is counted; other freelance income unconfirmed (safer)
- message_119: household income ended — primary stream kept, capped at the stated remaining amount (safer reading)
- message_123: platform payout pending / not withdrawable — gig income not projected (safer)
- message_130: only the confirmed invoice is counted; other freelance income unconfirmed (safer)
- message_141: only the confirmed invoice is counted; other freelance income unconfirmed (safer)
- message_158: platform payout pending / not withdrawable — gig income not projected (safer)
- message_168: platform payout pending / not withdrawable — gig income not projected (safer)
- message_173: only the confirmed invoice is counted; other freelance income unconfirmed (safer)
- message_180: household income ended — primary stream kept, capped at the stated remaining amount (safer reading)
- message_187: household income ended — primary stream kept, capped at the stated remaining amount (safer reading)
- message_203: household income ended — primary stream kept, capped at the stated remaining amount (safer reading)

## Retries (items that did not pass on the first try)

- none — every response passed schema validation on the first try

## Skipped / stops

- none
