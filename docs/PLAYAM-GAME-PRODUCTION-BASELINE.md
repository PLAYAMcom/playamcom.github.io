# PLAYAM Game Production Baseline

Status: approved product direction; planning baseline, not a claim that these games are implemented.

## Non-negotiable quality bar
- Each game runs in an isolated screen/session. Opening a game must pause or close the previous game cleanly; no shared timers, input handlers, audio loops, canvases, or state.
- Every game needs a complete playable loop: entry/menu, mode selection, instructions, matchmaking or local setup, gameplay, pause/resume, results, rematch/exit, settings, and error/connection states.
- Controls must work on touch devices and adapt to screen size. Audio and animation must be controllable.
- AI difficulty must be real and testable. Online modes must use server-validated state, not pretend local multiplayer.
- No game is labelled READY until its core rules, controls, navigation, reconnect/disconnect paths, and device layout pass tests.
- Keep current PLAYAM app stable; build game systems in isolated modules/projects and integrate only after tests.

## Visual and mode direction
- Snooker: premium cue-sports presentation inspired by 8 Ball Strike; realistic table, cloth, cushions, balls, cue aiming, spin, shot power, camera options, practice, timed challenge, tournaments, and multiplayer variants.
- Pool: 8 Ball Pool-style accessible presentation with original PLAYAM identity; 8-ball, 9-ball, practice, timed tables, tournaments, friends and ranked matchmaking.
- Ludo: Ludo Star-style social board experience with original art; classic, quick, team, private-room, tournament and AI modes.
- American football: original PLAYAM football modes inspired by the depth of college-football and NFL mobile games. Do not use NFL, NCAA, EA or team/player marks without licences.
- Checkers: polished draughts with standard rules, variants, puzzles, AI levels, local and online play.
- Ayo: Oware/Awale rules with tutorial, ranked, casual, variants and online play.
- Team Deathmatch: original competitive FPS modes with tactical movement, weapon balance, maps, loadouts, bots and online matchmaking.
- Battle Royale: original large-map survival shooter modes, squads/solo, loot, shrinking zone, vehicles only where supported, and fair matchmaking.
- Tactical 5v5: objective-based tactical FPS with round economy, team roles, maps, practice and ranked modes.
- Survival Extraction: original PvE/PvPvE extraction loop with loot, inventory, risk/reward, progression and server-authoritative saves.
- Zombie Survival: original cooperative wave/story modes, missions, crafting, upgrades and boss encounters.
- Casual games: sorting, fashion, makeover and short-session puzzle/challenge modes; each should be a distinct game, not a mislabeled placeholder.
- Scoreboard: clearly explained sports prediction/competition formats, transparent scoring and eligibility. No misleading gambling claims.
- Legends: original fantasy RPG/MOBA-inspired modes, heroes, progression and fair matchmaking; licensed properties and assets are not reused.
- Live Q&A: live host/stream questions, timed audience votes, red "Lie" and green "True" judgement buttons, visible vote totals, scoring and moderation. The buttons record audience votes; they do not scientifically detect lies. Mature party content must be age-gated, consensual and moderated.

## Call of Duty
The user has specifically asked for genuine Call of Duty, not a PLAYAM-made imitation labelled COD. Link to official Call of Duty Mobile distribution or pursue a formal licensing/partnership route if eligible. Do not copy Activision assets, branding, maps, characters or imply affiliation. A separate original PLAYAM shooter may be developed under its own name and identity.

## Engineering approach
- Existing PLAYAM website is a web app/prototype, not a native Unity game build.
- Evaluate a dedicated Unity mobile project for the high-fidelity 3D/competitive games. Keep turn-based/casual games modular where a lighter engine is suitable.
- Keep game rules and networking separate from presentation.
- For online play, use authoritative server validation, room lifecycle, reconnect handling, anti-cheat protections, rate limits and moderation. Never trust client-submitted match results.
- Before schema changes, inspect existing Supabase auth, tables, RLS and realtime setup. Never put service-role keys in client code.
- Native store release requires signed iOS/Android builds, device testing, privacy/content disclosures, and applicable store billing/licensing compliance.

## Delivery sequence
1. Stabilise game navigation and enforce one active game session at a time.
2. Select one pilot (Ludo is the recommended first pilot) and implement/test it end-to-end.
3. Build cue-sports games next, then board/casual games, then competitive online shooters and larger simulation games.
4. Add online multiplayer only with server-side validation and operational monitoring.
5. Integrate each finished game into PLAYAM only after acceptance tests.

## Acceptance checklist per game
- Launch and exit without leaving another game active.
- All buttons and menus have real actions.
- Core rules and edge cases tested.
- Touch controls tested on small and large mobile screens.
- AI opponents tested at each advertised difficulty.
- Online room creation, join, turn/action validation, reconnect, timeout and results tested where online is advertised.
- Audio, animation, pause/resume and accessibility settings tested.
- No fake "coming soon" controls presented as playable.
- No production release or paid service activation without explicit approval.
