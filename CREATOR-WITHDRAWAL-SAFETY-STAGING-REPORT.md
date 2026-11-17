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
