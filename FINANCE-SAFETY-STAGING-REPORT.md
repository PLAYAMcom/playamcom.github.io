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
