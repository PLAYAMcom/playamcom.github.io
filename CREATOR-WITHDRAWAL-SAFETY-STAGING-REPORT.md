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


## Batch 33 — MFA-protected withdrawal audit reader

### Staging database

- Added `playam_admin_list_creator_withdrawal_audit_v1(uuid)`, a read-only audit-list RPC. It requires a signed-in user with `aal2` and an active `super_admin` or `finance_admin` role, optionally filters to one withdrawal request, and returns at most 200 newest events.
- Execute privileges verified: `anon=false`, `authenticated=true`, `service_role=false`. The function independently enforces MFA and active finance role before returning rows.
- The existing `playam_creator_withdrawal_audit` table has RLS enabled, zero direct rows visible in this check, and a trigger preventing UPDATE/DELETE. Existing request lifecycle functions write audit events transactionally for approval, rejection, cancellation, processing, paid/failure and reversal events.

### Staging administrator page

- Added a read-only audit trail panel to `creator-withdrawal-admin-staging.html`, showing event type, request ID, actor, timestamp and event metadata.
- Panel loads after the existing sign-in/MFA gate and refreshes with the admin queue. It has no edit/delete controls and no payout action.
- Updated page is committed on `codex/playam-creator-withdrawal-safety`; no production deploy was performed.

### Verification limits and advisor findings

- Verified RPC privileges and inspected the audit table immutability trigger and existing audit writes.
- No signed-in MFA browser session was used; the page's live rendering and event retrieval have not been end-to-end tested. The audit table currently has zero rows, so there are no historical events to display.
- Supabase security advisors report 37 RLS-enabled tables with no policies (including finance/withdrawal tables that are intended to be inaccessible directly) and 63 authenticated-executable SECURITY DEFINER functions across the project. These findings require object-by-object review: some are intentionally RPC-gated and some are unrelated legacy/game functions. Do not mass-change grants or policies because that could break PLAYAM/Friendship Court. The advisor also reports leaked-password protection disabled; this should be enabled after reviewing auth compatibility.
- Performance advisors report unindexed foreign keys, including several new withdrawal/reversal foreign keys. Add targeted indexes after confirming query paths; do not remove unused indexes based on a low-traffic staging snapshot.
- Health advisors returned no findings.

### No activation

No creator wallet changes, payout, cash reward activation, production database change, or Friendship Court/gameplay change occurred.


## Batch 34 — Paystack workflow consistency review (read-only)

Inspected the deployed staging Edge Function source for `paystack-creator-payout` and `paystack-webhook`, plus the fee quote/confirmation and reversal RPC definitions.

### Confirmed safeguards

- The payout Edge Function requires a service-role bearer token and validates a withdrawal request ID.
- It calls the database preparation RPC before contacting Paystack. The preparation RPC currently always raises a staging-disabled exception, so the Edge Function returns 409 and no transfer is initiated.
- If preparation is ever enabled, the Edge Function checks NGN, gross/net/quoted-fee arithmetic, recipient code and unresolved stamp-duty payer before calling Paystack. Network/ambiguous provider responses leave the deterministic reference for manual reconciliation; they do not trigger an automatic second transfer.
- The webhook verifies Paystack's HMAC-SHA512 signature, fetches transfer verification from Paystack, checks reference, amount and currency, records actual transfer fee, and only then calls the paid/failure settlement functions.
- The transfer-reversal webhook path calls the five-argument reversal recorder with the verified reversed amount. That function only accepts a previously paid withdrawal and exact original net transfer amount; it records a recovery-review liability and does not debit the creator wallet.
- The fee quote confirmation RPC is owner-scoped, locks the quote and destination, enforces a ten-minute expiry and explicit confirmation, checks available funds, and reserves the gross amount only after confirmation. If stamp duty applies and payer remains pending, confirmation is blocked.

### Important unresolved fee-quote boundary

The quote RPC's current fee-tier calculation says it selects the Paystack fee tier using the net transfer amount, but its boundary handling is incomplete around the ₦50,000 threshold. It blocks one ambiguous band around ₦5,010–₦5,025 gross, but does not similarly handle the next boundary around ₦50,025–₦50,050 gross. For amounts in that latter band, the calculated quoted fee can be inconsistent with the tier implied by the resulting net transfer amount. Do not rely on this quote calculation for real creator payouts until the fee-tier basis and boundary treatment are verified against current Paystack documentation and corrected with tests on both sides of every threshold.

### Remaining integration blockers

- Stamp-duty payer policy is still `pending_policy`; any quote where stamp duty applies is blocked at confirmation and payout readiness.
- The actual transfer-preparation RPC is deliberately disabled, so no live or sandbox payout can be initiated through this path.
- The quote RPC can reserve gross funds after confirmation, but the creator-facing quote/confirmation experience and end-to-end wallet reconciliation have not been exercised with signed-in test accounts.
- The webhook's successful-transfer path accepts a verified fee mismatch as a reconciliation state; finance must review any mismatch and the policy that PLAYAM absorbs any amount above the creator's disclosed quote before enabling payouts.
- No signed webhook test, provider sandbox transfer, ambiguous-response recovery drill, or actual MFA creator/admin browser test was performed in this audit.

### Outcome

Read-only inspection only. No Edge Function was changed or deployed, no database records were inserted, no creator wallet changed, no Paystack transfer was attempted, and no production/Friendship Court changes occurred. Payouts remain disabled in staging.


## Batch 35 — Corrected Paystack fee quote boundaries (staging database only)

Applied migration `correct_creator_withdrawal_fee_quote_tier_boundaries` to staging project `pwnjrdedeoxbmtfywhkk` only. Replaced `playam_create_creator_withdrawal_fee_quote_v1` while preserving its authenticated-only execution model and the existing owner/destination/balance/expiry/idempotency checks.

### Fee calculation now

The calculation is based on the net transfer amount, matching Paystack's published NGN transfer fee bands: ₦10 for transfers up to ₦5,000; ₦25 for transfers above ₦5,000 through ₦50,000; and ₦50 above ₦50,000. The quote function now blocks both gross-amount intervals where no self-consistent net amount and fee tier exist:

- ₦5,010.01–₦5,025.00 gross, around the ₦5,000 net-transfer threshold.
- ₦50,025.01–₦50,050.00 gross, around the ₦50,000 net-transfer threshold.

It also rejects net transfers below Paystack's published ₦50 minimum. Stamp duty remains a separate ₦50 government charge for qualifying transfers at or above ₦10,000; its payer remains `pending_policy`, and confirmation continues to block where stamp duty applies.

### Verification performed

- A 12-point synthetic SQL boundary check covered both sides of both fee thresholds, both blocked intervals, the minimum transfer amount, and a higher amount. All 8 quoteable samples matched the fee tier implied by their calculated net transfer; all 4 samples inside the two ambiguous intervals were blocked.
- Function privileges checked: `anon` cannot execute; `authenticated` can execute; `service_role` cannot execute.
- Migration applied successfully.
- No actual authenticated creator quote was created, because no signed-in creator test session was used. This was a logic/boundary check, not an end-to-end RPC test.

### Advisor snapshot

Supabase security advisor still reports 38 RLS-enabled tables without policies and 63 authenticated-callable SECURITY DEFINER functions across the wider staging project. These are existing project-wide findings requiring object-by-object review; no blanket policy or permission changes were made. Performance advisor returned no lints in this check. Health advisor returned no findings.

### Outcome and remaining blocks

No creator wallet or financial rows were changed; no Paystack API call or transfer was made. Payout preparation remains disabled. Stamp-duty payer policy, provider-fee mismatch handling review, authenticated creator/admin browser tests, signed webhook tests, and sandbox transfer/reconciliation drills remain outstanding. Production and Friendship Court were not changed.


## Batch 36 — Fee mismatch and provider fee-reversal accounting (staging database only)

Applied migration `reconcile_creator_fee_overquote_and_reversals` to staging project `pwnjrdedeoxbmtfywhkk` only.

### What changed

- Added private service-role-only table `playam_creator_withdrawal_fee_cost_events` to separately record the portion of a verified Paystack fee above the creator's accepted quote as a PLAYAM platform expense, and later provider reversals of that absorbed overage. It is linked to the immutable fee event and withdrawal request, with unique event and idempotency keys.
- Added a database trigger that creates the overquote expense record when a verified provider fee exceeds the creator quote, and offsets that expense first when Paystack later reverses fees.
- Corrected creator fee reversal accounting. A provider fee reversal now offsets PLAYAM's previously absorbed overquote first. Only the portion that reduces the creator's effective fee below the amount they agreed to pay is returned to the creator's available earnings. This prevents refunding the creator for a fee amount they never bore.
- Kept the creator fee refund through the existing idempotent ledger transaction and retained the service-role-only fee recorder.

### Synthetic arithmetic checks

Four scenarios were checked without inserting wallet or financial records:

- Provider fee above quote: reversal first offsets PLAYAM's absorbed overage; creator receives only the excess after the fee falls below their quote.
- Subsequent partial reversal: only the incremental creator share is refunded.
- Provider fee below quote: the original quote difference is refunded, and later provider reversals only refund any additional creator-paid portion.
- Multiple reversals: incremental refunds do not duplicate prior refunds.

The arithmetic checks returned the expected incremental refund amounts for the four constructed scenarios. These are logic checks, not transactional end-to-end tests.

### Access checks

- New cost table has RLS enabled.
- `anon` and `authenticated` have no SELECT access.
- `service_role` has SELECT/INSERT access.
- Fee recorder execute: `anon=false`, `authenticated=false`, `service_role=true`.

### Remaining limitations

- The new cost subledger is not yet included in the finance dashboard's consolidated operating-expense summary; it is separately recorded and must be reconciled into that summary before PLAYAM treats dashboard net operating results as complete.
- No actual fee event, creator wallet refund, Paystack sandbox transfer, signed webhook, or browser MFA test was executed. No wallet/financial data rows were created by these checks.
- Payout preparation remains disabled. Stamp-duty payer policy remains pending. Production and Friendship Court remain unchanged.


## Batch 37 — Withdrawal fee costs integrated into finance reporting

Applied staging migration `include_withdrawal_fee_cost_events_in_financial_summary` to project `pwnjrdedeoxbmtfywhkk`. The MFA-protected `playam_get_financial_summary_v1(p_from,p_to)` now combines ordinary append-only financial entries with the private creator withdrawal fee-cost subledger. It includes verified overquote expense events and subtracts later provider-fee reversals in the period in which each event is recorded. The combined totals remain currency-separated and category breakdown includes `creator_withdrawal_fees`.

Updated `finance-admin-staging.html` on branch `codex/playam-creator-withdrawal-safety` to show the net creator-withdrawal fee overquote cost within each currency's management overview, calculated from the financial summary category breakdown. The dashboard still describes results as recorded operating results, not audited profit.

Verification: migration succeeded; function definition re-read; execute privileges verified (`anon=false`, `authenticated=true`, with MFA and finance-role checks enforced inside the function). Dashboard change committed. No actual fee events or ledger records were created, so there is no real expense amount to report yet. No signed-in MFA browser run or rendered dashboard test was performed.

Remaining accounting caution: finance administrators must not manually duplicate the same Paystack overquote expense in `playam_financial_entries`; the automatic fee-cost subledger is now included in the financial summary. Other provider transfer fees at or below the creator's accepted quote are not automatically booked as PLAYAM expense under this specific subledger. Stamp duty payer remains pending policy. Creator payouts remain disabled. No production or Friendship Court changes.


## Batch 38 — Creator wallet ledger lifecycle audit (read-only)

Reviewed the staging wallet trigger, fee-quote confirmation RPC, creator cancellation, administrator rejection/approval, payout failure/success settlement, fee refunds/reversals, table grants, and RLS on project `pwnjrdedeoxbmtfywhkk`.

### Lifecycle findings

- Fee quote confirmation locks the creator-owned quote and eligible destination, locks the NGN wallet row, checks available funds, creates the pending withdrawal request, writes a gross-amount reserve ledger entry, and marks the quote accepted in the same transaction. The trigger moves gross amount from available to reserved.
- Creator cancellation is restricted to the request owner, pending status, and before first administrator approval. It marks the request cancelled and releases the exact gross reserve.
- Administrator rejection requires aal2 and an active finance/super-admin role, a different actor from the creator, and a pending/approved request. It marks the request rejected and releases the exact gross reserve.
- Verified payout failure changes processing to failed and releases the gross reserve. Repeated failure webhook delivery is a no-op once failed.
- Verified payout success checks the request/provider reference, fee quote arithmetic, actual fee reconciliation and stamp-duty policy, then moves the gross reserve to withdrawn. The Paystack transfer itself is intended to be the net amount; creator bears only the accepted fee while PLAYAM absorbs any provider overquote recorded separately.
- A lower-than-quoted verified provider fee refunds the difference through an idempotent ledger adjustment. Provider fee reversals refund only the incremental portion the creator actually bore, after first offsetting any PLAYAM-absorbed overquote.
- Legacy generic withdrawal and withdrawal-reversal transaction types are rejected by the wallet trigger.

### Access findings

- Wallet balances and withdrawal requests: RLS enabled; authenticated users can read but cannot insert; anonymous users cannot read or insert.
- Earnings transaction ledger: RLS enabled; authenticated and anonymous users cannot read or insert; service role can read/insert.
- Balance changes occur through the security-definer ledger trigger; wallet and ledger are not directly writable by ordinary clients.

### Issues / limitations

- The wallet trigger's `admin_adjustment` branch permits positive or negative available-balance changes, provided the resulting available balance is nonnegative. Direct client inserts are denied by table grants/RLS, but this remains a powerful trusted-backend primitive. Future reversal recovery must not call it without a dedicated policy-enforcing function, strong authorization, dual-control review, evidence, and idempotency.
- The wallet table has a single wallet row per creator and a currency field; all current withdrawal logic explicitly selects NGN. Multi-currency expansion needs a deliberate composite-key migration rather than assuming the current structure supports it.
- No real signed-in creator/admin account lifecycle test was run. No synthetic wallet rows or financial ledger entries were inserted for this audit. This was source/permission review, not end-to-end balance proof.
- Request creation through the legacy withdrawal RPC remains blocked; fee-confirmation is the intended route. Payout preparation remains blocked. No Paystack transfer or webhook was triggered.

### Outcome

Read-only audit only. No database schema, wallet balances, ledger rows, Edge Functions, production resources, or Friendship Court code changed in this batch.



## Batch 39 — Withdrawal integration permissions and webhook coverage audit (read-only)

Reviewed the current staging Supabase project `pwnjrdedeoxbmtfywhkk`, deployed Edge Function source, withdrawal RPC definitions and Git feature-branch report.

### Verified staging Edge Function state

- `paystack-creator-payout` is deployed and active (version 2). It calls `playam_prepare_creator_withdrawal_transfer_v1` before contacting Paystack, validates NGN gross/net/fee arithmetic, and sends the net amount only if the preparation RPC returns one valid prepared transfer.
- The database preparation RPC still unconditionally raises the staging-disabled exception. Therefore the active Edge Function cannot reach the Paystack transfer request through the current database path; it returns a not-ready response and no transfer is initiated.
- `paystack-webhook` is deployed and active (version 8). It validates the HMAC-SHA512 signature, verifies transfer details directly with Paystack, checks the approved net amount/reference/currency, records the actual transfer fee, and then invokes the paid settlement RPC. Failure handling verifies the provider's failed status before releasing the gross reserve.
- For `transfer.reversed`, the webhook calls the five-argument transfer-reversal recorder. That recorder creates a recovery-review liability only; it does not debit the creator wallet.
- The webhook's normal success path calls the provider-fee-verified recorder. The deployed webhook source does not call the provider-fee-reversed event path. Automatic ingestion of a separate provider fee-reversal event is therefore not demonstrated and needs a defined provider event/reconciliation source before it can be claimed as automated.

### Fee and reversal accounting observations

- The fee quote function currently blocks both no-solution fee-tier transition intervals and keeps stamp duty separate with payer `pending_policy`.
- The fee recorder records verified actual fee, refunds a lower-than-quoted fee difference to the creator, records a platform overquote expense through the fee-cost trigger, and supports separately recorded provider-fee reversals.
- The transfer-reversal queue and recorder are present, but no recovery-resolution/write-off mutation is implemented or approved.
- The creator wallet trigger still permits trusted `admin_adjustment` entries to affect available balance. This is not an acceptable general-purpose reversal recovery mechanism without a dedicated policy-enforcing workflow.

### Exact permission checks

- Quote creation and quote confirmation: `anon=false`, `authenticated=true`, `service_role=false`; both are owner-scoped SECURITY DEFINER RPCs with empty search_path.
- Transfer preparation and fee recording: `anon=false`, `authenticated=false`, `service_role=true`.
- Both transfer-reversal recorder overloads: `anon=false`, `authenticated=false`, `service_role=true`.
- Administrator reversal and audit readers: `anon=false`, `authenticated=true`, `service_role=false`; each reader independently checks aal2 and active finance/super-admin role.
- Withdrawal quote, fee-event, fee-cost, reversal and audit tables all have RLS enabled; direct SELECT is denied to anon and authenticated roles and available to service_role.
- Current row counts are zero for fee quotes, fee events, platform fee-cost events, transfer reversals and withdrawal audit events. Thus no real or synthetic transaction data has been used to prove end-to-end reconciliation.

### Current Supabase advisor snapshot

- Security: 39 RLS-enabled tables without policies (INFO), 63 authenticated-callable SECURITY DEFINER functions (WARN), and leaked-password protection disabled (WARN).
- Performance: 25 unindexed foreign keys (INFO) and 103 unused indexes (INFO). The unused-index list must not trigger blanket index deletion on a low-traffic staging project.
- Health: no findings.
- These are project-wide findings. The 39 no-policy tables include intentionally direct-inaccessible finance tables; the 63 SECURITY DEFINER functions require object-by-object review. No broad permission changes were made.

### Remaining blockers confirmed

1. Stamp-duty payer policy is still unresolved. Affected quote confirmations and payout readiness remain blocked.
2. Transfer preparation is still disabled in staging. No Paystack sandbox or live transfer can proceed through the current database path.
3. Separate provider fee-reversal ingestion is not wired in the deployed webhook source.
4. Transfer reversal recovery policy and dual-control resolution workflow remain unapproved/unimplemented.
5. Signed-in creator quote/confirmation, two-admin MFA, signed webhook and provider sandbox tests remain outstanding.
6. No real bank/provider statement has been reconciled; dashboard results cannot yet be treated as audited profit or verified available cash.

### Outcome

Read-only inspection and permission/advisor checks only. No database migration, Edge Function deployment, GitHub application code change, withdrawal quote, wallet ledger entry, reversal record or financial event was created. No Paystack transfer was attempted. Production and Friendship Court remain untouched; creator cash rewards and payouts remain disabled.
