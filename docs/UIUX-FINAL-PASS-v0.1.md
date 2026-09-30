# ERRATA — Final Judge-Facing UI/UX Pass v0.1

Branch: `judge-uiux-opus-v0.1` · Brief: [`OPUS55-UIUX-FINAL-BRIEF-v0.1.md`](OPUS55-UIUX-FINAL-BRIEF-v0.1.md)

## Scope held

Changed: `web/operator/index.html`, `web/operator/app.css`, `web/operator/app.js` (render functions and presentation hooks only), self-hosted fonts in `web/operator/fonts/` (SIL OFL 1.1, license included), screenshots in `docs/ui/`, one wording line in `BROWSER-VOICE-PROOF-PROTOCOL-v0.1.md` (Barge-in now sits inside the voice settings disclosure).

Not changed: parser, reducer, validators, session signing, FastAPI/Vercel routes, AssemblyAI authority boundary, GTFS-RT serialization, evidence truth labels, commit/refusal behavior, request payloads. Every API call in `app.js` (`/api/amend/direct`, `/api/amend/voice`, `/api/preview/voice`, `/api/commit`, `/api/reset-demo`, `/api/voice-token`, `/api/session-receipt`) is sent with the same body as before. All element ids used by tests, docs and the voice flow are preserved. Status codes (`APPLIED`, `REVIEW_REQUIRED`, `STALE_REVIEW`, `COMMITTED`, `READY_TO_APPLY`, `NEEDS_CLARIFICATION`, …) and truth labels are shown verbatim; the UI adds glosses beside them, never instead of them.

## Direction — "the errata slip on the line"

A printer's correction slip laid over a transit strip map.

- **The Line** (hero): one cobalt line named by the `change_id`. rev1 → rev2 → rev3 are stations on the same line — visibly no fork. Ghost speech hangs off a station as a dashed lavender spur marked `0 canonical effect · hash unchanged`. The line ends at a **commit gate** where refusals land as `REFUSED` stamps (stale hash ≠ canonical) and the commit as `COMMITTED`.
- **Proofreader marks** for parsed operations: `SKIP` = struck in vermilion, `KEEP` = *stet* (literally "let it stand"), `END` = old time struck, new time highlighted.
- **Colour semantics** (never colour-only — each also has text, pattern or shape): cobalt = canonical; vermilion = correction/refusal; lime = live/current/human door; dashed lavender = ghost, no authority; hatching = held/refused.
- **Type roles**: grotesk (Archivo, variable width) = structure; serif italic (Instrument Serif) = human speech; mono (JetBrains Mono) = machine truth (ids, hashes).
- Headline performs the product: *ERRATA ~~forks~~ ⁁repairs the same service change.*
- **Voice proposes. Humans commit.** states point 4 of the 5-second test in one line.

## First viewport (1440×900)

Promise → who / without it / with ERRATA → "Voice proposes. Humans commit." → the full Line including the commit gate. The sticky masthead carries live state at all times: `change_id · rev · hash6 · SEALED`, mic state, core connection. Governance tables (validators, event log, external evidence, reset) moved below the fold into a "Ledger".

## Motion (each tied to a backend-reported transition)

| Transition | Motion |
|---|---|
| Page load | Line draws left→right, stations offset-and-delay in (once) |
| Revision became canonical | new segment draws, station dot morphs in, revision numeral flips, masthead chip bumps |
| Transcript arriving | lime caret on partial text |
| Ghost speech leaves authority | strike draws through the quote, spur drifts off the line |
| Stale commit refused / commit accepted | stamp lands |
| Downstream artifact refreshed | lime ring pulse on the rider-feed card |

Motion classes are only attached after the backend reports the change; the non-mutating preview never animates into the canonical area. `prefers-reduced-motion: reduce` removes all movement and ping loops while keeping every final state.

## States verified (headless Chromium, local core)

Driven through the real local core (`scripts/run_operator_surface.py`); voice turns use the real `/api/preview/voice` and `/api/amend/voice` endpoints. Only the microphone/WebSocket connection is simulated, because the sandbox has no microphone or AssemblyAI key.

| State | Result |
|---|---|
| Provider unavailable (voice token 503) / no microphone | error badge, explanation, "canonical state is unchanged" |
| Disconnected | ✓ |
| Listening + partial transcript | pipeline at *Transcribe*, caret, "not yet applied" |
| READY_TO_APPLY | preview card: canonical rev1 (untouched) ⇢ candidate rev2, ghosted diff; Apply door lit |
| NEEDS_CLARIFICATION | vermilion preview, Apply locked |
| Ghost / superseded speech | struck quote, `0 effect · hash unchanged`, spur on the Line |
| rev1 / rev2 / rev3, same `change_id` | ✓ |
| Stale commit refusal | `REFUSED` stamp in commit panel and gate, canonical rev unchanged |
| Current-hash commit | seal, masthead `SEALED`, authoring locked |
| Downstream GTFS-RT decoded view | trip × skipped-stop strip + decoded proof list |
| 390×844 mobile | Line turns vertical; 0 px horizontal overflow |
| 1280×800 and 1440×900 | 0 px horizontal overflow |
| Reduced motion | all states render in final form |

Accessibility: axe-core (WCAG 2 A/AA + best practice) reports **0 violations** in initial, mid-scenario (preview + ghost), stale-refusal, committed and mobile states. Visible focus ring on every control (cobalt + lime halo; inverted in the voice booth), skip link, `aria-live` on voice status, transcript, preview, ghost and guidance, plus an assertive announcer for revision advance / refusal / commit / zero-effect.

`pytest`: 59 passed, unchanged.

## Still open (honest boundary)

- First-5-second comprehension has **not** been human-tested; it needs a real person who hasn't seen ERRATA.
- Live browser proof with a real microphone and AssemblyAI key must be re-run on this branch per `BROWSER-VOICE-PROOF-PROTOCOL-v0.1.md`.
- Vercel deployment of this branch not yet performed.

## Screenshots

`docs/ui/01…09` — first viewport (fresh and completed story), voice preview, ghost speech, stale refusal, committed + decoded GTFS-RT, mobile, reduced motion.
