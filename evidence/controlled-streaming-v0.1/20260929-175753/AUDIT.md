# ERRATA — Evidence Audit: Immediate-ENTER Atomicity LIVE 2026-09-29

**Audit verdict:** PASS for bounded LIVE runtime binding, ForceEndpoint finalization, and partial-correction atomicity.  
**Original archive:** `ERRATA-live-atomicity-20260929-175753.zip`  
**Archive SHA-256:** `1c4004eb1367acc93f8a971f36a6b6369340a7e698dbeca11f15ef77760230e7`  
**Runtime git SHA embedded in evidence:** `c83f750cc3b7f8d26c936d92a0c2f6525605be30`  
**Branch:** `technical-reality-live-assemblyai-v0.1`  
**Tracked worktree clean:** `true`

## Archive integrity

ZIP CRC validation passed.

The embedded `evidence_manifest.json` matches every listed file byte count and SHA-256 exactly.

Files in the packet:

- `controlled_capture_receipts.jsonl`
- `evidence_manifest.json`
- `raw_streaming_events.jsonl`
- `runtime_manifest.json`
- `state-final.json`
- `state-rev-001-start.json`
- `state-rev-002.json`
- `state-rev-003-manual.json`
- `state-rev-003.json`

No Authorization/Bearer material or AssemblyAI key value appears in the archived evidence. Runtime metadata explicitly states audio and API-key persistence are `NOT_RECORDED`.

## Runtime binding

The packet is self-binding to runtime SHA:

`c83f750cc3b7f8d26c936d92a0c2f6525605be30`

The runtime manifest also records:

- Python `3.14.6`
- websockets `15.0.1`
- sounddevice `0.5.6`
- protobuf `6.33.6`
- Windows 11
- AssemblyAI Streaming endpoint
- model `universal-3-5-pro`
- mode `max_accuracy`
- voice focus `near-field`
- sample rate `16000`

Stream session:

`632f1661-88b0-4056-9471-86d1ac646acd`

## ForceEndpoint evidence

Raw stream evidence contains:

- 43 provider Turn events
- 8 SpeechStarted events
- 3 client ForceEndpoint events
- 1 client Terminate event

All three `HUMAN_APPLY` boundaries were followed by an observed provider final turn after ForceEndpoint:

1. rev1: turn count `0 → 1`, final observed after `330.7 ms`
2. rev2 malformed correction: turn count `4 → 5`, final observed after `119.6 ms`
3. rev2 clean correction: turn count `5 → 6`, final observed after `164.8 ms`

The raw event timestamps independently show each ForceEndpoint request preceding its associated final Turn.

This is bounded LIVE evidence that the explicit human ENTER boundary can request endpoint finalization instead of waiting for the provider's autonomous final-turn timing. It is not a universal latency guarantee.

## Initial change

Human boundary at rev1/hash:

`17d1be0a7080e628b8249aab5d6d2aff4655a9d43e0a821e0839738a5524f72a`

Final transcript:

`Route 55 west, skip King Edward and Cumberland until 9:30.`

Operations:

- `ROUTE=55`
- `DIRECTION=west`
- `SKIP=King Edward`
- `SKIP=Cumberland`
- `END=9:30`

Outcome:

- `APPLIED`
- rev `1 → 2`
- hash `8d6f83a9a20df286548030bdc1dda8c73fdda9de4da030ef5ff26b14f1de4225`
- all five blocking validators PASS

## Negative path — incomplete explicit correction

Before the malformed correction:

- revision `2`
- hash `8d6f83a9a20df286548030bdc1dda8c73fdda9de4da030ef5ff26b14f1de4225`

Accumulated transcript:

`Wait, keep Cumberland, make it. You're done. Wait, keep. Wait, keep Cumberland, make it. You're done.`

Parser-resolved subset:

- `KEEP=Cumberland`

Explicit unresolved cue:

- `END_TIME_AFTER_MAKE_IT`

Outcome:

- `CONTROLLED_CAPTURE_REVIEW`
- reason `UNRESOLVED_EXPLICIT_CUES`
- revision remains `2`
- hash remains exactly `8d6f83a9a20df286548030bdc1dda8c73fdda9de4da030ef5ff26b14f1de4225`
- no partial KEEP reaches PREPARE/APPLY

This is the bounded LIVE proof for **Partial Correction Atomicity**.

## Clean retry

Transcript:

`Wait, keep Cumberland, make it 10.`

Operations:

- `KEEP=Cumberland`
- `END=10`

Outcome:

- `APPLIED`
- revision `2 → 3`
- hash `5115bba1cbeb95fab157fa32b29a9414252933f7241d3cfb30c623ba969ffde4`
- all five blocking validators PASS
- final skipped set contains only King Edward
- Cumberland restored
- end time `10:00:00`
- no unresolved items
- no pending calls

## Independent canonical hash verification

Using the exact `ServiceChange.state_hash` algorithm at runtime SHA `c83f750...`, audit recomputation matches every persisted snapshot:

- rev1 start → `17d1be0a7080e628...` MATCH
- rev2 → `8d6f83a9a20df286...` MATCH
- rev3 → `5115bba1cbeb95fa...` MATCH
- final → `5115bba1cbeb95fa...` MATCH

## Important packet boundary

This ZIP contains **no** `HUMAN_COMMIT_REFUSED` or `HUMAN_COMMIT_ACCEPTED` receipt.

Its final state is:

- status `STAGED`
- revision `3`
- hash `5115bba1cbeb95fab157fa32b29a9414252933f7241d3cfb30c623ba969ffde4`

Therefore this packet does **not** prove human commit authority or stale-hash rejection by itself. Those remain supported by the separate earlier terminal-observed LIVE run, not by this archive.

## Gate interpretation

Promotable from this self-contained packet:

- `Evidence-to-Runtime Binding — LIVE → PROVEN`
- `ForceEndpoint Efficacy — LIVE → PROVEN` in bounded immediate-ENTER scope
- `Partial Correction Atomicity — LIVE → PROVEN`
- `Controlled Streaming STT Capture → PROVEN`
- `Human-Controlled Capture Boundary → PROVEN`
- `Live Core Loop → PROVEN` in bounded scope
- `Evidence Integrity` for this packet → PROVEN

Not promoted from this packet:

- Human Commit Authority
- stale commit rejection
- interruption/barge-in side-effect safety
- disconnect/recovery
- production speech reliability
- external GTFS-RT validation / independent consumer
- operator desirability/adoption
