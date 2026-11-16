# PLAYAM Finance Safety — Staging Work Report

Date: 2026-11-16

## Scope and safety boundaries

- Staging Supabase project only: `pwnjrdedeoxbmtfywhkk`.
- Dedicated branch: `codex/playam-finance-safety`.
- No production database, production app, payment activation, cash rewards, or Friendship Court gameplay changes.
- The existing admin dashboard was not overwritten. This work adds a separate finance-admin staging page.

## Added

### Private evidence storage

- Private Storage bucket: `playam-finance-evidence`.
- Maximum object size: 10 MiB.
- Accepted declared MIME types: PDF, JPEG, PNG.
- Read access requires active finance-admin role and MFA assurance level `aal2`.
- Upload access requires active finance-admin role and `aal2`, and is limited to the administrator who recorded the pending reconciliation.
- Objects are stored under a reconciliation UUID folder.
- Evidence attachment checks the stored object's metadata against the submitted MIME type and size.
- No public bucket or public URL is used. The admin page generates short-lived signed links only after the authenticated admin list function returns the record.

### Database workflow

- Added evidence metadata to `playam_financial_cash_reconciliations`.
- Added a protected helper to check active finance-admin role and `aal2`.
- Added an upload eligibility helper.
- Added `playam_attach_cash_reconciliation_evidence_v1`.
- Updated `playam_verify_cash_reconciliation_v1` to require attached evidence and a different MFA-authenticated administrator from the recorder/uploader.
- Added `playam_list_cash_reconciliations_v1`, restricted to active finance administrators with `aal2`.
- The balance must match the recorded statement balance exactly; a mismatch leaves the record pending.
- Evidence attachment and verification are audited.

### Admin interface

New file: `finance-admin-staging.html`

- Password sign-in followed by an MFA step-up challenge.
- Uses staging Supabase configuration only.
- Records statement metadata and amount in minor units.
- Allows the recorder to upload a redacted statement.
- Allows another finance administrator to open the evidence using a short-lived signed URL and submit the independent verification.
- Does not activate rewards, create reward commitments, or initiate payouts.

## Verification performed

- Confirmed the bucket exists, is private, has a 10 MiB limit, and has the expected MIME allowlist.
- Confirmed the storage SELECT and INSERT policies require the protected finance-admin/MFA checks.
- Confirmed the evidence columns exist.
- Confirmed the attach function compares supplied MIME/size against the uploaded Storage object's metadata.
- Confirmed the verification function requires attached evidence.
- Confirmed the reconciliation list function checks active finance-admin role and `aal2`.
- Confirmed there are currently zero reconciliation records and zero audit records.

## Not yet tested

- Browser rendering and mobile layout.
- Real admin login and MFA challenge using a finance-admin test account.
- Real file upload, signed download, and two-distinct-admin verification.
- Negative tests for non-admin, MFA level below `aal2`, wrong recorder/verifier, wrong amount, invalid file type, and oversized file.
- Malware scanning/content-signature validation of uploaded documents.
- Automated link between verified bank cash, available cash, reserve coverage, and funded reward commitments.

## Important limitations

A human administrator's inspection of a statement is still a manual evidence control, not an automated bank balance integration. File extension and MIME metadata are not malware/content-signature scanning. Do not treat a verified reconciliation as spendable reward funding until the cash-availability calculation, liabilities/reserve exclusions, and funded-commitment gate are implemented and tested.

Cash rewards must remain disabled. No production deployment or payment activation is authorised by this work.


## Cash position and reserve report added

A further staging-only migration added `playam_get_cash_position_v1()`, a read-only RPC restricted to active finance administrators with MFA assurance `aal2`.

It reports, by currency:
- Latest verified statements per recorded account, counting only statements dated within the last 7 days.
- Creator available, pending, and reserved-withdrawal balances as separate liability components.
- Unpaid verified reward commitments.
- Cash after those liabilities.
- The configured three-month reserve target and a provisional NGN estimate after reserve.

The finance-admin page now has a "Cash position & three-month reserve" section to call and display this report.

### Current staging data and limits

At the time of verification:
- Cash reconciliations: 0.
- Creator earnings wallet rows: 0.
- Funded reward commitment rows: 0.
- Essential monthly expense baseline: not configured.
- Reserve target: 3 months.
- Cash rewards: disabled.

Therefore the report cannot show an actual available cash amount yet. It explicitly returns `safe_to_commit_new_cash_rewards=false` and lists the missing evidence and account-coverage blockers.

The function is `SECURITY DEFINER` with an empty search path and performs its own active finance-admin plus `aal2` checks. Anonymous EXECUTE is revoked; authenticated EXECUTE is required for the signed-in admin page. A no-auth invocation was checked and rejected. Supabase's security advisor still flags authenticated-callable SECURITY DEFINER functions as a review warning; this function's internal authorisation guard must be included in the manual review.

### Important accounting caveat

This is a conservative, provisional management estimate, not a bank feed or a live bank balance. It cannot prove all PLAYAM accounts were entered, nor account for transactions that happened after a statement date. The report deliberately never authorises reward commitments. Verified bank/API integrations, account completeness attestation, fresh reconciliations and independent operational tests remain necessary.


## Income and expense ledger interface

Added an "Income and expense ledger" section to `finance-admin-staging.html`.

- Uses the existing MFA-protected `playam_record_financial_entry_v1` function to record income and expense entries.
- Supports the existing categories for LIVE platform share, advertising, sponsorship, marketplace income, payment fees, creator withdrawal fees, refunds/chargebacks, fraud losses, hosting, messaging, security, support, moderation, marketing, staffing, legal/accounting, taxes and other items.
- Stores amounts in integer minor units and uses a unique idempotency key per submission.
- Uses the existing financial summary RPC for income, expense and net operating totals by currency.
- Added `playam_list_financial_entries_v1`, a read-only listing function restricted to active finance administrators with MFA assurance `aal2`.
- The finance ledger remains append-only; corrections should be entered as traceable reversing entries rather than editing history.

### Validation and limits

- Confirmed the page contains the ledger form and calls the existing recording, summary and new listing RPCs.
- Confirmed the page references staging Supabase only; no production project reference is present.
- Confirmed anonymous execution of the new ledger-list RPC is denied.
- Existing ledger table has RLS enabled and existing database immutability trigger retained.
- No financial entries were inserted during this work.
- Browser form submission and real finance-admin MFA access have not yet been tested.

The ledger is an administrative record, not an automatic feed from bank, Paystack, ad networks, or invoices. Amounts must be reconciled against source statements and transaction reports. Net operating result in the ledger is not the same as cash available or audited profit.


## Liability register added

Added staging-only tables:
- `playam_liability_register` for supplier bills, tax payable, customer refunds, chargeback exposure, sponsor refund obligations and other payables.
- `playam_liability_register_events` for creation and settlement history.

Protected RPCs:
- `playam_create_liability_v1`
- `playam_settle_liability_v1`
- `playam_list_liabilities_v1`
- `playam_get_liability_summary_v1`

All four require an authenticated active finance administrator or super administrator with MFA assurance `aal2`. Direct client table access is revoked and RLS is enabled. Anonymous execution was checked and denied. Settlement is locked to the row, must be positive, cannot exceed the outstanding amount, and creates a separate event record.

The finance-admin staging page now includes forms to create liabilities, record verified settlements, and review open/overdue totals by currency.

### Cash position integration

Updated `playam_get_cash_position_v1` to deduct open/partially settled liabilities from the provisional cash position, in addition to creator wallet liabilities and unpaid verified reward commitments. The report labels these separately to help avoid double counting.

### Current state and limitations

- Liability records: 0.
- Liability event records: 0.
- No real liabilities or payments were fabricated or entered.
- The cash calculation still returns `safe_to_commit_new_cash_rewards=false` and `cash_account_coverage_complete=false`.
- The liability register is manual and depends on accurate, complete administrator entries. It is not connected to supplier invoices, tax systems, refund processors, or bank feeds.
- Browser workflow, MFA admin access, and settlement reconciliation have not yet been tested with real finance-admin accounts.
- Creator balances and funded reward commitments remain separate sources and must not be duplicated in this register.


## Unified financial management overview

Added a consolidated overview to `finance-admin-staging.html` on the staging-only finance branch.

The page calls the existing MFA-protected functions:
- `playam_get_cash_position_v1` for recent verified statement cash, creator balances, verified reward commitments, other recorded liabilities, reserve estimate and reward blockers.
- `playam_get_liability_summary_v1` for open and overdue payable totals.
- `playam_get_financial_summary_v1` for recorded income, expenses and net operating result over a selectable date range.

The view keeps currencies separate, displays the reserve and cash-account coverage warnings, and explicitly states that new cash rewards are not authorised. It describes ledger profit as recorded operating result, not audited profit, and cash as a provisional statement-based estimate, not a live bank balance.

### Verification and remaining limits

- Confirmed the updated page was committed and fetched back from `codex/playam-finance-safety`.
- Confirmed the dashboard markup, event handler and all three RPC calls are present.
- Confirmed the page uses the staging Supabase project reference and contains no production project reference.
- The staging security advisor currently reports 25 RLS-enabled tables without policies, 40 authenticated-callable SECURITY DEFINER functions, and leaked-password protection disabled. These are review findings, not all confirmed vulnerabilities; individual functions require authorization review. No blanket permission changes were made.
- No live browser test with a finance administrator, MFA, or populated financial records has been completed. No sample balances or liabilities were inserted.
- No production deployment, payment activation, reward activation, or Friendship Court/gameplay changes were made.

This dashboard is not a launch approval, accounting certification, bank reconciliation guarantee, or permission to spend. Full account coverage, real source-document reconciliation, ledger completeness, administrator testing and a separate launch decision remain required.
