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

After that comparison, the remaining Prototype Killer deltas are interruption/barge-in and failure/recovery.

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
