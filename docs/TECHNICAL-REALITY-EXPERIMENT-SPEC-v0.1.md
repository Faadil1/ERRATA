# ERRATA — Technical Reality Experiment Spec v0.1

**Lifecycle:** DESIGN — Technical Reality / Prototype Killer  
**Evidence rule:** architecture plausibility never promotes an execution gate.  
**Current executable mode:** `LOCAL_STUB`.

## 1. Hypothesis

ERRATA should allow self-correcting spoken operational intent to amend **one versioned staged transit service change** without forking truth.

The mechanism survives only if:

1. a correction preserves the same `change_id`;
2. revisions advance monotonically once per atomic applied batch;
3. only explicitly targeted fields change;
4. superseded operations remain in history;
5. interrupted/abandoned candidate operations create zero canonical side effects;
6. deterministic transit logic, not an LLM, computes consequences and refusals;
7. outputs tied to an older state hash become `STALE`;
8. a commit bound to an older reviewed hash is rejected;
9. final feed output is independently parseable/validatable;
10. the corrected voice-derived semantic state converges with direct entry of the same final intent.

## 2. Architecture under test

```text
LIVE VOICE
  ↓
AssemblyAI speech events
  ↓
Candidate Operation Proposer (LLM — proposal only)
  ↓
PENDING OP BATCH
  ├─ interrupted/abandoned → DISCARD
  └─ completed             → deterministic resolution
                                ↓
                         append-only typed op log
                                ↓
                             pure reducer
                                ↓
                    ServiceChange IR
                 change_id + revision + hash
                    ├─ validators
                    ├─ consequence calculator
                    └─ derived artifact graph
                                ↓
                         HUMAN REVIEW
                                ↓
                       HASH-BOUND COMMIT
                                ↓
                         GTFS-RT adapters
                                ↓
                independent validation / consumer
```

### Authority boundary

The LLM may interpret speech and propose typed operations. It must not:

- mutate canonical state directly;
- invent GTFS IDs accepted as truth;
- calculate consequence metrics;
- authorize commit;
- certify provenance;
- silently resolve material ambiguity;
- generate operational geometry that is treated as fact.

## 3. Canonical state

The bounded prototype uses a `ServiceChange` IR with:

- `change_id`
- `revision`
- `state_hash`
- route + direction
- service date
- effective time window
- skipped stops
- optional closed segment / detour reference
- reason
- unresolved items
- derived artifact references
- commit status

Material values carry provenance status such as:

`SPOKEN / RESOLVED / DERIVED / DEFAULTED / UNRESOLVED`.

## 4. Non-negotiable invariants

- **I-01 Same identity:** amendments never silently create a new change.
- **I-02 Revision monotonicity:** one revision increment per atomic applied batch.
- **I-03 Minimal correction:** non-targeted fields remain semantically identical.
- **I-04 History preservation:** superseded operations remain auditable.
- **I-05 Interruption safety:** abandoned candidate operations never reach canonical state.
- **I-06 State drives consequence:** the calculator never reinterprets free-form transcript.
- **I-07 Artifact invalidation:** outputs derived from an old hash become stale.
- **I-08 Stale commit rejection:** an old reviewed hash cannot commit.
- **I-09 Human authority:** no LLM/tool path may self-authorize consequential commit.
- **I-10 Unresolved blocks commit:** material ambiguity or contradiction stays uncommittable.
- **I-11 Independent acceptance:** final output must be consumable outside ERRATA's own UI.
- **I-12 Voice/text convergence:** equivalent final intent must converge semantically.

## 5. Primary experiment

Canonical utterance:

> “On Route 55 west, skip King Edward and Cumberland until 9:30… wait — keep Cumberland. Make it 10.”

Expected behavior:

- same `change_id`;
- initial revision contains both skipped stops;
- correction supersedes Cumberland's skip rather than deleting history;
- final state skips King Edward and serves Cumberland;
- end time becomes 10:00 only when binding is unambiguous;
- unrelated fields do not drift;
- revision-1 artifacts become `STALE`;
- stale-hash commit fails;
- current-hash human commit may proceed only after blocking validators pass.

## 6. Required scenario set

### SUCCESS / self-repair
The primary utterance above.

### NEGATIVE / unresolved entity
Reference a nonexistent or ambiguous stop. Expected: no fabricated ID, no mutation from unresolved input, commit blocked.

### BOUNDARY / domain contradiction
Ask to serve/keep a stop that lies inside a deterministically closed/unreachable segment. Expected: `REPAIR_REQUIRED`, state unchanged.

### INTERRUPTION
Prepare a candidate operation, then receive a true interrupted/abandoned voice turn. Expected: candidate discarded, before/after canonical hash identical.

### STALE COMMIT
Create revision N, then N+1, then attempt commit using N's hash. Expected: deterministic refusal, state unchanged.

### RECOVERY
Disconnect/reconnect during the live phase. Expected: persisted state reconstructs to the same canonical hash before the next amendment.

## 7. Sixteen promotion assertions for the live Prototype Killer

A live run must show:

1. same `change_id`;
2. revision increment;
3. superseded operation preserved;
4. corrected field has final intended value;
5. unrelated fields unchanged;
6. interrupted candidate creates zero side effect;
7. old derived artifacts become stale;
8. consequence report recomputes from new IR only;
9. stale hash cannot commit;
10. transit contradiction produces repair/refusal, not hallucinated acceptance;
11. GTFS-RT is genuinely serialized;
12. an independent validator accepts the relevant output;
13. an independent consumer observes the corrected state;
14. direct final entry converges semantically;
15. raw voice/session receipts bind the run to the exact state transition;
16. voice is compared against a keyboard/direct-entry baseline.

## 8. Baseline / voice-native necessity

Voice does not pass merely because it works. Compare at least:

- time to staged change;
- correction error rate;
- unintended field drift;
- number of interaction/context switches;
- entity-resolution errors;
- time to recovery.

If voice is slower, more error-prone, and adds no compensating operational benefit, the product thesis is falsified or must be redesigned.

## 9. AssemblyAI load-bearing experiment

The live adapter must preserve this transaction rule:

`tool.call → PREPARE only → wait for terminal reply state → completed: APPLY / interrupted: DISCARD`.

Also evaluate state-driven keyterms after route resolution.

Load-bearing status requires measured behavior/ablation, not the presence of an AssemblyAI transcript.

## 10. Evidence artifacts

Capture per canonical run:

- raw AssemblyAI event log;
- typed operation log;
- state snapshot per revision;
- before/after state hashes;
- validation report;
- consequence report;
- stale-artifact transitions;
- commit receipt;
- serialized GTFS-RT bytes;
- independent validator output;
- independent consumer output;
- baseline timing/error sheet;
- exact runtime/commit identifier;
- evidence label: `LIVE / LOCAL / LOCAL_STUB / PRESEEDED / SIMULATED / PARTIAL / NOT_IMPLEMENTED`.

## 11. Kill criteria

Any material occurrence of the following blocks promotion:

- silently wrong committed field;
- non-targeted field drift caused by a correction;
- interrupted candidate leaking into canonical state;
- fabricated operational entity;
- LLM-derived consequence presented as deterministic fact;
- stale reviewed hash accepted;
- unresolved domain contradiction committed;
- final artifact accepted only by ERRATA's own UI;
- false LIVE claim;
- voice losing the baseline without a measurable compensating advantage.

## 12. Current truth

The deterministic `LOCAL_STUB` harness is **not falsified locally**, but it does not prove live AssemblyAI behavior, external validator/consumer acceptance, operator desirability, or production readiness.

The next promotion decision occurs only after the live Prototype Killer run.
