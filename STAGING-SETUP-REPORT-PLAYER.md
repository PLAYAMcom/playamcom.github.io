# PLAYAM Report Player — staging environment setup

## Safety boundary
The production frontend contains the production Supabase project configuration. Do not use it for integration tests. Do not submit test reports on the live site. Do not copy production player accounts, report records, auth users, service-role keys, or other private data into staging.

## 1. Create a separate Supabase project
In the Supabase dashboard, create a new project named `PLAYAM-Staging` (or another clearly labelled staging name) in the appropriate region. Use a new database password and store it in a password manager. Confirm the project ref and URL clearly identify staging before running any SQL.

If the organisation already has a Supabase staging project, verify its project ref and that it is not production before using it.

## 2. Prepare the staging database
Use the Supabase migration workflow or SQL editor connected only to the staging project.

- Apply the schema and prerequisites needed by the Report Player feature.
- Apply the `player_reports` table and its indexes/policies.
- Apply `list_room_report_targets` and `submit_player_report`.
- Apply the admin report-list and review functions, including the admin audit table and admin-role checks.
- Ensure function privileges allow authenticated users where intended and deny anonymous users; admin functions must additionally enforce active-admin authorization.
- Do not run guessed or partial SQL. Use the exact reviewed migrations from the project and inspect dependencies first.

## 3. Configure staging authentication
Enable the same sign-in method(s) needed for testing. Create two dedicated test users (Player A and Player B) and a separate staging admin account. Use test-only email addresses and passwords. Do not reuse real users' credentials.

Create a test room and join both player accounts. Confirm the `players.auth_user_id` mapping is populated for both users.

## 4. Point a staging-only frontend at staging
Create a staging-only frontend configuration. Use the staging Supabase project URL and its public anon/publishable key only. Never put a service-role key in browser code or commit secrets to GitHub.

Before loading the staging page, inspect the configured project URL and project ref and confirm they match the staging dashboard. The production `index.html` must remain unchanged by this configuration work.

## 5. Integration test cases
1. Player A can open the report form and sees Player B as an eligible target.
2. Player A cannot select or report themselves.
3. Player A can submit a valid report and exactly one staging row is created.
4. Missing target, missing reason, invalid reason, oversized details, unauthenticated submission, non-room target and self-report are rejected.
5. The per-user hourly limit is enforced server-side.
6. Player B cannot read another user's private report or call admin-only functions.
7. An authorised staging admin can list the report, move it through allowed statuses, and produce an audit record.
8. An ordinary account cannot list or review reports.
9. Double-click/repeated submit does not create duplicate reports.
10. Realtime/UI refresh does not leak report details to other players.

Record each test result, the staging project ref (not secrets), and any failing SQL/RPC response. Remove test accounts and test records after the test is signed off.

## 6. Release gate
Keep PR #1 as draft and unmerged until all staging integration tests pass and the code review is complete. Only then prepare a separate production release and explicitly review its deployment impact.
