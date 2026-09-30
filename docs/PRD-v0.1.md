# ERRATA — Living Product Requirements Document v0.1

**Status:** ACTIVE / living document  
**Lifecycle:** DELIVER  
**Source of truth:** this repository  
**Concept lock:** v2  
**Prototype Killer:** PROVEN in bounded Technical Reality scope  
**Working name:** ERRATA; Naming / Collision Gate remains ACTIVE

> One change. One identity. Spoken corrections amend the same truth — they never fork it.

## 1. Product definition

ERRATA is a transit-operations change-authoring system for high-consequence service adjustments.

Its locked mechanism is narrow:

**self-correcting live speech → minimal typed amendments → one versioned staged ServiceChange → deterministic validation/consequence computation → explicit human review/commit → independently consumable transit output**

The product is not a generic voice assistant. It is a controlled authoring surface for operational change where probabilistic speech interpretation may propose intent, but canonical mutation and commit authority remain deterministic and human-controlled.

## 2. Problem

Transit control work frequently turns fast-changing operational intent into structured service adjustments. The risky part is not only recognizing speech. The system must preserve one change identity while operators correct themselves, reject ambiguous or contradictory input, keep a durable revision trail, recompute downstream consequences, and prevent stale review from becoming an authorized commit.

The negative event ERRATA is designed around is:

> a partially understood, superseded, interrupted, or stale instruction leaks into operational state and produces an incorrect or unauditable service change.

## 3. Intended user and JTBD

### Primary intended user

Transit operations controller / control-centre staff member staging a service adjustment.

External operator desirability is **not yet proven**.

### Core job to be done

> When service conditions change quickly, help me turn a spoken operational instruction and its corrections into one reviewable, versioned service change without making me restate the whole change or trust an opaque assistant with commit authority.

### Supporting jobs

- see exactly what changed between revisions;
- know what the system understood vs what remains unresolved;
- refuse unsafe/ambiguous amendments without silently applying the understood subset;
- review deterministic consequences before commit;
- prevent stale approvals from applying to newer state;
- produce an output that another system can independently consume.

## 4. Goals

### G1 — One canonical change identity

All amendments to one operational intent remain on the same `change_id`.

### G2 — Minimal correction

A correction changes only the explicitly targeted semantics; unrelated fields do not drift.

### G3 — Atomic ambiguity handling

If an utterance explicitly signals multiple coupled changes and one material component is unresolved, the batch is review-only. The system must not apply the resolvable subset.

### G4 — Human authority

The system may prepare and validate changes, but a consequential commit requires explicit human action bound to the current reviewed state hash.

### G5 — Deterministic operational truth

Entity resolution, state reduction, conflict/refusal logic, consequence calculation, artifact invalidation, and commit checks are deterministic code paths.

### G6 — Independent acceptance

The final transit artifact must be validated/consumed outside ERRATA's own UI before product-level promotion.

### G7 — Voice utility without voice dogma

Voice must earn its place. It is acceptable only if it provides material workflow value relative to direct entry, such as correction speed, lower context-switch cost, or hands/eyes availability.

## 5. Non-goals

ERRATA v0.1 does not attempt to:

- become an autonomous dispatcher;
- publish directly into a live agency production system;
- treat GTFS-Realtime as the agency operational source of truth;
- infer passenger-impact counts without demand data;
- generate unsupported detour geometry as fact;
- claim global product novelty;
- replace existing OCC/dispatch systems;
- make an LLM the source of operational truth;
- prove production-grade speech reliability from local prototype runs.

## 6. Locked mechanism

The canonical flow is:

```text
live speech
  ↓
AssemblyAI Streaming STT
  ↓
provider transcript fragments
  ↓
human-owned transaction boundary
  ↓
bounded semantic parser
  ↓
typed pending operation batch
  ↓
deterministic entity resolution + validation
  ↓
pure reducer
  ↓
ServiceChange IR (change_id + revision + state_hash)
  ↓
consequence / artifact graph
  ↓
human hash-bound review + commit
  ↓
transit output adapters
  ↓
external validator + independent consumer
```

The managed Voice Agent path remains a sponsor-native comparison surface, not the authoritative mutation boundary, because live tests showed irregular managed turn segmentation for this task.

## 7. Canonical invariants

- **I-01 Same identity:** amendments never silently create a new change.
- **I-02 Revision monotonicity:** one revision increment per atomic applied batch.
- **I-03 Minimal correction:** non-targeted fields remain semantically identical.
- **I-04 History preservation:** superseded operations remain auditable.
- **I-05 Human boundary:** provider end-of-turn never authorizes canonical mutation.
- **I-06 Atomic ambiguity:** explicit unresolved cues block the whole amendment batch.
- **I-07 Deterministic truth:** free-form transcript never directly becomes operational fact.
- **I-08 Artifact invalidation:** outputs derived from an older state hash become stale.
- **I-09 Stale commit rejection:** an old reviewed hash cannot commit.
- **I-10 Human commit authority:** no model/tool may self-authorize commit.
- **I-11 Independent acceptance:** final output must be accepted outside ERRATA's own parser/UI.
- **I-12 Voice/text convergence:** equivalent final intent should converge semantically.
- **I-13 Recovery continuity:** transport replacement must not change canonical revision/hash.
- **I-14 Truth-bound evidence:** every promoted live claim must bind to runtime/evidence receipts.

## 8. Primary user flow

1. Operator starts a staged service change.
2. Operator speaks a bounded operational instruction.
3. Operator explicitly ends the transaction boundary.
4. ERRATA receives/accumulates final transcript fragments.
5. Parser emits typed operations plus unresolved-cue markers.
6. If material ambiguity remains, ERRATA returns REVIEW_REQUIRED with no mutation.
7. Otherwise deterministic resolver/validators prepare the amendment.
8. Reducer applies one atomic revision.
9. Operator sees the exact semantic diff, consequences, stale artifacts, revision and hash.
10. Operator may issue a spoken correction against the same change identity.
11. A stale reviewed hash is refused.
12. Current hash may be committed only by explicit human action.
13. Output is serialized and checked by an external validator/consumer.

## 9. Hero demo

Canonical scenario:

> “Route 55 west, skip King Edward and Cumberland until 9:30.”

Then:

> “Wait, keep Cumberland. Make it 10.”

Expected visible result:

- same `change_id`;
- revision 1 → 2 → 3;
- King Edward remains skipped;
- Cumberland is restored;
- end time becomes 10:00;
- unrelated fields remain unchanged;
- unresolved or malformed correction attempts produce REVIEW_REQUIRED / refusal with no partial mutation;
- stale reviewed hash is rejected;
- current hash can be committed only by the human;
- downstream artifact from an older hash is visibly stale;
- final output passes an independent acceptance check.

The judge-facing version should expose the revision/hash/evidence boundary above the fold rather than hide it in logs.

## 10. Functional requirements

### MUST

- preserve one `change_id` across amendments;
- expose monotonic revision + canonical state hash;
- parse the bounded route/direction/skip/keep/time grammar;
- preserve typed operation provenance;
- reject unresolved entities and contradictory operations;
- block partial amendment leakage when explicit cues remain unresolved;
- support human-owned endpoint/apply;
- recompute deterministic consequences from state, not transcript;
- invalidate stale derived artifacts;
- reject stale reviewed hashes;
- require explicit human commit;
- survive bounded live transport reconnect without state drift;
- emit runtime/evidence receipts;
- serialize the bounded transit artifact;
- pass an external/canonical validation path before product-level promotion.

### SHOULD

- present a concise semantic diff per amendment;
- show source/provenance status for material fields;
- show why REVIEW_REQUIRED / REJECTED happened;
- provide an operator-facing review surface instead of terminal-only interaction;
- surface stale artifacts and dependent outputs;
- make recovery/reconnect status visible;
- preserve a deterministic demo mode using the same shared product core.

### MAY

- use managed Voice Agent features for conversational assistance where they are not the transaction-authority boundary;
- support alternate structured/direct-entry input through the same parser/reducer core;
- support additional bounded operation types after the core invariants remain proven;
- add richer consequence views once public-network data is integrated.

### MUST NOT

- allow provider turn completion to mutate state automatically;
- allow an LLM to commit;
- fabricate GTFS entities;
- silently apply only the understood half of a material correction;
- present LOCAL_STUB evidence as LIVE;
- claim external validation from ERRATA's own parser;
- imply agency integration, production readiness, or controller adoption without evidence.

## 11. Product surfaces

### P0 — Operator review surface

Required next product surface:

- live transcript/capture state;
- pending vs applied amendment;
- semantic diff;
- revision/hash;
- validation/refusal reason;
- consequence summary;
- artifact freshness;
- explicit commit affordance.

### P1 — Evidence / judge surface

- runtime SHA;
- evidence label;
- before/after hashes;
- deterministic receipts;
- scenario status;
- external validation result;
- no need to inspect raw terminal logs to understand the proof.

### P2 — Direct-entry comparison surface

A structured keyboard path should remain available as a baseline and fallback, sharing the same deterministic core.

## 12. Architecture

### Load-bearing components

- AssemblyAI Streaming STT — live speech recognition;
- controlled human endpoint — mutation admission boundary;
- bounded parser — typed operation extraction;
- deterministic resolver/validator — entity and domain truth;
- reducer — canonical state transitions;
- `ServiceChange` IR — one identity/revision/hash;
- artifact/consequence layer — derived state;
- human commit guard — hash-bound authorization;
- output adapter — GTFS-Realtime-shaped artifact;
- external validator/consumer — independent acceptance.

### Shared product core

Voice and direct entry must converge on the same parser/coordinator/reducer semantics wherever applicable. Separate modality-specific business logic is not allowed.

## 13. Non-functional requirements

### Safety / correctness

- fail closed on unresolved material intent;
- no partial side effect from an incomplete atomic correction;
- stale hash commit rejection is deterministic;
- reconnect must preserve exact canonical state.

### Auditability

- revision and hash visible at every consequential step;
- operation provenance retained;
- runtime SHA/evidence manifest available for promoted runs;
- negative paths recorded, not only successes.

### Performance

Prototype target is not “voice must always be faster.”

Current bounded evidence shows near aggregate parity with direct typing across the two canonical phases, with keyboard faster on the longer initial instruction and voice faster on the short correction.

Future acceptance must measure realistic operator workflow value, not only raw speech latency.

### Reproducibility

- deterministic core tests must pass in CI;
- demo path must be repeatable;
- external dependencies and fixture boundaries must be explicit.

## 14. Current evidence ledger

### PROVEN in bounded scope

- live controlled Streaming core;
- same-identity amendment;
- minimal correction for canonical scenario;
- human-controlled capture boundary;
- ForceEndpoint efficacy;
- runtime/evidence binding;
- stale commit rejection;
- human commit authority;
- transport reconnect continuity;
- post-reconnect successful amendment;
- direct-entry semantic convergence;
- LOCAL_STUB artifact invalidation and idempotency.

### ACTIVE / incomplete

- `UNBOUND_TIME_VALUE` live negative-path isolation;
- AssemblyAI broader load-bearing/ablation claim;
- public-network entity resolution;
- consequence depth;
- operator-facing surface;
- external operator desirability;
- stronger voice-native necessity evidence;
- operational economics.

### BLOCKED

- external/canonical GTFS-RT validation;
- independent third-party consumer acceptance;
- real consequence promotion dependent on those external checks;
- agency live integration;
- production readiness.

## 15. Success metrics

### Mechanism

- zero silent partial mutations in the canonical scenario set;
- 100% stale reviewed-hash rejection;
- 100% same-identity preservation across amendments;
- exact semantic convergence between supported voice and direct-entry scenarios;
- exact revision/hash continuity across bounded reconnect.

### Operator workflow

To measure with real/external users:

- time to correct staged change;
- number of interaction/context switches;
- correction retries;
- unresolved/review rate;
- unintended field drift;
- operator confidence in what changed;
- recovery time after transport failure.

### Output

- external validator acceptance;
- independent consumer correctly observes final amended state.

## 16. Risks

### R1 — Speech corruption

STT may drop linking language while retaining entities/numbers.

Mitigation: explicit unresolved-cue guards, bounded grammar, REVIEW_REQUIRED, human transaction boundary.

### R2 — False semantic completeness

A batch can contain plausible operations while omitting intended coupled changes.

Mitigation: atomicity rules and adversarial live corpus; continue expanding from observed failures rather than hypothetical grammar alone.

### R3 — Demo-only transit realism

Synthetic fixture behavior may look correct while failing on real/public network data.

Mitigation: external/canonical GTFS-RT validation and independent consumer are mandatory next depth gates.

### R4 — Voice is not materially useful

Direct entry may be equal or better for some workflows.

Mitigation: preserve direct-entry baseline and test actual controller context, especially corrections and hands/eyes availability.

### R5 — Terminal prototype mistaken for product

A technically valid terminal harness is not an operator experience.

Mitigation: build operator review surface before product/judge-ready promotion.

## 17. Dependencies

- AssemblyAI Streaming API and credentialed access;
- deterministic Python core;
- GTFS static/reference data;
- GTFS-Realtime serialization;
- external validator/consumer path;
- operator/user access for desirability testing;
- GitHub Actions for deterministic CI/evidence.

## 18. Acceptance criteria for v0.1 delivery slice

The delivery slice is accepted when:

1. current deterministic tests remain green;
2. operator review surface uses the shared product core;
3. canonical hero flow works through that surface;
4. malformed/ambiguous corrections show review/refusal without state drift;
5. revision/hash/diff are visible;
6. stale commit refusal is visible;
7. transport recovery state continuity is visible or demonstrable;
8. external validator accepts the generated artifact;
9. an independent consumer observes the corrected final state;
10. evidence packet binds runtime to the demonstrated state;
11. no claim exceeds its evidence label.

## 19. Evidence plan

For every promoted scenario, capture:

- runtime Git SHA;
- evidence label;
- provider/session identifier where applicable;
- transcript/typed operations;
- before/after revision + state hash;
- unresolved/refusal reason;
- validator/consequence results;
- artifact freshness transitions;
- human commit receipt where relevant;
- external validator output;
- independent consumer output.

Representative scenario set:

- success;
- negative/unresolved entity;
- partial correction;
- boundary/domain contradiction;
- stale commit;
- reconnect/recovery;
- direct-entry baseline.

## 20. Promotion gates

Before broader DELIVER promotion:

- external/canonical GTFS-RT validation → PROVEN;
- independent consumer → PROVEN;
- real operator-facing surface → at least LOCAL_VERIFIED with evidence;
- post-vertical-slice depth gap review → completed;
- truth boundary / evidence registry current.

Before AUDIT:

- judge-ready deterministic demo;
- hostile Q&A pack;
- as-built reconciliation;
- clean evidence package;
- no false LIVE/production claims.

Before EXPAND:

- operator evidence;
- public-network realism;
- measured workflow value;
- scope-specific operational economics;
- postmortem / learning capture.

## 21. Definition of Done — v0.1

ERRATA v0.1 is not “done” because the terminal prototype works.

Definition of Done requires:

- bounded core invariants preserved;
- real operator review surface;
- representative success/negative/boundary/recovery scenarios;
- external validator + independent consumer;
- evidence/runtime binding;
- deterministic judge demo;
- clear truth boundary;
- no unresolved P0 depth gap;
- PRD reconciled against the as-built system.

## 22. Version history

### v0.1 — 2026-09-30

Created after promotion of the bounded Technical Reality / Prototype Killer.

This version locks the validated architecture, explicitly records remaining gaps, and becomes the product-level source of truth before consequential delivery expansion.
