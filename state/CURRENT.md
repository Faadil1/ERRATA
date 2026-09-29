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

Observed terminal output is useful runtime evidence, but the canonical promotion packet still requires preserved evidence files tied to an exact git SHA.

Therefore:

- `Voice → native tool → reducer`: observed LIVE in a bounded successful run;
- managed turn regularity: **falsified for the current operational-dictation path**;
- controlled Streaming path: implemented, **not yet credentialed-run proven**;
- Prototype Killer: still BLOCKED.

## Still blocked

- `Prototype Killer` — broader promotion remains pending baseline + remaining live safety/recovery checks
- full `Live Core Loop`
- `Voice-native Necessity`
- `Interruption Side-effect Safety — LIVE`
- `Failure / Recovery — LIVE`
- external/canonical GTFS-RT validation
- third-party consumer acceptance
- `Real Consequence — LOCAL`
- operator desirability

## Protected claims

Do not claim production voice reliability, agency integration, controller adoption, production safety, public-network mutation, external GTFS-RT acceptance, or a completed Prototype Killer.

## Next human checkpoint

Stay in the successful controlled Streaming session and test hash-bound human authority before quitting:

```text
commit 8d6f83a9a20d
```

must be refused as stale, then:

```text
commit 320221743ffd
```

must be accepted.

After that, capture `snapshot`, then `quit`.

The controlled Streaming core run itself is already a successful Technical Reality result. See `docs/TECHNICAL-REALITY-CONTROLLED-STREAMING-RESULTS-v0.1.md`.

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
