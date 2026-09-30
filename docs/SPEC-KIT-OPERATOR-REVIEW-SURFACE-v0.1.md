# ERRATA — Spec Kit: Operator Review Surface v0.1

**Lifecycle:** DELIVER  
**Parent:** `docs/PRD-v0.1.md`  
**Prerequisite:** External Acceptance Slice — PROVEN  
**Status:** READY FOR IMPLEMENTATION  
**Scope:** smallest credible operator-facing review surface using the existing shared product core

## 1. Objective

Turn the proven terminal mechanism into a legible operator workflow without creating a second business-logic stack.

The surface must make the central ERRATA promise visually obvious:

> One change. One identity. Spoken corrections amend the same truth — they never fork it.

The UI is a review/control surface. It does not replace the deterministic coordinator, resolver, reducer, validators, consequence calculator, artifact graph, or human hash-bound commit guard.

## 2. Product contract

The surface reads from and acts through the existing canonical `LiveTransactionCoordinator`.

It may:

- submit bounded direct-entry text through the shared parser for fallback/testing;
- display live transcript/capture state;
- display pending/prepared/applied/review-required/rejected outcomes;
- request snapshots;
- request explicit human commit against the visible current hash.

It must not:

- mutate `ServiceChange` fields directly;
- recreate parser/reducer logic in JavaScript;
- synthesize a successful state when the backend refused/reviewed;
- hide unresolved cues or validator failures;
- make commit automatic;
- present synthetic fixture data as agency live data.

## 3. Above-the-fold information hierarchy

The first viewport must show:

1. **Change identity** — `change_id`
2. **Revision** — current revision number
3. **Canonical hash** — visibly shortened with full-copy affordance
4. **Truth/evidence label** — e.g. SYNTHETIC / LIVE STT / LOCAL
5. **Current operational state**
   - route
   - direction
   - service date
   - time window
   - skipped stops
6. **Latest amendment status**
   - CAPTURED
   - PREPARED
   - APPLIED
   - REVIEW_REQUIRED
   - REJECTED
7. **Exact semantic diff** for the latest successful amendment
8. **Human commit control** bound to the visible current hash

A judge/operator should not need terminal logs to answer “what changed, why, and can it be committed?”

## 4. Primary screen regions

### A. Change header

- ERRATA wordmark / working-name label
- `change_id`
- revision badge
- status: STAGED / COMMITTED
- evidence/truth tag
- connection/recovery status

### B. Canonical state

Structured, compact state card:

- Route
- Direction
- Service date
- Start
- End
- Skipped stops
- Unresolved items

Each field may expose provenance on demand.

### C. Amendment timeline

Chronological revision history:

- rev number
- transcript/direct-entry text
- operations
- before hash → after hash
- result
- supersession/repair relationship where relevant

The active revision should be visually dominant; older revisions remain inspectable but not confused with current truth.

### D. Latest transaction

Shows:

- captured text
- parsed operations
- unresolved cues
- validation outcome
- consequence delta
- mutation result

REVIEW_REQUIRED and REJECTED must be visually distinct from APPLIED.

### E. Consequence / artifact panel

For the bounded fixture:

- affected trip count
- affected trip IDs
- skipped stop-time count
- generated GTFS-RT artifact status
- artifact source hash
- independent consumer status
- canonical validator status / warnings

### F. Commit rail

Commit remains a protected human action.

Required interaction:

1. operator sees full current revision/hash context;
2. operator explicitly selects commit;
3. UI confirms the hash being reviewed;
4. backend executes `human_commit(hash_prefix)`;
5. stale hash refusal is surfaced without mutation;
6. successful commit shows receipt authority and final status.

## 5. Required states

The UI must have deterministic render states for:

- EMPTY / initial staged change
- CAPTURING
- PREPARED
- APPLIED
- REVIEW_REQUIRED
- REJECTED
- RECONNECTING
- RECOVERED
- STALE_REVIEW
- COMMITTED

No generic “error” state may replace a domain-specific refusal when the backend provides one.

## 6. Required demo scenarios

### Scenario S1 — canonical success

Initial:
`Route 55 west, skip King Edward and Cumberland until 9:30.`

Correction:
`Wait, keep Cumberland. Make it 10.`

Expected UI:
- same change identity;
- rev 1→2→3;
- King Edward remains skipped;
- Cumberland restored;
- end 10:00;
- clear semantic diff.

### Scenario S2 — atomic review

Malformed/incomplete correction.

Expected:
- REVIEW_REQUIRED;
- unresolved cue visible;
- revision/hash unchanged;
- no partial semantic diff presented as applied truth.

### Scenario S3 — stale commit

Attempt commit with prior revision hash.

Expected:
- stale review refusal;
- current state untouched;
- current hash visually re-emphasized.

### Scenario S4 — recovery

Reconnect transport at known revision.

Expected:
- RECONNECTING;
- RECOVERED;
- same revision/hash continuity shown;
- later amendment applies on same identity.

### Scenario S5 — external acceptance

Show:
- official bindings consumer PASS;
- canonical validator PASS with zero ERROR groups;
- retained validator warnings W002/W008 with explanations;
- synthetic-fixture truth boundary.

## 7. Backend surface contract

Minimum local API/service layer should expose equivalents of:

- `GET /api/change` — canonical snapshot + latest transaction/evidence summary
- `POST /api/amend/direct` — bounded direct text through shared parser/coordinator
- `POST /api/commit` — explicit reviewed hash/prefix
- `POST /api/reset-demo` — deterministic demo reset only
- `GET /api/evidence` — external acceptance + runtime evidence summaries

Live microphone capture may remain in the existing controlled Streaming process initially, but state events must use the same coordinator object if shown in the same product session.

No endpoint may accept arbitrary canonical-state field replacement.

## 8. Visual/design requirements

Design must be operational, evidence-forward, and domain-native.

Avoid:

- generic dark “AI command center” styling;
- chat-bubble-first layouts;
- decorative agent avatars;
- excessive gradients/glow;
- hidden proof in secondary screens;
- dashboard-card clutter without hierarchy.

Prefer:

- strong state hierarchy;
- revision/timeline framing;
- evidence receipts as first-class UI;
- semantic before/after emphasis;
- restrained transit-operations visual language;
- responsive layout that keeps current truth and commit context together.

A separate visual-reference pass should precede polish implementation.

## 9. Accessibility / interaction

- keyboard operable;
- visible focus states;
- status is never color-only;
- reduced-motion compatible;
- copyable hashes/receipts;
- no critical detail accessible only through hover;
- responsive through laptop/tablet widths.

## 10. Evidence instrumentation

Every demo action should be able to produce:

- timestamp;
- action type;
- before revision/hash;
- after revision/hash;
- transcript/direct-entry source;
- parsed operations;
- result status;
- validator/refusal details;
- commit receipt when relevant.

UI screenshots are presentation evidence only; canonical receipts remain authoritative.

## 11. Acceptance criteria

The surface slice is accepted when:

1. it renders the canonical current state from the shared Python core;
2. canonical initial + correction scenario is operable;
3. REVIEW_REQUIRED produces no hidden mutation;
4. semantic diff is visible for APPLIED revisions;
5. stale commit refusal is visible;
6. current hash-bound commit works;
7. external-consumer / canonical-validator evidence is visible;
8. no JavaScript-only business rule can mutate canonical truth;
9. deterministic tests remain green;
10. a judge can understand the hero mechanism without opening terminal logs.

## 12. Definition of Done

This spec is complete when implementation can begin without reopening product semantics.

Implementation itself remains `Real-user Surface = ACTIVE` until the browser/operator surface is running and demonstrated against the shared core.
