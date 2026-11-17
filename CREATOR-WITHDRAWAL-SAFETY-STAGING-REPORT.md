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
- No authenticated browser invocation, live quote, confirmation, expiry, duplicate replay or concurrent-wallet integration test has been run.
- The fee quote uses the current configured published NGN fee bands as an estimate, not a live provider quote. Actual provider fee must still be verified from Paystack.
- Stamp-duty payer remains unresolved; any quote where stamp duty applies cannot be confirmed.
- The existing request confirmation path has not yet been connected to the creator page. No payout has been enabled.
