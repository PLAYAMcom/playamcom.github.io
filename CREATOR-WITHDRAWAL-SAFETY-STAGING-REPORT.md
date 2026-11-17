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
- The quote table/RPC, explicit creator consent, net payout amount, actual provider-fee webhook reconciliation and wallet adjustment/refund logic are not yet implemented.
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
