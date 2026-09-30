# ERRATA — Final Judge-Facing UI/UX Pass v0.2 · "Live Caption"

Branch: `judge-uiux-opus-v0.1` · Brief: [`OPUS55-UIUX-FINAL-BRIEF-v0.1.md`](OPUS55-UIUX-FINAL-BRIEF-v0.1.md)
Supersedes the v0.1 "errata slip" direction; chosen from five explored directions (Signal Box, Live Caption, Restatement, Strip, Overprint).

## Scope held

Changed: `web/operator/index.html`, `web/operator/app.css`, `web/operator/app.js` (render functions, view router, presentation hooks only), self-hosted fonts in `web/operator/fonts/` (Bricolage Grotesque + DM Mono, SIL OFL 1.1, license included), screenshots in `docs/ui/`.

Not changed: parser, reducer, validators, session signing, FastAPI/Vercel routes, AssemblyAI authority boundary, GTFS-RT serialization, evidence truth labels, commit/refusal behavior, request payloads. Every element id used by tests, CI smoke and docs is preserved; every panel stays in the DOM (views only toggle `hidden`). Status codes and truth labels are shown verbatim.

## Direction — broadcast control room

*Speech is a draft. Truth is versioned.*

- **Caption bars** are the signature element. What ERRATA is hearing is a dashed-outline caption (draft, not on air). What is canonical is a solid yellow caption (on air). A dropped attempt is a hatched, struck caption with `0 canonical effect · hash unchanged`.
- **Tally light**: the mic state is a broadcast tally in the top bar (magenta = live).
- **Timeline = edit reel**: one `change_id`, every applied revision is a keyframe; dropped frames sit between keyframes on a dashed track and never air; the reel ends at the commit gate (`✕ REFUSED` stale hash ≠ current, `✓ COMMITTED` current hash).
- **Edit marks** for parsed operations: SKIP ✕ in magenta, KEEP as *stet · kept*, END with the old time struck and the new time on yellow.
- **Colour semantics** (always doubled by text, pattern or shape): yellow = on air / canonical / committed; magenta = intervention (listening, correction, refusal); dashed white = draft; hatched grey = dropped.

## Not one long page — five views

A persistent top bar (wordmark, tally, view nav with live badges, canonical chip) and a persistent bottom **dock** (the mini reel + the next reference step as a single CTA) frame five hash-routed views:

| View | Contents |
|---|---|
| `#/air` 01 On Air | 5-second story (who / without it / ERRATA / "Voice proposes. Humans commit."), live caption stage, voice pipeline Mic › Caption › Draft › Apply (human) › On air, draft card (on air untouched vs would air), dropped frame, ERRATA replies, typed entry, voice settings |
| `#/timeline` 02 Timeline | the reel + event log |
| `#/commit` 03 Commit | canonical change (huge revision numeral, hash), hash-checked commit gate with live display-only hash comparison, latest transaction |
| `#/feed` 04 Feed | decoded rider feed (trip × skipped stop), decoded proof list, derived impact |
| `#/ledger` 05 Ledger | materialized state, blocking validators, external evidence, demo reset |

Nav badges: On Air `live / hearing / draft / ?`, Timeline `revN`, Commit `ready / ✕ refused / ✓ sealed`, Feed `decoded`, Ledger `n/5`. When the mic goes live the On Air intro compacts so the caption becomes the hero. Each view has its own `h1`; route changes move focus to it.

## Motion (each tied to a backend-reported transition)

View change fade-up · reel draws once on load · new revision: keyframe cuts in, caption fades on, revision numeral flips, canonical chip bumps · dropped frame: strike draws, frame settles off the track · refusal / commit: stamp lands · artifact refresh: yellow ring on the rider feed · listening: tally and caret blink. Nothing animates toward canonical before Apply. `prefers-reduced-motion: reduce` removes all movement and keeps every final state.

## Verification (headless Chromium, local core)

Driven through the real local core; voice turns use the real `/api/preview/voice` and `/api/amend/voice`. Only the mic/WebSocket connection is simulated (no microphone or AssemblyAI key in the sandbox).

- States: provider unavailable, disconnected, listening + partial, READY_TO_APPLY, NEEDS_CLARIFICATION, dropped/superseded, rev1/rev2/rev3, stale refusal, current-hash commit, decoded GTFS-RT, sealed + mic stopped — at 1440×900, 390×844 and 1280×800 with reduced motion.
- 0 px horizontal overflow on every view at every size; 0 console errors.
- axe-core (WCAG 2 A/AA + best practice): **0 violations** on all 5 views × initial, mid-scenario, sealed, mobile.
- `pytest`: 59 passed. CI smoke strings (`id="referenceGuide"`, `voiceStatus`, `voiceEngine`, `neuralVoice`, `exportVoiceReceipt`, "Voice proposes.", "Humans commit.") present.

## Still open

- First-5-second comprehension not yet human-tested.
- Live browser proof with a real microphone and AssemblyAI key to be re-run on this branch.
- Vercel deployment of this branch.

## Screenshots

`docs/ui/01…11`.
