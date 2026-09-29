# ERRATA — Controlled Streaming Technical Reality Results v0.1

**Evidence state:** LIVE_CANDIDATE — user-observed terminal run, canonical file bundle not yet ingested  
**Exact git SHA under test:** `6efbd6036647998aeb4d9efe0974c194a9819d35`  
**Local evidence directory reported:** `evidence/controlled-streaming-v0.1/20260929-143810`

## Result

The central ERRATA amendment mechanism survived the controlled Streaming Technical Reality test.

Observed live chain:

`microphone → AssemblyAI Universal-3.5 Pro Realtime → transcript → human-controlled apply → bounded parser → PREPARED → deterministic reducer → APPLIED`

### Initial change

Observed final transcript:

`Route 55, west, skip King Edward and Cumberland until 9:30.`

Parsed operations:

- `ROUTE=55`
- `DIRECTION=west`
- `SKIP=King Edward`
- `SKIP=Cumberland`
- `END=9:30`

Result:

- revision `1 → 2`
- state hash `17d1be0a7080e628... → 8d6f83a9a20df286...`

### Spoken amendment

Observed final transcript:

`Wait, keep Cumberland, make it 10.`

Parsed operations:

- `KEEP=Cumberland`
- `END=10`

Result:

- revision `2 → 3`
- same `change_id = ERR-LIVE-001`
- state hash `8d6f83a9a20df286... → 320221743ffda843...`

### Revision 3 state

Observed canonical state:

- route: `R55`
- direction: `1`
- service date: `20260929`
- start: `09:00:00`
- end: `10:00:00`
- skipped stops: only `S_KING_EDWARD`
- `S_CUMBERLAND`: no longer skipped
- unresolved items: none
- pending calls: none
- revision: `3`
- state hash: `320221743ffda8433ac5abfbd5a5565aed96c166e87360955a51961dd7ca6f64`

## What this proves

Within the bounded controlled-Streaming prototype:

- live speech can reach the canonical reducer through AssemblyAI;
- provider turn segmentation does not itself authorize state mutation;
- the initial service change can be staged deterministically;
- a later spoken correction amends the **same change identity** rather than forking it;
- the correction changes the targeted semantics: Cumberland is restored and the end time becomes 10:00;
- King Edward remains skipped;
- no unresolved or pending mutation remains after the amendment.

## What this does not prove

This result does **not** establish:

- production speech reliability;
- real barge-in side-effect safety;
- disconnect/session recovery;
- voice superiority over keyboard/direct structured entry;
- public-network GTFS realism;
- external GTFS-RT validator acceptance;
- third-party consumer acceptance;
- operator desirability/adoption;
- agency integration.

## Gate interpretation

Promotable now:

- `Technical Reality Check → PROVEN`
- `Controlled Streaming STT Capture → PROVEN` for this bounded run
- `Human-Controlled Capture Boundary → PROVEN` for this bounded run
- `Same Identity / Revision Semantics — LIVE → PROVEN`
- `Minimal Correction — LIVE → PROVEN` for this amendment
- `Live Core Loop — controlled Streaming scope → PROVEN`

Still pending before broader product promotion:

- stale reviewed-hash refusal and current-hash human commit in the same live session;
- voice-vs-keyboard baseline;
- interruption/barge-in side-effect test;
- disconnect/recovery;
- external GTFS-RT validation / consumer;
- operator trial.

The managed Voice Agent path remains a useful sponsor-native comparison surface, but its turn ownership was falsified as the primary consequential mutation boundary for this terminal experiment.
