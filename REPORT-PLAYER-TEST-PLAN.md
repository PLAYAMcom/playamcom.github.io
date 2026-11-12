# Report Player test plan

## Safe automated checks
The GitHub Actions workflow runs offline checks against the pull request. It checks required Report Player UI/RPC wiring and parses inline JavaScript with Node.js. It does not contact Supabase, create reports, or change production data.

## Required staging integration test
Do not run the following against the production Supabase project.

1. Create or select a separate Supabase staging project.
2. Apply the report-table/RPC SQL and the admin moderation functions to staging.
3. Configure a staging-only copy of the frontend with the staging project URL and anon key. Never place a service-role key in browser code.
4. Create two test accounts and one test room. Join both accounts to the same room.
5. As player A, open Report Player. Confirm player A is not selectable and player B is selectable.
6. Submit one test report as player A against player B. Confirm one row appears in the staging `player_reports` table.
7. Attempt self-reporting, reporting a player outside the room, anonymous submission, and a sixth report inside one hour. Confirm each is rejected server-side.
8. Sign in as an authorised admin. Confirm the report appears, can move through the permitted statuses, and the decision is written to the admin audit log.
9. Confirm an ordinary authenticated account cannot call either admin RPC.
10. Repeat a successful submission and verify the UI prevents duplicate clicks.

## Release gate
Keep PR #1 in draft and do not merge until the staging integration checks pass. No production report data should be used for testing.
