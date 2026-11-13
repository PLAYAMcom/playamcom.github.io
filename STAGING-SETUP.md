# PLAYAM — Supabase staging setup

## Purpose
Create a completely separate Supabase project for integration testing the Report Player feature. The production project and live website must remain untouched.

## 1. Create the staging project
In the Supabase dashboard:
1. Create a new project named `PLAYAM-staging`.
2. Use a separate database password and keep it in a password manager.
3. Do not clone production player records or copy real personal data. Use synthetic test accounts and room data only.
4. Record the staging Project URL and anon/publishable key for the staging frontend configuration.
5. Keep the service-role/secret key private. Never put it in HTML, JavaScript, GitHub commits, or a browser.

## 2. Keep configuration separate
- Production site configuration must continue pointing to production.
- The staging test page must use only the staging project URL and anon/publishable key.
- Store any server-side test credentials only in GitHub Actions secrets or a secure server environment, never in repository files.
- Do not replace production credentials in `index.html`.

## 3. Apply the database schema safely
Apply the required schema and functions to staging only:
- `player_reports` table and its constraints/indexes
- `list_room_report_targets(p_room_id uuid)`
- `submit_player_report(p_reported_auth_user_id uuid, p_reason text, p_details text, p_room_id uuid)`
- Admin list/review RPCs and their private audit table
- The required RLS policies and grants

Use the SQL already reviewed in the development conversation as the source. Before running it, verify that the SQL editor is connected to the staging project by checking the project name and project reference. Do not run it in production as part of this staging exercise.

## 4. Create synthetic test identities
Create two ordinary authenticated test users and one separate admin test user. Use test-only email addresses you control. Create one test room and join both ordinary users to it. Grant admin status only to the dedicated admin test account using the existing approved admin mechanism.

## 5. Integration test matrix
| Test | Expected result |
|---|---|
| Player A loads room targets | Player B appears |
| Player A loads room targets | Player A is excluded |
| Player A reports Player B | One open report is created |
| Player A reports self using direct RPC | Rejected |
| Player A reports someone outside the room | Rejected |
| Anonymous user submits report | Rejected |
| Sixth report within one hour | Rejected by rate limit |
| Ordinary user calls admin list/review RPC | Rejected |
| Admin lists open reports | Test report appears |
| Admin reviews report | Allowed status transition and audit entry |
| Double-click submit | At most one report is created |

Also verify that a report cannot be read by an ordinary player through direct table access.

## 6. Evidence and release gate
Record test results without including passwords, access tokens, or personal data. Keep the feature PR in draft until all integration tests pass and the code review is complete. Do not merge or deploy this feature as part of staging setup.

## Current status
- Offline GitHub static checks: passing on the earlier run.
- Isolated mock test page: committed to the feature branch.
- Real Supabase staging integration: not yet run.
- Production: unchanged; no test reports submitted.
