# PLAYAM Creator Withdrawal Safety — Staging Report

## Scope

This work is limited to the Supabase staging project `pwnjrdedeoxbmtfywhkk` and Git branch `codex/playam-creator-withdrawal-safety`. It does not change production, activate cash rewards, initiate real payouts, or modify Friendship Court/gameplay.

## Batch 24 — Fee-preview page and legacy-path safety block

### Creator page

Updated `creator-withdrawal-staging.html` with a non-transactional NGN fee preview. It estimates the Paystack transfer fee band using the net transfer amount and displays estimated creator proceeds. It warns when the estimated net transfer reaches the ₦10,000 stamp-duty threshold.

The page labels the estimate as illustrative, not a live provider quote. It does not submit a withdrawal, reserve wallet funds, or initiate Paystack transfers.

### Staging database guard

Applied migration `temporarily_block_legacy_gross_withdrawal_path` to staging only.

- `playam_request_creator_withdrawal_v1` now rejects new withdrawal requests with an explicit message that fee disclosure and creator confirmation are not yet complete. This prevents the old gross-only request route from reserving funds without consent.
- `playam_prepare_creator_withdrawal_transfer_v1` now rejects payout preparation until the fee-confirmed net-transfer workflow is implemented. This prevents the existing service-role payout Edge Function from preparing a gross-only transfer.
- Function security-definer status and intended grants were retained: request RPC is authenticated-only; transfer preparation is service-role-only.
- Verified with database privilege checks: anonymous execution is false for both functions; authenticated execution is true only for the request RPC; service-role execution is true only for the transfer-preparation RPC.
- Staging withdrawal request table currently contains zero rows. No wallet transactions were created.

### Fee-policy handling

The separate stamp-duty payer remains unresolved. Withdrawals for which the separate ₦50 stamp duty applies must remain blocked until the payer policy is explicitly approved. The fee preview does not imply a confirmed deduction policy.

### Verification limits

- Re-fetched the committed page and checked staging project reference, fee preview, no request-RPC/Paystack invocation, pending stamp-duty notice and non-transactional disclosure.
- Verified the staging database function grants and that the withdrawal request table remains empty.
- No browser-based creator login/preview test was run.
- No signed-in withdrawal attempt was made; no real or test Paystack transfer was initiated.
- The quote table and authenticated quote/confirmation RPCs have now been added in Batch 25. The net payout is stored on the withdrawal request, but the transfer preparation function remains deliberately blocked, so no payout can proceed yet. Actual provider-fee webhook reconciliation and wallet adjustment/refund logic remain unimplemented.
- Existing payout Edge Functions remain deployed in staging, but the database transfer-preparation guard blocks them before a Paystack transfer can be initiated.
- This is not approval to enable withdrawals or cash rewards.

## Next implementation steps

1. Design an expiring, immutable fee quote tied to creator, amount, payout destination, provider, currency and policy version.
2. Add an authenticated confirmation RPC that atomically validates the quote and reserves the gross amount only after explicit consent.
3. Keep stamp-duty-applicable quotes blocked while payer policy is pending.
4. Update transfer preparation and Paystack payout to send only the approved net transfer amount.
5. Update webhook verification to compare the provider's amount against net transfer and record actual fee/reversal events idempotently.
6. Reconcile creator wallet accounting so provider-fee differences and reversals are returned correctly without counting fees as PLAYAM revenue.
7. Run staging integration tests for expiry, replay, concurrency, success, failure, fee mismatch, reversal and duplicate webhook events before any activation decision.


## Batch 25 — Expiring fee quote and explicit confirmation foundation

Applied staging migrations:
- `add_creator_withdrawal_fee_quote_and_confirmation_flow`
- `restrict_creator_fee_quote_rpcs_to_authenticated_creators`

### Added quote storage

Created `playam_creator_withdrawal_fee_quotes` with:
- Creator and verified payout destination binding.
- Gross amount, estimated creator-paid transfer fee, net transfer amount and stamp-duty applicability.
- Currency, fee-policy version, idempotency key, status and 10-minute expiry.
- Accepted withdrawal request linkage and acceptance timestamp.
- RLS enabled; no direct client table grants. Service role only has table-level access.

### Added authenticated RPCs

- `playam_create_creator_withdrawal_fee_quote_v1` validates the signed-in creator, amount limits, active verified Paystack NGN destination and available wallet balance. It calculates the published fee band from the estimated net amount and returns an expiring quote. It does not reserve funds.
- `playam_confirm_creator_withdrawal_fee_quote_v1` locks and validates the quote, rechecks destination eligibility and available funds, then atomically creates the pending withdrawal request, reserves the gross amount in the existing ledger, records explicit creator confirmation and marks the quote accepted.
- Quotes with stamp duty applicable and payer still set to `pending_policy` are rejected at confirmation.
- Both RPCs are SECURITY DEFINER with an empty search path. Verified grants: anon=false, authenticated=true, service_role=false for both.

### Safety and test limits

- Legacy gross-only request RPC remains blocked.
- Service-role payout preparation remains blocked; no Paystack transfer can be initiated through the existing payout function yet.
- Confirmed quote table RLS is enabled and currently has zero records.
- No creator wallet or withdrawal request was created by this work.
- Seven synthetic fee-boundary checks passed, including both sides of the ₦5,000 and ₦50,000 transfer-fee tier boundaries and the ₦10,000 stamp-duty threshold.
- Re-checked RPC privileges and function configuration: both new RPCs are SECURITY DEFINER with empty search_path; anon=false, authenticated=true, service_role=false. The old request route remains authenticated-only but rejects requests; transfer preparation remains service-role-only but rejects payout preparation.
- No authenticated browser invocation, live quote, confirmation, expiry, duplicate replay or concurrent-wallet integration test has been run.
- The fee quote uses the current configured published NGN fee bands as an estimate, not a live provider quote. Actual provider fee must still be verified from Paystack.
- Stamp-duty payer remains unresolved; any quote where stamp duty applies cannot be confirmed.
- The existing request confirmation path has not yet been connected to the creator page. No payout has been enabled.


## Batch 26 — Creator staging page connected to fee quote and confirmation

Updated `creator-withdrawal-staging.html` on the feature branch.

### Page integration

- Loads only the signed-in creator's verified, active, eligible Paystack NGN destinations through the new authenticated destination-list RPC. It displays only provider, currency and a shortened destination identifier; no bank account number or recipient code is exposed.
- Sends the gross amount and selected destination to the authenticated fee quote RPC.
- Displays the returned gross amount, estimated creator fee, net transfer, separate stamp-duty amount, fee policy version and quote expiry.
- Requires the creator to tick an explicit consent checkbox before enabling confirmation.
- Calls the confirmation RPC only after consent.
- Explains that confirmation reserves the gross amount in the staging wallet and creates a pending request, but does not send a payout.
- If stamp duty applies while payer policy remains pending, the confirmation control stays disabled and the database independently rejects confirmation.
- Refreshes the wallet and withdrawal history after successful confirmation.

### Database hardening and fee tier correction

- Corrected the fee-tier calculation so it selects the fee using the net transfer amount, including exact tier boundaries.
- Added `playam_list_creator_withdrawal_destinations_v1`, SECURITY DEFINER with empty search_path, authenticated-only. It returns only creator-owned verified eligible Paystack NGN destination metadata.
- Fee quote and confirmation RPCs remain authenticated-only; anonymous and service-role execution are false.
- Re-checked page JavaScript syntax in isolation; syntax is valid.
- Re-fetched committed page and verified it references staging only, calls the three expected RPCs, requires consent, and states no Paystack payout is sent.

### Test limits

- No signed-in browser session or real creator account was available in this execution to test end-to-end quote creation or confirmation.
- No quote or withdrawal request was created by the checks.
- No wallet reservation was executed in this batch.
- No Paystack transfer, webhook, or real payout was initiated.
- The transfer-preparation function remains deliberately blocked.
- Stamp-duty payer remains pending, so affected quotes cannot be confirmed.
- Do not enable creator withdrawals or cash rewards based on static/syntax checks alone.


## Batch 26 — Connect creator quote/consent page and harden fee-tier boundary

### Staging creator page

Connected the creator staging page to:
- `playam_list_creator_withdrawal_destinations_v1` to list only the signed-in creator's verified, eligible Paystack NGN destinations.
- `playam_create_creator_withdrawal_fee_quote_v1` to request an expiring database quote.
- `playam_confirm_creator_withdrawal_fee_quote_v1` to explicitly accept the displayed quote and create a pending staging request with gross wallet reservation.

The page shows gross withdrawal, estimated creator fee, net transfer, stamp-duty amount and quote expiry. A checkbox is required before confirmation. Quotes where stamp duty applies remain blocked while payer policy is pending. The page wording now accurately explains that eligible staging confirmations reserve funds, but no Paystack payout is sent.

### Fee-tier boundary hardening

A calculation review identified a narrow range where a net-based provider fee tier has no self-consistent estimate: gross amounts ₦5,010.01–₦5,025.00. A ₦10 fee pushes the net amount into the next fee tier, while a ₦25 fee pushes it back into the lower tier. The quote RPC now rejects that range with a clear instruction to choose a slightly lower or higher amount, rather than risk overquoting the creator.

Verified the boundary guard is present and quote RPC grants remain anon=false, authenticated=true, service_role=false.

### Verification limits

- Confirmed source wiring for all three RPCs, explicit consent, stamp-duty block and no Paystack transfer call.
- Confirmed quote function permissions and fee-tier boundary guard in staging.
- No real signed-in creator session has been used to exercise the UI end-to-end.
- No live quote or confirmation has been made; no wallet reservation or payout has occurred during this implementation.
- Browser-level accessibility, responsive layout and Supabase API runtime behaviour remain to be tested.
- Net transfer payout, Paystack webhook verification, actual fee reconciliation, fee refunds/reversals and admin payout approval remain unfinished. Existing payout preparation is still blocked.


## Batch 27 — Net payout and actual provider-fee reconciliation safeguards

### Staging Edge Functions updated

Updated deployed staging functions only:
- `paystack-creator-payout` version 2 now requires a valid gross amount, approved net transfer amount and quoted fee whose arithmetic reconciles. It sends only `net_transfer_minor` to Paystack, and records gross/net/quoted fee in the audit metadata.
- `paystack-webhook` version 7 now compares Paystack's verified transfer amount against the approved net amount, not the gross creator liability. It still validates the Paystack HMAC-SHA512 signature and verifies transfer details directly with Paystack.
- On verified transfer success, the webhook requires a valid `fee_charged` value, records the actual provider fee through the service-role-only fee recorder, and only then attempts to mark the withdrawal paid.
- Webhook verification also checks that the request's net amount and quoted fee reconcile with the gross amount and that the stamp-duty payer is not pending.

### Creator fee reconciliation and wallet credits

Replaced `playam_record_creator_withdrawal_fee_v1` on staging:
- Records verified actual Paystack fees and provider fee reversals idempotently.
- When actual fee is lower than the amount quoted to the creator, credits the difference back to the creator's available wallet using an auditable `admin_adjustment` ledger event.
- When actual fee exceeds the quote, it does not silently deduct the extra from the creator; it records a mismatch for PLAYAM finance reconciliation.
- When a provider fee is reversed, credits the reversed amount back to the creator's available wallet.
- Ledger refund entries use deterministic event idempotency keys.

### Settlement guard

Updated `playam_mark_creator_withdrawal_paid_v1` so a withdrawal cannot be marked paid unless:
- The provider reference matches the request.
- Gross, quoted fee and net transfer arithmetic reconcile.
- A verified actual provider fee has been recorded.
- Fee reconciliation is matched or mismatch (the latter means PLAYAM must absorb any excess rather than charge the creator more).
- Any applicable stamp-duty payer policy is resolved.

Verified the three service-only payout/fee RPCs are SECURITY DEFINER with execute grants restricted to service_role; anon and authenticated execution are false.

### Important limitations

- The transfer-preparation RPC remains deliberately blocked. No payout can be initiated until administrator approval, the final net-transfer preparation function and end-to-end tests are complete.
- No Paystack transfer or webhook was sent during this work.
- No withdrawal requests or fee events were created; staging request table remains empty.
- Paystack's live `fee_charged` response behaviour has not been exercised with a real provider transfer.
- The separate stamp-duty payer remains pending. Affected withdrawals remain blocked.
- The staging edge function source is deployed in the staging Supabase project. Production Supabase was not changed.


## Batch 28 — MFA-protected administrator withdrawal review

### Database

- Added `playam_admin_list_creator_withdrawals_v1()`: returns up to 100 pending, approved or processing requests only to an authenticated user with `aal2` and an active `super_admin` or `finance_admin` role.
- Hardened `playam_approve_creator_withdrawal_v1(uuid)`: before approval it now requires internally consistent fee-confirmed gross, creator fee and net transfer values. If stamp duty applies, approval is blocked until its payer is resolved.
- Existing approval policy retained: one MFA finance admin for ordinary requests; two different MFA finance admins for requests at or above the configured threshold.
- Existing rejection RPC remains MFA finance-admin restricted and releases the reserved amount through the ledger with an audit event.
- Verified list/approve/reject RPCs are SECURITY DEFINER with anon=false, authenticated=true, service_role=false.

### Administrator review page

Added `creator-withdrawal-admin-staging.html`:
- Staging Supabase project only.
- Email/password sign-in followed by verified authenticator MFA (aal2).
- Restricted queue listing.
- Displays gross, estimated creator fee, net transfer, stamp-duty policy, fee reconciliation status, destination ID and approval history.
- Requires confirmation before approval.
- Rejection requires a reason and confirmation.
- No Paystack payout or transfer action is exposed on this page.

### Verification

- Source inspection confirmed MFA flow, queue RPC, approve/reject RPCs, staging project ID, and absence of any Paystack payout call.
- Database permissions for list/approve/reject verified.
- No actual signed-in administrator session or MFA code was used; no approval or rejection was performed.
- No withdrawal records were present during the check.
- The page is a source artifact on the staging feature branch; it has not been deployed to a staging web host or tested in a browser.

### Payout safety remains

- Transfer preparation remains blocked.
- No production changes, real transfers or cash reward activation.
- Stamp-duty payer policy remains unresolved.


## Batch 29 — Read-only payout readiness preflight

Added `playam_admin_check_creator_withdrawal_readiness_v1(uuid)`, an authenticated finance-admin-only SECURITY DEFINER RPC requiring aal2 and an active finance role. It checks:
- Request is approved.
- First approval exists and is not the creator or the currently reviewing admin.
- Large withdrawal has a second approval by a different administrator.
- NGN and Paystack provider.
- Payout destination belongs to creator, is active, verified, and past the security cooldown.
- Gross amount, quoted creator fee and net transfer reconcile.
- Stamp-duty payer is resolved if stamp duty applies.
- Creator reserved wallet balance covers the gross withdrawal liability.

The RPC returns a structured blocker list and always reports `payout_enabled=false` and `transfer_initiated=false`. It performs no mutation and initiates no payout.

Added a read-only preflight action to the staging admin page. Source checks confirm MFA, queue, approve/reject, preflight RPC wiring, staging project ID and no Paystack payout call.

No withdrawal request or fee event was created. No administrator session was used. Browser runtime and actual MFA review remain untested. The transfer-preparation RPC remains blocked; no payout was initiated.


## Batch 30 — Stale payout recovery queue and duplicate-transfer safeguards

### Stale request queue

Added `playam_admin_list_stale_creator_withdrawals_v1(integer)`:
- Requires authenticated finance administrator with aal2 and active role.
- Lists only requests still in `processing` older than a caller-specified 1 minute to 7 day threshold (admin page uses 10 minutes).
- Shows existing provider reference, request age, gross/net/fee and approval history.
- Read-only; it does not retry, mark failed, release funds or initiate another transfer.

### Admin page

Added a stale transfer reconciliation panel:
- Lists processing requests older than 10 minutes.
- Displays the exact existing Paystack reference and a copy-reference action.
- Explicitly instructs administrators to verify that same reference with Paystack and never create a new reference when provider outcome is uncertain.
- Unknown outcomes remain reserved and require manual review.

### Verification

- Confirmed the RPC is SECURITY DEFINER with execute grants: anon=false, authenticated=true, service_role=false.
- Source checks confirm the page calls the stale queue, keeps MFA checks, includes readiness preflight and does not call the payout Edge Function.
- Existing payout Edge Function uses the saved deterministic transfer reference and deliberately does not automatically retry after network timeout or unreadable response.
- Existing failure webhook verifies transfer status with Paystack before releasing the gross reservation; duplicate failure notifications are a no-op after the first failure.
- No staging withdrawal records were available for real queue testing. No Paystack transfer, retry, failure release or reversal was executed.

### Remaining recovery gaps

- A provider transfer reversal is currently recorded for manual review only; it does not automatically recreate a creator liability or claw back a previously withdrawn wallet amount. This is intentional until a fully audited reversal ledger workflow is designed and tested.
- A successful provider transfer whose webhook is delayed remains in processing/reserved until the signed webhook or manual reconciliation resolves it.
- The current payout-preparation RPC remains deliberately blocked. The preflight and stale queue are administrative diagnostics, not permission to pay.
- No browser session, live Paystack sandbox transfer or end-to-end duplicate webhook test was performed.
- No production changes.


## Batch 31 — Paystack transfer reversal liability accounting

### Database

- Added private `playam_creator_withdrawal_reversals` table, service-role-only, with unique provider/reference and idempotency constraints.
- A reversal record links to the original paid withdrawal, creator, exact Paystack reference, verified reversed net amount, optional provider fee, and recovery status.
- Replaced the reversal recorder so it accepts only a previously paid NGN Paystack withdrawal and requires the verified reversed amount to equal the original net transfer amount.
- Duplicate reversal events for the same Paystack reference resolve to the existing record; conflicting request/amount data is rejected.
- Added MFA finance-admin-only reversal queue RPC. It lists outstanding recovery liabilities without changing creator balances.

### Paystack webhook

- Deployed staging `paystack-webhook` version 8.
- On `transfer.reversed`, it still verifies the transfer directly with Paystack and requires provider status `reversed`.
- It passes the verified transfer amount and optional provider fee into the service-role-only reversal recorder.
- The webhook records the reversal liability and returns the record status; it does not debit the creator wallet or automatically net the reversal against future earnings.

### Administrator page

- Added a reversal recovery queue to `creator-withdrawal-admin-staging.html`.
- Queue is protected by the existing authenticator MFA and finance-role gate.
- Shows creator, original withdrawal, Paystack reference, reversed amount, fee when supplied and recovery status.
- Explicitly warns that this view does not debit creator funds, freeze accounts, write off amounts or offset future earnings.

### Verification and limitations

- Source checks confirm webhook version 8 verifies reversed provider status and calls the reversal recorder with the verified net amount.
- Admin page source check confirms MFA remains in place and reversal queue is connected.
- Reversal table currently contains zero records; no synthetic or real financial records were inserted.
- No Paystack transfer or reversal was executed.
- No actual signed-in MFA admin session or browser runtime test was performed.
- Creator recovery, write-off, future-earnings offset and accounting treatment remain deliberately unimplemented pending an explicit fair recovery policy and legal/accounting review.
- All changes are staging project/feature-branch only; production untouched.


## Batch 32 — Reversal recovery ledger audit (read-only)

Audited the staging reversal table, transaction constraints, wallet trigger and administrator reversal queue before designing any recovery mutation.

### Confirmed database facts

- The private playam_creator_withdrawal_reversals table stores provider/reference, linked paid withdrawal, creator, exact reversed net amount, optional provider fee, idempotency key, status and review metadata.
- The table enforces unique provider/reference and unique idempotency key. Allowed statuses are recovery_required, under_review, recovered and written_off.
- The reversal recorder accepts only a previously paid NGN Paystack withdrawal with the exact original net transfer amount. It records a liability and does not debit the creator wallet.
- The MFA finance-admin queue returns only recovery_required and under_review items.
- The creator wallet trigger permits admin_adjustment entries to change available balance, including negative adjustments if the resulting available balance remains nonnegative. A future recovery debit must never be implemented as an ordinary admin adjustment without additional strict guards and explicit policy.
- The existing withdrawal_reversal transaction type is deliberately rejected by the wallet trigger as a legacy event; it must not be assumed to be a safe recovery ledger path.
- Current staging reversal count is zero.

### Decision: no automatic recovery debit or write-off

No recovery mutation was applied in this batch. The current schema has only one reviewer field on reversal records, which is not enough by itself to prove independent two-person write-off approval. The creator-recovery policy also has not been approved.

Before implementing any wallet recovery, PLAYAM needs an explicit policy covering:
1. Whether the reversal was caused by provider/bank error, recipient bank rejection, fraud, or another cause.
2. Whether the creator actually received and retained the original transfer.
3. Whether recovery is legally and contractually permitted.
4. Whether recovery can be limited to future available earnings, with no negative wallet balance and no access to pending earnings.
5. A notice and dispute window for the creator.
6. Independent two-person approval for any write-off or recovery adjustment.
7. A complete evidence trail and idempotent accounting entries.

### Verification limits

- Read-only SQL inspection only; no database schema or records changed in this batch.
- No creator wallet balance changed.
- No real or test Paystack transfer or reversal occurred.
- No browser/MFA admin session was exercised.
- No production project or Friendship Court code was touched.

### Next safe milestone

Add an auditable recovery decision workflow only after the recovery policy is approved. Until then, reversal records remain outstanding finance-review liabilities; do not debit creators, offset future earnings, freeze accounts, or write off balances automatically.
