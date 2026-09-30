# ERRATA — CURRENT

**Lifecycle:** DELIVER  
**Workstream:** Final Judge Integration — Public Voice / Context Streaming / Phone Transport  
**Concept:** same-identity voice repair locked  
**Product:** ERRATA  
**Canonical finalization branch:** `judge-finalization-deepseek-v0.1`

## Current truth

The deterministic `LOCAL_STUB` core is promoted on `main` and reproduced by GitHub Actions.

Credentialed microphone runs have now been observed on the live branch. They established that connectivity, microphone transport, real AssemblyAI transcription, deterministic refusal, and canonical reducer transitions are reachable. The controlled Streaming architecture also completed the central same-identity amendment loop live.

They also falsified an assumption: **managed conversational turn ownership is not regular enough for ERRATA's high-consequence operational dictation path on the current terminal setup.**

Observed failures included:

- one operational sentence split into multiple final user turns;
- route / action / stop clauses separated across turns;
- a correction split into `Wait.`, `Keep.`, and `Cumberland...`;
- correct speech sometimes transcribed as `make it turn`;
- native tool selection not consistently firing on fragmented turns;
- a new session remaining at revision 1 when the initial command never reached the reducer.

A prior successful live run did produce a real `stage_transit_change` tool call, deterministic rejection of `West Cape`, then a successful retry that advanced revision 1 → 2. That is bounded evidence only; it does not satisfy the full Prototype Killer.

## Controlled Streaming result — passed core mechanism

Do not continue threshold-tuning the managed Voice Agent path as the primary operational capture mechanism.

The branch now includes **Controlled Streaming v0.1**, and a credentialed run on exact SHA `6efbd6036647998aeb4d9efe0974c194a9819d35` passed the bounded core mechanism:

`microphone → AssemblyAI Universal-3.5 Pro Realtime → accumulate provider turns → human-controlled ForceEndpoint/apply → bounded deterministic parser → same coordinator / validators / reducer`

Observed run:

- initial speech: `Route 55, west, skip King Edward and Cumberland until 9:30.`
- parsed operations: `ROUTE=55`, `DIRECTION=west`, `SKIP=King Edward`, `SKIP=Cumberland`, `END=9:30`
- canonical transition: revision `1 → 2`
- amendment speech: `Wait, keep Cumberland, make it 10.`
- parsed operations: `KEEP=Cumberland`, `END=10`
- canonical transition: revision `2 → 3`
- same `change_id = ERR-LIVE-001`
- revision 3: King Edward skipped, Cumberland restored, end time `10:00:00`, no unresolved items, no pending calls
- final observed hash: `320221743ffda8433ac5abfbd5a5565aed96c166e87360955a51961dd7ca6f64`

Properties:

- AssemblyAI remains load-bearing for live speech recognition;
- provider end-of-turn splits are accumulated rather than treated as transaction boundaries;
- the human/operator explicitly owns the consequential capture boundary with `apply`;
- `ForceEndpoint` flushes the current speech boundary;
- route, direction, stop, KEEP/SKIP, and end-time parsing is deliberately bounded;
- the same canonical reducer and validation path remains authoritative;
- managed Voice Agent API remains available as a comparison / interruption baseline, not as the only architecture.

This matches the product's risk profile better: conversational segmentation may be probabilistic, but canonical mutation admission must not be.

## Evidence boundary

The original controlled-Streaming ZIP has now been audited and its archive/file SHA-256 values anchored in the repository. The central transition evidence is file-backed and internally consistent. The original runner did not embed its git SHA or persist the later commit-authority events, so the packet is not yet fully self-binding for every gate.

Therefore:

- `Voice → native tool → reducer`: observed LIVE in a bounded successful run;
- managed turn regularity: **falsified for the current operational-dictation path**;
- controlled Streaming path: **credentialed-run proven for the bounded initial-change + amendment loop**;
- Prototype Killer: still BLOCKED.

## Still blocked

- `Prototype Killer` — broader promotion remains pending baseline + remaining live safety/recovery checks
- broader Live Depth beyond the bounded controlled-Streaming core loop
- `Voice-native Necessity`
- `Interruption Side-effect Safety — LIVE`
- `Failure / Recovery — LIVE`
- external/canonical GTFS-RT validation
- third-party consumer acceptance
- `Real Consequence — LOCAL`
- operator desirability

## Protected claims

Do not claim production voice reliability, agency integration, controller adoption, production safety, public-network mutation, external GTFS-RT acceptance, or a completed Prototype Killer.

## Live commit-authority result — passed

In the same controlled Streaming run:

- stale reviewed hash `8d6f83a9a20d` was refused against current hash `320221743ffda843...`;
- current reviewed hash prefix `320221743ffd` was accepted;
- commit receipt reported `authority = human_terminal_command`;
- the final snapshot showed `status = COMMITTED`, revision `3`, same `change_id = ERR-LIVE-001`, no pending calls, and final hash `320221743ffda8433ac5abfbd5a5565aed96c166e87360955a51961dd7ca6f64`.

This promotes the bounded live evidence for stale-commit rejection and human commit authority.

## Evidence audit result

The uploaded archive passed bounded evidence audit:

- archive SHA-256: `bd0866451ec4eecc97484f80173665d062b92fbfab79b7eb7a33aaa70a8136b0`;
- receipt hash chain is continuous from revision 1 → 2 → 3;
- both state snapshot hashes independently recompute correctly from runtime commit hashing semantics;
- both mutation batches pass all blocking validators;
- no obvious credential material was found;
- the archive itself does not contain the later human-commit proof or embedded runtime SHA.

Audit anchor: `evidence/controlled-streaming-v0.1/20260929-143810/AUDIT.md`.

## Next checkpoint — instrumented proof + voice baseline

The next workstream is now implemented:

1. run one hardened controlled-Streaming pass so the evidence packet is self-binding;
2. run the keyboard/direct-entry baseline on the same two semantic instructions;
3. compare the two paths using the generated evidence.

New tools:

- `scripts/run_keyboard_baseline.py`
- `scripts/compare_voice_keyboard.py`
- `docs/VOICE-VS-KEYBOARD-BASELINE-v0.1.md`

This directly tests the `Voice-native Necessity` gate without assuming voice is faster or better.

First paired measurement is now complete on runtime SHA `9bf768bd77200b8363fa8cc9ab57fbd4993ccdc6`.

Observed:

- semantic operation match = true for initial change and correction;
- voice safe-stage time: 23.79 s initial / 16.82 s correction;
- keyboard total: 6.13 s initial / 7.85 s correction.

This is negative evidence for a simple "voice is faster" claim, but the voice figures include provider-final → human-`apply` delay. The comparator has been upgraded to decompose capture, confirmation, and apply latency using the same existing evidence.

Next checkpoint: pull and re-run only the comparator. No new microphone run is required for this decomposition.

After that interpretation, the remaining Prototype Killer deltas are interruption/barge-in and failure/recovery.

For reproducibility, the harness remains:

```bash
python scripts/run_controlled_streaming.py --service-date 20260929 --start-time 09:00:00
```

Workflow:

1. Speak: **Route 55 west, skip King Edward and Cumberland until 9:30.**
2. Type `apply`.
3. Wait for `APPLIED rev=2`.
4. Speak: **Wait, keep Cumberland. Make it 10.**
5. Type `apply`.
6. Type `snapshot`.

Provider turn splits may still appear, but they must no longer independently trigger canonical mutations.


## Voice-native necessity — first decomposition

Paired evidence on SHA `9bf768bd77200b8363fa8cc9ab57fbd4993ccdc6` shows:

- initial voice capture to provider-final: 12.11 s vs keyboard entry 6.13 s;
- correction voice capture to provider-final: 5.80 s vs keyboard entry 7.85 s;
- provider-final → human apply delay: ~10.13 s initial / ~9.49 s correction;
- apply → canonical applied: ~1.5 s in both phases;
- semantic operation match: exact in both phases.

Therefore `Voice-native Necessity` remains ACTIVE, not proven. The evidence rejects a simple universal "voice is faster" story, but also shows that the current confirmation UX dominates avoidable latency and masks a voice advantage on the short correction.

### Next live delta

The controlled runner now treats a blank ENTER as `apply`. The operator should press ENTER immediately after finishing each utterance, without waiting for provider final output.

This tests two things at once:

1. whether a human-owned endpoint can remove confirmation friction while preserving safe mutation admission;
2. whether `ForceEndpoint` produces a final turn when invoked before provider finalization.

No architecture or semantic logic changes in this delta.


## Immediate-ENTER experiment — negative runtime finding

A credentialed immediate-ENTER run exposed a new atomicity defect.

Observed sequence:

- early transcripts repeatedly misheard `skip` / `9:30`, producing safe `REVIEW_REQUIRED` / `REJECTED` outcomes at revision 1;
- a later clean initial command applied successfully to revision 2;
- correction transcript `Wait, keep Cumberland, make it turn.` parsed only `KEEP=Cumberland`;
- because an old end time already existed in canonical state, validators allowed that partial subset and advanced revision 2 → 3;
- later attempts to apply `KEEP=Cumberland` + `END=10` were rejected because Cumberland had already been restored by the partial correction;
- final revision 3 therefore had Cumberland restored but end time still `09:30:00`.

This falsifies the assumption that validator completeness alone prevents partial spoken corrections from leaking into canonical state.

Corrective delta now implemented:

- parser emits explicit `unresolved_cues` when phrases such as `make it ...`, `until ...`, `skip ...`, or `keep ...` fail to resolve their target/value;
- any batch with unresolved explicit cues is `REVIEW_REQUIRED` and cannot reach PREPARE/APPLY;
- exact repeated semantic operations across accumulated retry fragments are deduplicated while conflicting self-repairs remain ordered;
- `ouest` is accepted as a bounded alias for west because that exact live STT output was observed.

This gate remains open until a new live correction proves that `KEEP=Cumberland` cannot apply without the intended time amendment when the transcript signals both.


## Immediate-ENTER retest — second atomicity failure variant

A second credentialed run reproduced the same class of defect through a different STT surface:

- intended spoken correction: `Wait, keep Cumberland, make it turn.`
- observed transcript: `Wait, keep Cumberland, make U-turn.`
- bounded parser extracted only `KEEP=Cumberland`
- revision advanced `2 → 3`, restoring Cumberland while retaining end time `09:30:00`
- subsequent correct `KEEP=Cumberland + END=10` was rejected because the KEEP had already leaked into canonical state.

This proves the first guard was too literal: it protected `make it ...` but not semantically adjacent STT corruptions such as `make U-turn`.

Corrective delta:

- any unsupported `make ...` cue without a resolved END value is now review-only;
- exact `make it ...` failures retain the specific `END_TIME_AFTER_MAKE_IT` cue;
- other `make ...` variants emit `UNRESOLVED_MAKE_CUE`;
- regression coverage now includes the exact observed `make U-turn` transcript.

Do not promote Partial Correction Atomicity until the new live retest leaves revision/hash unchanged for this transcript.


## Immediate-ENTER retest — observed U-turn variant

A second credentialed run reproduced the partial-correction leak through a different STT transcript. The intended malformed time correction was transcribed as `Wait, keep Cumberland, make U-turn.` The parser extracted only `KEEP=Cumberland`, which advanced revision 2 to 3 while leaving the prior end time at `09:30:00`. A later correct `KEEP=Cumberland + END=10` was then rejected because the KEEP had already changed canonical state.

The prior guard was too literal because it only recognized `make it ...`. The parser now treats any unsupported `make ...` cue without a resolved END value as review-only. Exact `make it ...` failures retain the specific `END_TIME_AFTER_MAKE_IT` cue, while other variants emit `UNRESOLVED_MAKE_CUE`. Regression coverage includes the exact observed `make U-turn` transcript.

Do not promote Partial Correction Atomicity until a new live retest leaves revision/hash unchanged for that malformed transcript.


## Partial Correction Atomicity — bounded LIVE proof

A subsequent credentialed immediate-ENTER run passed the negative-path invariant that previously failed.

Observed:

- clean initial command applied revision `1 → 2`, hash `8d6f83a9a20df286...`;
- malformed/incomplete correction accumulated as:
  `Wait, keep Cumberland, make it. You're done. Wait, keep. Wait, keep Cumberland, make it. You're done.`;
- parser extracted only `KEEP=Cumberland` but also emitted unresolved cue `END_TIME_AFTER_MAKE_IT`;
- runtime returned `REVIEW_REQUIRED`;
- revision remained `2`;
- canonical hash remained `8d6f83a9a20df286...`;
- no partial KEEP leaked into canonical state;
- a subsequent clean correction `Wait, keep Cumberland, make it 10.` parsed `KEEP=Cumberland + END=10` and applied revision `2 → 3`.

This closes the bounded live atomicity defect discovered in the two prior immediate-ENTER runs. A final snapshot/commit receipt from this same session is still pending before treating the entire run as a complete self-contained proof packet.


## Audited self-bound immediate-ENTER packet

The uploaded packet `ERRATA-live-atomicity-20260929-175753.zip` passed audit.

Archive SHA-256:

`1c4004eb1367acc93f8a971f36a6b6369340a7e698dbeca11f15ef77760230e7`

Embedded runtime:

- git SHA `c83f750cc3b7f8d26c936d92a0c2f6525605be30`
- tracked worktree clean = true
- stream session `632f1661-88b0-4056-9471-86d1ac646acd`
- AssemblyAI `universal-3-5-pro`, max_accuracy, near-field, 16 kHz

Audit proves in bounded LIVE scope:

- runtime/evidence binding is self-contained;
- all embedded file hashes match the evidence manifest;
- 3/3 human ENTER boundaries emitted ForceEndpoint and were followed by provider finals;
- incomplete explicit correction produced REVIEW_REQUIRED and left rev2/hash unchanged;
- clean retry applied rev3;
- all persisted state hashes independently recompute exactly;
- Terminate is present;
- no obvious credential value is persisted.

The packet does **not** contain commit refusal/acceptance receipts. Its final state is STAGED. Human commit authority remains supported by the separate earlier LIVE terminal-observed run, not by this ZIP.

### Immediate-ENTER timing versus keyboard

Using this packet against the existing keyboard baseline:

- initial safe-stage: voice `8.79 s` vs keyboard `6.13 s`;
- correction safe-stage: voice `5.07 s` vs keyboard `7.85 s`;
- two-phase total: voice `13.85 s` vs keyboard `13.98 s`.

This is near aggregate parity in one local trial, with keyboard faster for the long initial command and voice faster for the short correction. It supports voice viability, not voice necessity.

### Current hard blocker

For the bounded Prototype Killer, the remaining hard technical blocker is now:

`Failure / Recovery — LIVE`

The next experiment must deliberately interrupt the live AssemblyAI transport and prove that canonical state does not drift and that the same in-process change can resume safely after reconnection.

Audit anchor:

`evidence/controlled-streaming-v0.1/20260929-175753/AUDIT.md`


## Recovery runner implemented

The authoritative controlled-Streaming runner now supports deliberate in-process transport recovery with the `reconnect` command.

Behavior:

- records the current revision/hash/session before disconnect;
- clears uncommitted transcript fragments;
- terminates and closes the current AssemblyAI WebSocket;
- opens a new Streaming session without recreating the canonical `ServiceChange`;
- records `TRANSPORT_DISCONNECTED` and `TRANSPORT_RECONNECTED`;
- checks exact revision/hash continuity;
- preserves all stream session IDs in the integrity manifest.

The recovery gate is now ACTIVE rather than BLOCKED. Credentialed execution is still required before promotion.

See `docs/LIVE-FAILURE-RECOVERY-TEST-v0.1.md`.


## Recovery run — transport continuity passed, semantic retry failed

Credentialed run at evidence directory:

`evidence/controlled-streaming-v0.1/20260929-230646`

Transport recovery itself passed:

- pre-disconnect state: rev2 / `8d6f83a9a20df286...`;
- first stream session: `11dbe02c-d36d-4831-bbc5-23f33272c894`;
- deliberate `reconnect`;
- second stream session: `5f2e5fc2-0e76-4211-b647-2bda071d51c6`;
- runtime reported `same_revision=True` and `same_hash=True`;
- post-reconnect snapshot remained exactly rev2 / same hash;
- same `ServiceChange` identity remained in memory.

Therefore bounded **Transport Recovery Continuity — LIVE** is proven.

However, the required post-recovery semantic correction did not pass cleanly. AssemblyAI transcribed repeated attempts as variants ending in `McKitten 10`; the parser extracted only `KEEP=Cumberland`, missed the intended time amendment, and applied a partial rev2→rev3 change. End time remained `09:30:00`.

This is not a reconnect-state-continuity failure. It is another partial-correction atomicity variant caused by an **unbound time value** surviving while the linking phrase was lost.

Corrective delta implemented:

- correction batches containing KEEP/SKIP plus an unbound time-like numeric/word token without a resolved END are now review-only;
- new unresolved cue: `UNBOUND_TIME_VALUE`;
- regression coverage includes the exact observed `McKitten 10` shape and a spoken-word `ten` form;
- expected WebSocket-close race in the audio sender is now swallowed so normal quit/reconnect no longer emits `Task exception was never retrieved`.

Gate consequences:

- `Transport Recovery Continuity — LIVE → PROVEN`;
- `External Dependency Failure → PROVEN` in bounded reconnect scope;
- broader `Failure / Recovery — LIVE` remains ACTIVE until a post-reconnect correction is safely reviewed/applied;
- `Partial Correction Atomicity — LIVE` returns to ACTIVE because the new unbound-time variant leaked through.

Do not use the rev3 state from this run as a correct correction proof.


## Recovery retest — bounded Failure / Recovery passed

Credentialed run evidence directory:

`evidence/controlled-streaming-v0.1/20260929-231455`

Observed sequence:

- after several safe transcription failures/reviews, the initial operational change eventually applied at rev2;
- pre-reconnect rev2 hash: `c3d84ea92c8482ee3465c41fa2faa6bf0b627e01cc6d124169c47cdab5cdd2ad`;
- deliberate reconnect opened a new AssemblyAI stream session `9b3a7ceb-6ee0-41fe-93e6-e88e3a48ffe1`;
- runtime reported `same_revision=True` and `same_hash=True`;
- post-reconnect correction fragments accumulated to a semantically complete batch with `KEEP=Cumberland` + `END=10`;
- canonical state advanced rev2→rev3 on the same `ERR-LIVE-001` identity;
- final rev3 had King Edward skipped, Cumberland restored, end time `10:00:00`, no unresolved items, and hash `c44bc7d5f7dc7515d593c8b1d1f85bdfe5a57316fb37a4838350de97c74cb992`;
- repeated identical correction retries after rev3 were safely rejected with no further mutation;
- normal quit completed without the prior unhandled sender-close task exception.

This satisfies bounded `Failure / Recovery — LIVE` for the authoritative controlled-Streaming path.

Important boundary: the latest run did **not** isolate the new `UNBOUND_TIME_VALUE` negative path because earlier fragments contained valid `until 10` / `make it 10` cues before the final `... 10` fragment. Therefore `Partial Correction Atomicity — LIVE` remains ACTIVE specifically for that new unbound-time variant, while the broader Prototype Killer is promoted.

### Prototype Killer decision

The bounded Technical Reality / Prototype Killer is now **PROVEN**.

This means the architecture survived the required falsification work for:

- live speech capture;
- human-owned mutation admission;
- same-identity revision semantics;
- explicit negative/review behavior;
- partial-correction guard class;
- ForceEndpoint behavior;
- keyboard baseline comparison;
- runtime/evidence binding;
- stale commit/human commit authority (from the earlier separate LIVE run);
- deliberate transport reconnect with exact state continuity and successful post-reconnect mutation.

It does **not** mean production readiness.

Next lifecycle focus: `DELIVER` with a living PRD and Post-Vertical-Slice Depth Gap Review. Remaining product-depth gaps include external/canonical GTFS-RT validation, independent consumer acceptance, real-user surface, external operator evidence, and stronger voice-necessity/operator-workflow validation.


## Living PRD + depth-gap review completed

Canonical product-level artifacts now exist:

- `docs/PRD-v0.1.md`
- `docs/POST-VERTICAL-SLICE-DEPTH-GAP-REVIEW-v0.1.md`

The PRD locks:

- target user/JTBD;
- goals/non-goals;
- validated architecture;
- fourteen product invariants;
- canonical hero demo;
- MUST / SHOULD / MAY / MUST_NOT requirements;
- product surfaces;
- NFRs;
- evidence ledger;
- success metrics;
- risks/dependencies;
- acceptance criteria;
- promotion gates;
- Definition of Done.

The depth-gap review changes the next decision boundary. The project should not spend the next cycle on generic voice tuning or visual polish.

### P0 next workstream — External Acceptance Slice

Required chain:

`ERRATA serializer → external/canonical validation → independent consumer → evidence receipt`

This directly attacks the remaining invariant that the final artifact must be accepted outside ERRATA itself.

After P0 external acceptance:

- operator review surface;
- public-network scenario;
- external operator evidence / voice-necessity validation;
- deterministic judge demo + Q&A;
- as-built reconciliation.

`Living PRD → PROVEN`
`Post-Vertical-Slice Depth Gap Review → PROVEN`
`Spec Kit → ACTIVE`


## External Acceptance Slice — independent consumer passed

CI run `36664709491` completed with all three jobs green.

The new `external-acceptance` job:

- generated the bounded corrected GTFS-Realtime artifact;
- packaged the matching synthetic static GTFS ZIP;
- parsed the protobuf using MobilityData's official `gtfs-realtime-bindings==2.0.0`;
- observed three R55 TripUpdate entities;
- observed only `S_KING_EDWARD` as skipped;
- confirmed `S_CUMBERLAND` is not skipped;
- uploaded a self-described external-acceptance artifact.

TripUpdates.pb SHA-256:

`bb5e6bd94acd01a61b2ad70e96047bda5f2bad27b1bc5d6824eb8915920591be`

GitHub artifact digest:

`sha256:c2c695af3b6fb5cbf71de27dff54ed686a3dde7559a8a12c20048fba2f894537`

Therefore:

`Independent Consumer → PROVEN` in bounded fixture scope.

Truth boundary:

Official bindings parse is not canonical validation. `External / Canonical GTFS-RT Validation` remains BLOCKED until MobilityData's validator rule engine consumes the packaged static GTFS + identical protobuf.

Evidence anchor:

`evidence/external-acceptance-v0.1/OFFICIAL-CONSUMER-CI.md`


## External Acceptance Slice — canonical validator passed

CI run `36665394082` closed the P0 external acceptance slice.

The exact same bounded `TripUpdates.pb` was:

1. decoded by MobilityData official Python bindings with the intended corrected semantics;
2. validated by a pinned build of `MobilityData/gtfs-realtime-validator@7041fa3fcaf674bf730e17325c179d329cdff6f2`.

Canonical validator result:

- process exit code: `0`
- ERROR rule groups: `0`
- WARNING rule groups: `2`
- validation-results SHA-256: `74abce167f10ff3d1047c0903f709d9fb1f5d29babaa7cc0c9cde561f34647e8`

Warnings retained:

- `W002`: vehicle_id not populated — ERRATA does not fabricate vehicle identity for a service-change-only fixture;
- `W008`: deterministic CI header timestamp older than 65 seconds — freshness warning only; a live publisher must use actual generation time.

Exact inputs:

- static GTFS ZIP SHA-256: `93bacc260f6ce286cadc22c2773e7eae164cd9ec00b18960f82690ac24b1023b`
- TripUpdates.pb SHA-256: `f7ceac24f2f6c4a380f0aa465c3bf4f13abe25a4d7753b7b02b04b8baf771eef`

Evidence artifact:

- GitHub artifact ID `11075618019`
- digest `sha256:94f892077adcf332961025b9a3b6f337e979c3374593346b2bc2fd94c33debcd`

Promoted in bounded synthetic-fixture scope:

- `Independent Consumer → PROVEN`
- `External / Canonical GTFS-RT Validation → PROVEN`
- `External Acceptance Slice → PROVEN`
- `GTFS-RT Adapter → PROVEN`
- `Real Consequence — LOCAL → PROVEN`

This does not prove public-network correctness or agency production integration.

### Next P0 delivery work

The highest remaining product-depth gap is now the **operator review surface**, followed by a public-network scenario.

The operator surface must expose the already-proven shared core rather than create a second business-logic stack.

Canonical anchors:

- `evidence/external-acceptance-v0.1/OFFICIAL-CONSUMER-CI.md`
- `evidence/external-acceptance-v0.1/CANONICAL-VALIDATOR-CI.md`


## Operator Review Surface — implementation checkpoint

The P0 surface contract now has a concrete implementation:

- `errata/operator_surface.py` — thin session/controller over the existing shared core;
- `scripts/run_operator_surface.py` — local HTTP/API server;
- `web/operator/index.html`
- `web/operator/app.css`
- `web/operator/app.js`
- `tests/test_operator_surface.py`

Protected commit authority is surface-aware: the shared coordinator now accepts an explicit human authority label while preserving `human_terminal_command` as the default. The browser passes `human_web_review`.

CI run `36666549465` has already shown:

- deterministic/operator-surface pytest step: PASS;
- operator runner smoke: PASS;
- end-to-end HTTP surface smoke: PASS;
- canonical initial amendment: APPLIED;
- correction: APPLIED;
- stale reviewed hash: STALE_REVIEW with state unchanged;
- static browser shell served successfully.

Truth boundary:

This is a local synthetic-fixture operator surface. It is not yet a real external operator trial and no production-agency claim is implied.

Gate state remains:

- `Operator Review Surface → ACTIVE` pending human visual/runtime review;
- `Real-user Surface → ACTIVE`;
- external operator evidence remains BLOCKED.


## Human visual review — first operator-surface recording

A 63.8 s human screen recording of the local operator surface exposed a presentation/workflow problem rather than a core-state defect.

Observed:

- the initial Route 55 amendment applied correctly at rev2;
- the commit rail was visually dominant and immediately available once validators passed;
- the operator committed rev2 before applying the intended correction;
- subsequent correction / malformed-correction attempts were then correctly rejected with `CHANGE_ALREADY_COMMITTED`;
- stale-review demonstration could no longer be completed because the change was already sealed;
- the current canonical operational state was partly below the first viewport, despite the surface spec requiring current truth to be immediately legible.

This is a UI sequencing/hierarchy issue. The backend behaved correctly.

Corrections now implemented:

- reference walkthrough stepper: base change → correction → stale review → current commit;
- explicit advisory at rev2 that commit is technically valid but ends the reference walkthrough before the correction;
- compact route/direction/window/skipped-stop truth strip added directly under revision/hash;
- consequence panel moved before commit in the right rail;
- committed changes now disable authoring/fill/apply controls in the browser and show a sealed-state message;
- commit UI collapses to committed-hash receipt after commit;
- protected commit events now render a human-action narrative instead of “No operator amendment yet”;
- server exposes `can_author` / `commit_ready` capabilities;
- JS syntax is checked in CI;
- regression test proves post-commit amendment attempts cannot mutate state.

`Operator Review Surface` remains ACTIVE until the corrected visual flow is re-recorded once.


## Operator Review Surface — corrected human recording passed

A second human recording (~74.6 s) demonstrates the corrected browser surface end-to-end.

Observed in the same recording:

- above-fold canonical identity/revision/hash/route/direction/window/skipped stops;
- intentional early rev2 commit → COMMITTED + authoring lock;
- reset to clean staged revision 1;
- initial hero amendment → rev2;
- hero correction → rev3 with Cumberland restored and end time 10:00;
- malformed correction → REVIEW_REQUIRED with explicit unresolved cue;
- invalid repeated correction → REJECTED without state drift;
- prior reviewed hash → STALE_REVIEW;
- current reviewed hash → COMMITTED;
- final committed state remains visible and sealed;
- external official-consumer / canonical-validator evidence remains visible with warnings and synthetic truth boundary.

CI head `c26b15cab7e71fe38c99de749e8265ebcda5dc77` is green in run `36667899502`.

Promoted in bounded local/synthetic scope:

- `Operator Review Surface → PROVEN`
- `Real-user Surface → PROVEN`

This does **not** promote external operator evidence or production UX.

Canonical audit:

`docs/OPERATOR-SURFACE-HUMAN-VISUAL-AUDIT-v0.2.md`

### Next P0

Move to the **Representative Public-Network Scenario**. The goal is to prove the mechanism and external acceptance chain against non-synthetic GTFS data before judge packaging or broader operator claims.


## Public-Network Scenario — STO public GTFS passed

CI run `36674052762` executed the ERRATA shared-core mechanism against STO's public planned GTFS dataset for service date `20260930`.

Source:

- provider: Société de transport de l'Outaouais (STO);
- public GTFS URL: `https://contenu.sto.ca/GTFS/GTFS.zip`;
- HTTP Last-Modified: `2026-09-28`;
- source ZIP SHA-256: `a7e1f22955084828484cca5e8f1ebff9e785c70984ad5dd93b872a5d64ace6e4`.

Canonical scenario:

- route `15` / `DES ÉRABLES`;
- direction_id `0`;
- reference trip `62759262`;
- initial: skip `SAINT-LOUIS/Av. GATINEAU` + `ARRÊT DE COURTOISIE Érables/Tire`, end `17:22`;
- correction: restore `ARRÊT DE COURTOISIE Érables/Tire`, end `17:52`;
- final revision `3`;
- final hash `eb433070258612cba763d66937fee11c0c3c1aeea897da764a38eb2bf1be9664`.

External acceptance on the exact public-source identifiers:

- official MobilityData bindings: PASS;
- exact TripUpdates.pb SHA-256: `c486f610ab6faddac3ff83104f43233a1f13cc053720f6b50108ad6e62cfb87e`;
- pinned MobilityData canonical validator: exit 0;
- ERROR groups: 0;
- WARNING groups: 1 (`W002 vehicle_id not populated`);
- validator result SHA-256: `0a24f7f37f0bba2c0303a447a8aa19be27a4656dc194553f30c10d7d9b5c4234`.

Evidence artifact:

- ID `11078928665`;
- digest `sha256:4998dd1c8a42cb136ec8b86be7600c95c649b6040f087db32729bc9a9e5ce339`.

Required STO attribution is preserved in the manifest.

Promoted in bounded public-data / local-mutation scope:

- `Public-Network Scenario → PROVEN`;
- `Entity Resolution → PROVEN`;
- `Consequence Calculator → PROVEN`;
- `Real Consequence — PUBLIC DATA / LOCAL MUTATION → PROVEN`.

Truth boundary remains strict: ERRATA did not publish to STO systems, did not create a real service disruption, and has no agency production integration.

Canonical anchor:

`docs/PUBLIC-NETWORK-STO-EVIDENCE-v0.1.md`

### Remaining delivery gap

The technical/product stack is now deep enough that the next highest-value unresolved question is no longer another GTFS implementation task.

Remaining product proof:

1. external operator/user evidence;
2. stronger voice-native workflow-value evidence;
3. deterministic judge demo/story/Q&A;
4. final as-built reconciliation and submission integrity.


## Operator evidence + judge packaging protocols ready

Two downstream artifacts are now canonical:

- `docs/EXTERNAL-OPERATOR-TRIAL-PROTOCOL-v0.1.md`
- `docs/JUDGE-DEMO-SCRIPT-v0.1.md`

The operator trial protocol is ready but the evidence gate remains BLOCKED until a representative external participant actually completes it. One trial will be treated as bounded evidence, not adoption or endorsement.

The judge demo is now script-locked to:

1. same-identity amendment;
2. atomic REVIEW_REQUIRED path;
3. stale-hash refusal;
4. explicit current-hash commit;
5. public STO Route 15 external-validation receipt;
6. AssemblyAI live capture / ForceEndpoint / reconnect evidence;
7. strict non-production truth boundary.

A deterministic fallback is explicitly permitted only if it is labeled as such; it must not be narrated as live voice.

Latest CI includes a strengthened public-network official-bindings assertion for route, direction, service date, retained skip, and restored stop. That rerun is still pending/in progress at this checkpoint.


## Judge packaging checkpoint — 2026-09-30

The strengthened CI rerun on functional head `d03db942513e30501a7e68bf037a36dcb4701cf8` completed successfully:

- workflow: `technical-reality`;
- run: `36674855222`;
- jobs: `local-stub`, `live-adapter-contract`, `public-network-sto`, and `external-acceptance` all SUCCESS.

Latest revalidation artifacts from that run:

- public-network STO: `11079153984`, digest `sha256:bd4754995ef216500f7f91ff1fc437dbec1a2fedb46aa78cd5f14da94c0239f9`;
- external acceptance: `11079179121`, digest `sha256:468e61a6392cfb84ce212946a6d05816594e8d8319ece0a815888af1536bc0c6`;
- local stub: `11079029513`, digest `sha256:ad736dad62b4dade9e56e7d8ca6c7caa3f7f1c84fb87b138826089754c7e1827`.

The original public-network closure receipt `11078928665` / `sha256:4998dd...` remains the historical canonical closure artifact. The latest rerun is a separate revalidation package and does not overwrite that history.

Judge packaging is now materialized in:

- `docs/JUDGE-DEMO-PACK-v0.1.md`
- `docs/JUDGE-HOSTILE-QA-v0.1.md`

Gate truth remains:

- `External Operator Evidence = BLOCKED` until a representative external participant executes the protocol;
- `Voice-native Necessity = ACTIVE`;
- `DEMO = ACTIVE` until a complete 90–120 s rehearsal/recording passes the demo-pack checklist;
- `Agency Live Integration = BLOCKED`.

The next human action is a full judge-demo rehearsal. Do not substitute builder rehearsal for external operator evidence.


## Live Product Integration correction — 2026-09-30

A product-depth gap was identified before judge rehearsal: the existing browser operator surface was a local review/direct-entry interface, while the credentialed AssemblyAI voice proofs lived in separate terminal experiments. The product therefore **was not yet an integrated voice web application**, and no Cloudflare public runtime had been deployed.

This changes the next P0.

Implemented in the local browser surface on the feature branch:

- server-minted short-lived AssemblyAI Streaming v3 token;
- browser microphone capture;
- AudioWorklet PCM16/16 kHz path;
- direct browser WebSocket to AssemblyAI using the temporary token;
- provider transcript buffering with zero automatic mutation;
- explicit human ForceEndpoint / Apply spoken turn boundary;
- `POST /api/amend/voice`;
- voice transcript routed through the same existing ERRATA parser/resolver/validators/reducer as direct entry;
- distinct transaction provenance `assemblyai_browser_voice_human_boundary`;
- CI coverage of the shared-core voice mutation endpoint.

Truth boundary:

- this implementation is **not yet credentialed-browser proven**;
- the prior terminal AssemblyAI evidence remains valid bounded technical proof;
- the local operator surface remains valid direct-entry/review proof;
- neither proof may be substituted for integrated product evidence.

Cloudflare remains not deployed.

Canonical deployment target is now documented at:

`docs/LIVE-PRODUCT-INTEGRATION-CLOUDFLARE-v0.1.md`

Current gates:

- `Integrated Browser Voice Surface = ACTIVE`;
- `Cloudflare Public Runtime = BLOCKED`;
- `Cloudflare State Continuity = BLOCKED`;
- `Live Product Integration = BLOCKED`;
- `DEMO = BLOCKED`;
- `External Operator Evidence = BLOCKED` independently.

Next checkpoints in order:

1. credentialed local browser microphone run proving voice → same core → revision semantics;
2. Cloudflare Worker + static assets + stateful session implementation;
3. public deployment with AssemblyAI key stored only as secret;
4. public-runtime end-to-end voice / negative / stale-review / commit proof;
5. only then judge-demo rehearsal.


## Integrated browser voice proof harness ready

The local browser voice path is now ready for a credentialed human run.

Implementation hardening completed before the run:

- AssemblyAI Streaming v3 temporary token remains server-minted; permanent API key is never returned to the browser;
- browser audio is PCM16 mono 16 kHz;
- AudioWorklet output is buffered into ~100 ms frames rather than tiny render-quantum packets;
- Streaming connection uses `universal-3-5-pro`, `mode=max_accuracy`, and formatted turns;
- human `Apply spoken turn` sends `ForceEndpoint`;
- provider turns remain non-mutating until that human boundary;
- voice mutation records AssemblyAI session ID and boundary metadata;
- `/api/session-receipt` exports exact git SHA, worktree-clean flag, state, validation, history, and voice provenance;
- browser exposes **Export proof receipt**.

Execution protocol:

`docs/BROWSER-VOICE-PROOF-PROTOCOL-v0.1.md`

Gate remains:

`Integrated Browser Voice Surface = ACTIVE`

until a real microphone run produces the required receipt. Static/CI coverage is not sufficient for promotion.


## Interactive voice guidance correction

Human browser review showed that the first integrated voice surface behaved like a capture harness rather than a true operator copilot: it transcribed and buffered speech but did not greet, interpret, guide, or recover conversationally enough.

The product-depth correction is now implemented locally:

- spoken greeting on successful voice connection;
- AssemblyAI provider turns reconciled by turn identity instead of blindly concatenated;
- non-mutating `POST /api/preview/voice` runs the transcript against a disposable copy of canonical state;
- safe interpretation is summarized to the operator before Apply;
- incomplete/ambiguous input produces contextual guidance and keeps Apply disabled;
- browser voice guidance can be repeated or muted;
- microphone frames are suppressed while browser guidance speech is playing to reduce self-capture;
- canonical revision/hash remain unchanged during preview/guidance;
- explicit human Apply remains the only mutation boundary.

Truth boundary:

- this is implemented and CI-testable;
- it is **not yet PROVEN by a credentialed human microphone run**;
- Cloudflare Public Runtime, Cloudflare State Continuity, Live Product Integration, DEMO, and External Operator Evidence remain BLOCKED.

Next checkpoint remains the credentialed local browser run, now using the upgraded interactive protocol in `docs/BROWSER-VOICE-PROOF-PROTOCOL-v0.1.md`.


## Neural guidance voice + echo guard correction

Human review of the Edge `Microsoft Aria Online (Natural)` fallback confirmed that browser Web Speech remains audibly synthetic and that spoken guidance can still be picked up again by the microphone in some conditions.

Implemented local product delta:

- server-side `POST /api/tts/guidance` using OpenAI `gpt-4o-mini-tts`;
- default neural voice `cedar`, alternate `marin`;
- server-only `OPENAI_API_KEY`; the browser receives only generated audio;
- `GET /api/voice-capabilities` truthfully reports whether neural TTS is available;
- visible `AI-generated voice` disclosure when the neural engine is active;
- Edge/Windows voice remains an automatic fallback when neural TTS is unavailable;
- strict half-duplex echo guard suppresses microphone frames while guidance is being prepared/played;
- 750 ms post-playback cooldown before microphone frames resume;
- overlapping guidance requests are cancelled/invalidated so stale TTS cannot play over a newer operator state.

Current truth:

- implementation + fallback CI path can be proven automatically;
- `Neural Guidance Voice = ACTIVE` until a real browser run with `OPENAI_API_KEY` proves neural playback;
- `Echo / Self-Capture Guard = ACTIVE` until a human run shows that ERRATA's own speech is not re-transcribed;
- Integrated Browser Voice, Cloudflare Public Runtime, Live Product Integration, and DEMO are not promoted by this implementation alone.


## AI33 Pro guidance provider substitution

The previously planned OpenAI TTS dependency is superseded. The user already owns and has a proven AI33 Pro integration, so ERRATA now reuses that provider instead of requiring a new OpenAI API key.

Canonical implementation:

- secret: `AI33_API_KEY`;
- base URL: `https://api.ai33.pro`;
- TTS create: `POST /v3/text-to-speech` with multipart `text`, `voice_id`, `speed`;
- task polling: `GET /v1/task/{task_id}` until `status=done`;
- audio source: `metadata.audio_url` / compatible output URL;
- default ERRATA voice: `Zach / George V2` (`elevenlabs_yG30oCchdy9JCUsKqYfV`);
- speed: `0.98`;
- browser receives generated audio only, never the AI33 key;
- Windows persistent User/Machine `AI33_API_KEY` is reused automatically when not already present in the current process;
- Edge/Windows TTS remains fallback-only;
- UI surfaces AI33 generation latency and credit cost when returned;
- half-duplex speech guard + 750 ms echo cooldown remain mandatory.

Truth boundary:

- code path and no-key fallback are CI-testable;
- `AI33 Guidance Voice = ACTIVE` until a credentialed local browser run proves actual AI33 generation/playback and measures latency;
- `Echo / Self-Capture Guard = ACTIVE` until a human run confirms ERRATA speech is not re-transcribed;
- no Cloudflare/public-runtime promotion occurs from this local provider substitution alone.

## AI33 live browser review — retry semantics + latency correction

Human browser video review confirmed:

- AI33 Pro guidance audio now plays successfully through Zach / George V2;
- observed generation examples were approximately 6.80 s / 104 credits and 9.24 s / 176 credits;
- this is functionally successful but too slow to treat as conversationally complete;
- AssemblyAI sometimes misheard Cumberland as Cubberland and skip as keep;
- after a rejected interpretation, subsequent spoken retries were appended to the prior rejected buffer, producing repeated Route 55 transcripts and making recovery worse.

Implemented correction:

- rejected / clarification-required attempts mark the next spoken turn as a fresh attempt;
- the next utterance clears the rejected buffered turns instead of concatenating indefinitely;
- AssemblyAI streaming now receives keyterms for King Edward and Cumberland;
- repeated AI33 guidance audio is cached in-process after first successful generation;
- cache hits report 0 new credits and are labeled in the UI;
- first-generation latency remains an ACTIVE product concern and must be measured rather than hidden.

Truth:

- AI33 Guidance Voice is functionally observed locally but remains ACTIVE pending a clean proof run with retry behavior and latency evidence;
- Echo / Self-Capture Guard remains ACTIVE pending explicit proof;
- Conversational Latency / Operational Economics remains ACTIVE.

## Live browser semantic-time regression + draft reset correction

Human browser video review exposed a blocking semantic bug even though AI33 guidance audio was functioning:

- AssemblyAI formatted `9:30` as `9: 30` in the completed transcript;
- the bounded parser treated that spaced clock separator as hour-only `9`, causing ERRATA to preview and stage `09:00` instead of `09:30`;
- the operator then repeated the full instruction while the first preview was already READY_TO_APPLY, and the browser appended the second completed turn to the first draft.

Corrections implemented:

- controlled transcript normalization now collapses numeric clock separators with surrounding whitespace (`9:30`, `9: 30`, `9 : 30` -> equivalent);
- regression tests prove spaced realtime STT clock formatting preserves `09:30:00` and never degrades to `09:00:00`;
- every new spoken turn after a completed preview starts a fresh draft until the prior preview is explicitly applied;
- UI now exposes `AI33 GENERATING VOICE` -> `ERRATA SPEAKING` -> `ECHO COOLDOWN` -> `VOICE CONNECTED` so the operator knows listening is intentionally suspended during the slow AI33 reply.

Truth:

- the observed video does NOT promote Integrated Browser Voice because it staged the wrong end time;
- STT Clock-Time Fidelity remains ACTIVE until a clean human rerun proves `9: 30` -> `09:30` end-to-end;
- AI33 Guidance Voice remains ACTIVE pending clean latency/playback evidence;
- Echo / Self-Capture Guard remains ACTIVE pending explicit no-self-transcription evidence.

## Clean browser rerun — clock-time fidelity closed

Human browser video rerun after the spaced-clock parser fix observed:

- voice engine AI33 Pro / Zach / George V2 active;
- greeting/guidance entered explicit AI33 generating and ERRATA speaking states;
- buffered operator transcript contained one bounded instruction: `Route 55 west, skip King Edward and Cumberland until 9:30.`;
- non-mutating preview summarized `until 09:30`;
- human Apply staged revision 2 with end time `09:30`;
- no prior `09:00` degradation recurred;
- the operator buffer was cleared after Apply.

Promotion:

- `STT Clock-Time Fidelity = PROVEN` for this bounded local browser scenario.

Still ACTIVE:

- AI33 Guidance Voice: functioning but first-generation latency remains materially high;
- Echo / Self-Capture Guard: visually promising in this run, but final evidence should include the complete correction/negative flow and exported receipt;
- fresh-draft retry behavior: implementation is present but this clean run did not require a rejected retry.

## Browser scenario B — same-identity correction + recovery proven

Human browser video observed the complete correction path on the same staged change:

- base change reached revision 2 at end time 09:30;
- first correction attempt was transcribed as `Wait, keep Cumberland, make it turn.`;
- ERRATA returned clarification (`I need one more detail`) and explicitly stated nothing had changed;
- next operator attempt `Wait, keep Cumberland, make it 10.` replaced the prior rejected draft rather than concatenating with it;
- preview resolved the intended candidate: route 55 west, King Edward skipped, Cumberland restored, end time 10:00, canonical state still unchanged before Apply;
- explicit human Apply then staged revision 3;
- revision 3 summary showed route 55 west, skipping King Edward, until 10:00; Cumberland was no longer in the skipped set;
- operator buffer cleared after Apply;
- multiple AI33 guidance playbacks occurred without observed self-transcription into the operator buffer.

Observed AI33 telemetry in this run included approximately 9.48 s / 189 credits, 11.61 s / 241 credits, 11.83 s / 192 credits, and 13.89 s / 225 credits for distinct uncached guidance. This proves functional playback but also confirms conversational latency/operational economics remain materially ACTIVE.

Promotions:

- `Interactive Voice Guidance = PROVEN` (bounded local browser);
- `AI33 Guidance Voice = PROVEN` for local functional playback + telemetry, not low-latency conversational quality;
- `Echo / Self-Capture Guard = PROVEN` for the bounded local browser evidence;
- `Voice Retry Draft Isolation = PROVEN`;
- same-identity browser correction rev2→rev3 = PROVEN within the current Integrated Browser Voice workstream.

Still required before Integrated Browser Voice Surface can be promoted:

- explicit atomic negative scenario `Wait, keep Cumberland. Make it.` with rev/hash unchanged and no partial KEEP leak;
- stale reviewed-hash refusal + current-hash commit through the browser;
- exported session receipt bound to the exact git SHA/run;
- reconcile final evidence on one exact head.
\n## P0 product hardening + Vercel runtime block\n\nImplemented as one consolidated product-depth delta after human browser review:\n\n### Voice initialization / response latency\n\n- AssemblyAI temporary-token fetch and microphone permission now initialize in parallel;\n- voice connection time and deterministic preview time are shown in the UI and exported as evidence;\n- visual guidance remains immediate while spoken guidance is asynchronous;\n- spoken guidance now uses concise, cache-stable copy rather than reading the full visual diff;\n- the greeting is prefetched as soon as Start microphone is pressed;\n- the reusable READY_TO_APPLY phrase is prefetched as soon as the first operator speech begins;\n- the reusable applied-state phrase is prefetched once a safe preview exists;\n- AI33 audio is cached in memory and persistently outside the git worktree on local machines;\n- the microphone stays live while AI33 is only generating audio;\n- half-duplex suppression begins only when guidance audio actually plays, then keeps the 750 ms echo cooldown;\n- new operator speech invalidates a stale pending voice reply before it can play;\n- a Skip voice reply control cancels delayed spoken guidance without disconnecting the live microphone;\n- UI telemetry now reports connect / interpret / voice generation latency plus cache and incremental AI33 credit information.\n\n### Evidence / recovery hardening\n\n- exported receipts now include client voice telemetry and a bounded client event ledger;\n- non-mutating previews, including malformed/clarification paths, are retained in the client evidence ledger so a correct pre-mutation refusal is no longer invisible;\n- exact operator sessions can be serialized and reconstructed through the shared Python core;\n- signed compressed HMAC session tokens reject tampering and preserve revision/hash/history across serverless rehydration;\n- CI asserts canonical rev3 signed-token size remains below 12 KB.\n\n### Vercel public runtime implementation\n\n- `app.py` is a FastAPI Vercel entrypoint exposing the same operator APIs and shared ERRATA Python core;\n- public state model is explicitly `SIGNED_BROWSER_SESSION`, not process-global memory;\n- session signing requires a dedicated server secret `ERRATA_SESSION_HMAC_KEY`;\n- `/api/health` exposes non-secret readiness and exact runtime git binding;\n- state truth explicitly records cold-start continuity=yes, shared multi-operator durable store=no, rollback resistance=no;\n- `vercel.json` configures the Python function duration;\n- `.github/workflows/deploy-vercel.yml` can create/link the `errata` Vercel project in `faadil1s-projects`, deploy the exact commit, verify `/api/health`, and emit a deployment receipt.\n\n### Deployment reality\n\nThe Vercel MCP deployment action is currently broken server-side (`deploy_to_vercel` -> tool not found). The GitHub deployment fallback executed on run `36695606628` and stopped at an explicit credential preflight:\n\n- status: `BLOCKED_MISSING_VERCEL_TOKEN`;\n- `VERCEL_TOKEN`: absent in GitHub Actions secrets;\n- `ASSEMBLYAI_API_KEY`: absent in GitHub Actions secrets;\n- `AI33_API_KEY`: absent in GitHub Actions secrets;\n- no public deployment URL was created;\n- deployment receipt artifact: `11087222278`;\n- artifact digest: `sha256:aee74d48a6911aa096d6fcf364966ca1fa549f883204f56e4090c5a1a3f61e74`.\n\nThis is a credential boundary, not a code/runtime claim. Do not promote Vercel Public Runtime until a URL and exact-SHA health receipt exist.\n\n### Historical browser receipt archived\n\nThe user-exported receipt from the prior browser run is now checked in under `evidence/browser-voice-v0.1/20260930-085302/` as `HISTORICAL_PARTIAL`. It proves the correct rev1→2 and rev2→3 voice mutations on one AssemblyAI session, but its runtime SHA is old, the recorded worktree was dirty, state remained STAGED, and preview-only negative evidence was not yet embedded. It is not final closure evidence.\n\nCurrent next proof order:\n\n1. exact-head CI all green;\n2. one clean local browser run using the new latency/event-ledger build: base -> malformed negative -> recovery -> rev3 -> stale refusal -> current commit -> export receipt;\n3. configure Vercel deployment credentials without exposing them in chat;\n4. deploy preview and verify `/api/health` exact SHA;\n5. configure provider secrets for full public voice;\n6. repeat the same evidence-backed flow on the public runtime;\n7. only then promote Integrated Browser Voice / Vercel Public Runtime / Live Product Integration as warranted.\n\n## Hardening block final reconciliation\n\nAdditional closure details after the consolidated P0 hardening pass:\n\n- Vercel deployment preflight is now a failing/BLOCKED check when `VERCEL_TOKEN` is absent, so a green deploy check cannot be mistaken for a deployment;\n- a secure local PowerShell fallback exists at `scripts/deploy_vercel_local.ps1`; it reuses local Windows AssemblyAI/AI33 environment variables, configures Vercel secrets through stdin, creates a dedicated session HMAC secret, deploys preview by default, and verifies `/api/health` against exact git HEAD;\n- Vercel runtime specification is canonical at `docs/VERCEL-PUBLIC-RUNTIME-v0.1.md`;\n- Browser Voice Proof Protocol now includes latency/barge-in/cache/client-event evidence requirements;\n- README and `.env.example` are reconciled with the dedicated `ERRATA_SESSION_HMAC_KEY` boundary;\n- historical browser receipt is archived as `HISTORICAL_PARTIAL`, never final closure.\n\nDeployment remains credential-blocked until either the local Vercel CLI path is authenticated/executed or `VERCEL_TOKEN` is added to GitHub Actions. No public URL is claimed.\n
## Vercel preview runtime proven — exact SHA 36ccd03

Observed deployment result:

- deployment id: `dpl_3ntykUre5uPvrKWfacuPg21ftmUa`;
- preview URL: `https://errata-5hg3gfy46-faadil1s-projects.vercel.app`;
- Vercel state: `READY`;
- git SHA: `36ccd03ab2b246a063855098115bc2c17f443dfa`;
- branch: `technical-reality-live-assemblyai-v0.1`;
- authenticated local verification via `vercel curl /api/health` returned:
  - `runtime=vercel-fastapi`;
  - `session_signing_ready=True`;
  - `assemblyai_ready=True`;
  - `ai33_ready=True`;
  - `full_public_voice_ready=True`;
- no secret value was printed.

Promotion:

- `Vercel Preview Runtime = PROVEN`;
- exact deployed-commit/runtime binding = PROVEN;
- server-side provider readiness = PROVEN;
- signed-session public runtime availability = PROVEN for the protected preview.

Still not promoted:

- `Judge/Public Accessibility = BLOCKED` because Vercel Deployment Protection is still enabled;
- `Public Voice Core Loop = ACTIVE` because server readiness is not the same as browser product proof;
- production domain/runtime is not promoted;
- Live Product Integration remains BLOCKED until the browser core loop, negative path, stale/current commit, receipt, and post-build reconciliation pass on the deployed URL.

## Judge-performance delta — ghost speech, bilingual correction, downstream consumer

Implemented before final hackathon packaging:

- judge-first hero above the canonical state explains the user, problem, exact voice scenario, same-change repair invariant, and GTFS-RT consequence;
- rejected or superseded un-applied speech is visualized as `GHOST SPEECH · NOT CANONICAL` with `0 effect · hash unchanged`;
- revision trail now starts with a same-identity rail (`rev1 -> rev2 -> rev3`) before the detailed audit history;
- AssemblyAI Streaming v3 now biases expected languages to English + French while keeping Universal-3.5 Pro Realtime and transit keyterms;
- bounded parser supports the code-switched correction `Wait, garde Cumberland. Make it 10.` and retains deterministic mutation authority;
- a downstream consumer panel now displays an independent decode of the actual serialized GTFS-RT bytes using `consumer_wire.py`, rather than presentation-only state;
- judge-first README now explains the product before governance terminology.

Truth:

- official AssemblyAI capability supports French/code-switching, but ERRATA's bilingual browser path remains ACTIVE until human-observed on deployed runtime;
- the consumer panel is an independent demo consumer of generated protobuf bytes, not a claim that STO, Transit, Google or another agency/rider app ingested the feed;
- ghost speech is UI evidence of non-mutation; it does not replace the canonical receipt/hash evidence.

## DeepSeek review delta — AssemblyAI context-aware streaming

Accepted from external review after verification against current AssemblyAI documentation:

- use Universal-3.5 Pro Realtime `agent_context` as an STT accuracy lever rather than adding a new mutation-authority model;
- keep provider Context Carryover enabled by default;
- refresh `keyterms_prompt` mid-session from canonical route/stop context via `UpdateConfiguration`;
- use `balanced` mode for the interactive browser voice path and measure latency rather than assuming improvement.

Implemented on `judge-finalization-deepseek-v0.1`:

- seed `agent_context` with the ERRATA opening guidance;
- publish the completed AI33/browser guidance reply to AssemblyAI only after playback completes;
- refresh keyterms after canonical Apply without reconnecting;
- record `ASSEMBLYAI_STREAM_CONFIG` and `ASSEMBLYAI_UPDATE_CONFIGURATION` events in the client evidence ledger;
- expose context/keyterm update counters in browser voice metrics;
- tests lock the configuration shape.

Not adopted before submission:

- migration to LiveKit/Pipecat;
- an LLM function-calling mutation layer;
- Guardrails API without a demonstrated PII/moderation requirement in the bounded scenario;
- Twilio phone transport;
- multi-operator collaboration;
- Calendar integration;
- speaker diarization for a single-operator demo.

`AssemblyAI Context-Aware Streaming = ACTIVE` until deployed-browser proof. Provider benchmark improvements must not be restated as ERRATA-specific WER gains.

## Kimi review delta — Twilio phone transport

Accepted after verification against current Twilio, AssemblyAI and Vercel capabilities:

- Twilio bidirectional Media Streams provide inbound μ-law 8 kHz audio and DTMF events;
- Universal-3.5 Pro Realtime accepts `pcm_mulaw` at 8000 Hz natively, so ERRATA does not need resampling for the phone path;
- Vercel Functions added WebSocket server support in 2026, allowing the phone adapter to coexist with the FastAPI runtime;
- Twilio explicitly requires `X-Twilio-Signature` validation, so both the voice webhook and WebSocket upgrade enforce it.

Implemented on the finalization branch:

- `/twilio/voice` returns signed/validated TwiML with `<Connect><Stream>`;
- `/api/twilio-stream` is a Node WebSocket Function;
- Twilio media frames are decoded from base64 and forwarded as raw μ-law bytes to AssemblyAI;
- final AssemblyAI turns are sent to the existing non-mutating `/api/preview/voice` path;
- the caller receives the interpreted preview by SMS;
- DTMF `1` may Apply only when preview status is `READY_TO_APPLY` and the review SMS succeeded;
- DTMF `2` discards the captured preview;
- Apply uses the same `/api/amend/voice` endpoint, signed session token, reducer and validators, with `boundary=TwilioDTMF1`;
- commit remains a separate protected action;
- static tests lock codec, signature, route ordering and human-boundary invariants.

Truth boundary:

- Twilio Phone Transport remains `ACTIVE`, not `PROVEN`;
- no Twilio account/number/credentialed call has been exercised yet;
- public production accessibility is required because Twilio cannot use the protected preview flow as a normal caller;
- no claim of phone TTS conversation is made: the current bounded path uses Twilio voice instructions + SMS review + DTMF Apply/Discard;
- this is a second transport to the same ERRATA core, not a second mutation authority.

## Public production runtime proven

Observed on Vercel production:

- deployment: `dpl_7FrSneaFEHQRZi7KUfPQoT6QW9Nd`;
- permanent judge URL: `https://errata-beige.vercel.app`;
- state: `READY`;
- exact deployed SHA: `48ab84a11061cf7dfa729c1b774565cabaf444c8`;
- root HTTP status: `200`;
- `/api/health` HTTP status: `200`;
- session signing: READY;
- AssemblyAI: READY;
- AI33: READY;
- full server-side browser voice readiness: TRUE;
- Deployment Protection: disabled.

Promotions:

- `Vercel Production Runtime = PROVEN`;
- `Judge/Public Accessibility = PROVEN`;
- exact production runtime/commit binding = PROVEN.

Still ACTIVE / not promoted:

- `Public Voice Core Loop`: needs the final human production-browser run and exported receipt;
- `AssemblyAI Context-Aware Streaming`: implemented, needs deployed-browser evidence;
- `Browser Barge-In`: implemented opt-in, needs human proof without self-capture;
- `Twilio Phone Transport`: implemented but not credentialed/configured on production;
- agency live integration/adoption: not claimed.

Metadata caveat: this first production deployment reports the correct exact SHA but Vercel branch metadata still says `technical-reality-live-assemblyai-v0.1` because the local `git checkout main` was blocked by an uncommitted `.gitignore`. The next packaging redeploy should be performed from an actual local `main` checkout to reconcile `git_branch=main`.
## Final submission sequencing — Twilio + UI/UX

- Twilio has no available credentials/number for a credentialed proof before submission.
- `Twilio Phone Transport = BLOCKED` and is explicitly non-blocking for the hackathon submission.
- Do not show or claim Twilio as a live proven feature; keep it as implemented future transport architecture only.
- The final UI/UX improvement pass is intentionally deferred until all functional/runtime/proof updates are complete.
- Planned final design pass: Claude Opus 5.5, focused on judge comprehension in the first 5 seconds, stronger visual hierarchy, memorable same-change repair storytelling, clearer evidence/consequence surfaces, responsive/mobile behavior, accessibility, reduced motion, and anti-AI-slop review.
- The final design pass must not change canonical semantics, authority boundaries, evidence labels, or the verified demo scenario without re-running the affected gates.

## Twilio submission decision — no paid upgrade

- Twilio Full Access requires balance/payment setup.
- Paid upgrade was explicitly declined for this hackathon.
- No credentialed Twilio Media Streams proof will be attempted before submission.
- `Twilio Phone Transport` remains `BLOCKED` and non-blocking.
- Do not show or claim Twilio as a live proven feature in the video, README hero, or Lablab submission.
- Keep the implementation as future transport architecture only.
\n## Bandwidth Build phone transport — selected free path\n\nTwilio remains BLOCKED because its required Media Streams path would require a paid upgrade.\n\nBandwidth Build is now the selected optional phone proof path because its current self-serve trial advertises:\n\n- no credit card;\n- 3,000 Voice API trial credits;\n- one included US local number;\n- access to the full Voice API rather than a sandbox.\n\nImplemented on `bandwidth-phone-transport-v0.1`:\n\n- authenticated inbound BXML webhook;\n- bidirectional `<StartStream>` with inbound PCMU 8 kHz media;\n- direct raw μ-law forwarding to AssemblyAI Universal-3.5 Pro Realtime;\n- same non-mutating `/api/preview/voice` path;\n- stateless signed review token binding call ID + transcript + canonical revision/hash;\n- Bandwidth OAuth client-credentials flow for Update Call BXML;\n- spoken review inside the live call;\n- DTMF `1` Apply / `2` Discard through the same ERRATA core;\n- Apply rechecks the reviewed canonical revision/hash before mutation;\n- static CI contract for codec, auth, route ordering and mutation boundary.\n\nTruth boundary:\n\n- `Bandwidth Phone Transport = ACTIVE`, not PROVEN;\n- no Bandwidth account/number/credentialed call has been exercised yet;\n- the optional phone demo is one bounded reviewed amendment; the canonical browser path remains the primary same-identity rev1→rev2→rev3 demo;\n- no claim of agency telephony integration.\n