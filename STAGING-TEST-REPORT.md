# PLAYAM Staging Test Report

**Date:** 2026-11-16  
**Target branch:** `codex/playam-staging-mobile`  
**Test page:** `staging-game.html`  
**Purpose:** Pre-deployment source-readiness and two-player mobile test record.

## Scope and safety
- This report covers the isolated staging gameplay page only.
- The page is configured for the PLAYAM staging Supabase project.
- The production Supabase project URL is absent from the staging page.
- No production deployment, merge to `main`, database migration, or production data change was performed.
- Vercel is not yet connected in this ChatGPT session, so no hosted preview has been deployed.

## Automated source checks

| Check | Result |
|---|---|
| Staging Supabase URL present | PASS |
| Production Supabase URL absent | PASS |
| Visible staging-only warning | PASS |
| Portrait responsive rules | PASS |
| Narrow-screen responsive rules | PASS |
| Landscape responsive rules | PASS |
| Safe-area handling | PASS |
| Reduced-motion handling | PASS |
| Room session storage key present | PASS |
| Server-side room membership validation on restore | PASS |
| Ready RPC includes room code | PASS |
| Start-game RPC includes room code | PASS |
| Submit-answer RPC includes room code | PASS |

**Source checks: 13/13 PASS.**

These are source/configuration checks, not proof that the page renders or gameplay works in a real browser.

## Runtime and two-player tests

Status for all items below: **NOT RUN — hosted staging preview is not yet available.**

- [ ] Open preview on two separate devices/browser sessions.
- [ ] Sign in with staging test account A and account B.
- [ ] Account A creates a Friendship Court room.
- [ ] Account B joins using the room code.
- [ ] Both players appear in the lobby.
- [ ] Both players can toggle ready state.
- [ ] Host starts the game.
- [ ] Questions and timer display correctly.
- [ ] Both players submit answers.
- [ ] Voting/results flow completes correctly.
- [ ] Refresh/reopen restores only a server-verified room membership.
- [ ] Test portrait, landscape, and narrow-screen layouts.
- [ ] Confirm no production URL, data, or account is used.

## Known limitations
- Browser-level visual testing has not been performed.
- Real two-player gameplay has not been exercised.
- Staging question-bank completeness and end-to-end persistence must be verified during runtime testing.
- No conclusion that PLAYAM is ready for public launch should be drawn from the source checks alone.

## Next gate
Connect Vercel, deploy only `codex/playam-staging-mobile` as a separate staging preview, verify the deployed page still targets staging, then execute the runtime checklist with the two staging test accounts. Do not merge or deploy to production as part of this test.


## Batch 42 — Full-height portrait-first mobile navigation pass

Updated `staging-game.html` on `codex/playam-staging-mobile` and `www/index.html` on `codex/playam-mobile-app`.

### Layout changes
- On narrow portrait screens, the existing navigation becomes a fixed bottom dock spanning the full screen width.
- The brand/side-label clutter is hidden in the dock while existing navigation actions remain available and horizontally scrollable.
- The main content receives bottom clearance so the dock and iPhone safe-area inset do not cover gameplay controls.
- Dock sizing and content spacing adapt to short landscape screens.
- Existing game screens, Supabase staging configuration, and Friendship Court interaction code were not intentionally changed.

### Source checks
- Both updated files retain only the staging Supabase URL; no production Supabase URL is present.
- The full-height portrait CSS marker appears once in each file.
- Safe-area insets are included for the fixed dock and content clearance.
- Narrow-screen and landscape rules are present.
- This is a CSS/source-level pass only. No browser screenshot, device visual test, two-player runtime test, Android install test or iOS build test was performed.

### Deployment status
Source changes are committed to the two separate feature branches only. No production deployment or merge was performed. The Vercel staging preview still requires browser/device verification before calling this update complete.


## Batch 43 — Full-height portrait navigation source correction

Applied the portrait-first CSS pass to `staging-game.html` in this branch and `www/index.html` in `codex/playam-mobile-app`.

### Source verification
- Both files contain the expected full-height portrait CSS marker exactly once.
- Both contain the staging Supabase project URL and neither contains the production Supabase project URL.
- Both include safe-area bottom padding and a fixed full-width bottom navigation treatment.
- Both include narrow-screen and short-landscape adjustments.

### Preview deployment
- Created a Vercel deployment in the dedicated `playam-mobile-staging` project with target `staging`.
- Deployment ID: `dpl_EFXprQmaKssQBcNxn76BedeXGhpu`.
- Source branch: `codex/playam-mobile-app`.
- Source commit: `219612db43ff272864d05c6410afa91368ffbce0`.
- Last observed state during this report update: `BUILDING`. A READY state and browser/device rendering have not yet been verified.
- Project SSO protection is enabled, so preview access may require authorised team sign-in.

### Scope
No production deployment, merge, Supabase migration, payout, or Friendship Court gameplay logic change was made. This is a source-level mobile layout update pending actual browser/device testing.
