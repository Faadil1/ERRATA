# ERRATA — Operator Review Surface Human Visual Audit v0.2

**Reviewed artifact:** human screen recording, 74.6 s  
**Surface:** local operator review browser at `127.0.0.1:8765`  
**Truth boundary:** synthetic GTFS fixture / local shared-core surface  
**Implementation CI head:** `c26b15cab7e71fe38c99de749e8265ebcda5dc77`  
**CI run:** `36667899502` — SUCCESS

## Verdict

**PASS — bounded local operator surface**

The corrected surface is now legible enough to promote the operator review surface itself. The recording demonstrates the shared-core workflow, protected commit behavior, refusal/review states, and explicit synthetic/local truth boundary without requiring terminal logs.

This is **not** external operator validation or production UX proof.

## What the recording proves

### 1. Current truth is visible above the fold

The revised header exposes:

- change identity;
- revision;
- canonical hash;
- pending mutation count;
- route;
- direction;
- effective window;
- skipped stops;
- LOCAL / SYNTHETIC truth label.

The core operational state is therefore legible before scrolling into the detailed materialized state table.

### 2. Premature commit is safely handled

The recording intentionally commits a valid rev2 before the hero correction.

Observed:

- rev2 commit succeeds;
- status becomes COMMITTED;
- authoring controls disable;
- the UI shows **Change sealed**;
- later amendments cannot mutate that committed change;
- protected action receipt is visible.

This confirms the product surface reflects the backend invariant rather than hiding it.

### 3. Demo reset restores a clean staged change

The recording resets after the early-commit test and returns to the seeded revision-1 staged context.

### 4. Canonical amendment flow is understandable

On the clean second walkthrough:

- initial Route 55 change applies;
- guide advances to the correction step;
- correction applies to rev3;
- end time becomes 10:00;
- Cumberland is restored;
- King Edward remains skipped.

### 5. Negative/review state is visible

The malformed correction `Wait, keep Cumberland. Make it.` surfaces:

- `REVIEW_REQUIRED`;
- explicit unresolved-cue reason;
- no semantic state drift.

### 6. Repeated/invalid correction is visibly rejected

A subsequent correction that attempts to keep Cumberland again is shown as REJECTED because Cumberland is no longer skipped.

The refusal is domain-specific and visible rather than collapsed into a generic error.

### 7. Stale-review refusal is demonstrable

The recording loads a prior hash and produces a visible `STALE_REVIEW` event in the revision trail while current rev3 state remains unchanged.

### 8. Current-hash commit is explicit and legible

The final current hash is committed through the protected human-action rail.

Observed:

- explicit review checkbox;
- current reviewed hash;
- commit receipt;
- final COMMITTED state;
- authoring lock;
- committed hash shown in canonical state.

### 9. External acceptance evidence is visible

The evidence rail shows:

- official bindings consumer PASS;
- canonical validator errors = 0;
- pinned validator identity;
- CI workflow reference;
- retained validator warnings.

The synthetic-fixture / non-production boundary is also visible.

## Remaining UX observations

These are polish/depth items, not promotion blockers:

- the page remains information-dense and scroll-heavy;
- revision history is technically strong but visually compact;
- the demo stepper does not separately track the malformed-correction side experiment;
- a dedicated live-voice capture affordance is not yet part of this browser surface;
- public-network realism is not demonstrated here.

## Gate consequence

Promote in bounded local/synthetic scope:

- `Operator Review Surface → PROVEN`
- `Real-user Surface → PROVEN`

Keep separate:

- `External Operator Evidence → BLOCKED`
- `Voice-native Necessity → ACTIVE`
- public-network realism remains open.

## Next P0

**Representative Public-Network Scenario**

Run the hero mechanism against a public/non-synthetic GTFS dataset while preserving the same truth boundary and external validation chain.
