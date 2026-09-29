# ERRATA — CURRENT

**Lifecycle:** DESIGN  
**Workstream:** Technical Reality / Prototype Killer — LIVE AssemblyAI v0.1  
**Concept:** v2 relocked  
**Brand:** ERRATA working name; Naming / Collision Gate remains ACTIVE.  
**Canonical feature branch:** `technical-reality-live-assemblyai-v0.1`

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
