# ERRATA — Evidence Audit: Controlled Streaming LIVE 2026-09-29

**Audit verdict:** PASS for the bounded live core mechanism, with explicit instrumentation gaps.  
**Original archive:** `ERRATA-controlled-streaming-live-evidence-20260929.zip`  
**Archive SHA-256:** `bd0866451ec4eecc97484f80173665d062b92fbfab79b7eb7a33aaa70a8136b0`  
**Runtime source SHA under test:** `6efbd6036647998aeb4d9efe0974c194a9819d35`  
**Runtime binding source:** synchronized branch/head context plus the operator's terminal run; the original archive did not embed the git SHA.

## Archive integrity

ZIP CRC validation passed. The archive contains exactly four files and no unexpected path entries:

| File | Bytes | SHA-256 |
|---|---:|---|
| `controlled_capture_receipts.jsonl` | 2962 | `5cd6fa7eff67c535aec442c044cb29db4c06bb294f211d4c710b9a0226844d23` |
| `raw_streaming_events.jsonl` | 27685 | `f4f1e19c4f25ecf2dd5f3f963d5807697035ee4dd8e8f12c4add5c7d986522ce` |
| `state-rev-002.json` | 1541 | `f7ae93db5b05379ff9f2775763abcc5f5ef1cfa006149dff543a884b1a025e19` |
| `state-rev-003.json` | 1351 | `cc7f2d22a1508c97317aa66559ff6d43956b1461c8be86f6bb29dbf1d9c8aca5` |

No authorization header, bearer token, API-key field, or obvious secret string appears in the archived JSON evidence. Raw microphone audio was not persisted.

## Streaming evidence

The raw event file is valid JSONL and contains 36 events:

- 1 `Begin`
- 2 `SpeechStarted`
- 31 `Turn`
- 2 client `ForceEndpoint`

The `Begin` event reports:

- API version: `2025-05-12`
- model: `universal-3-5-pro`
- mode: `max_accuracy`
- voice focus: `near-field`

Exactly two final turns have `end_of_turn=true` and `end_of_turn_confidence=1.0`:

1. `Route 55, west, skip King Edward and Cumberland until 9:30.`
2. `Wait, keep Cumberland, make it 10.`

The two `ForceEndpoint` client events are present. In this particular run, each was sent **after** the corresponding provider final turn had already arrived. Therefore the run proves human-controlled mutation admission, but it does **not** prove that `ForceEndpoint` itself caused a live endpoint.

## Canonical transition evidence

The receipt file contains exactly two `CONTROLLED_CAPTURE_FINALIZED` records.

### Revision 1 → 2

Operations:

- `ROUTE=55`
- `DIRECTION=west`
- `SKIP=King Edward`
- `SKIP=Cumberland`
- `END=9:30`

Observed:

- before hash: `17d1be0a7080e628b8249aab5d6d2aff4655a9d43e0a821e0839738a5524f72a`
- after hash: `8d6f83a9a20df286548030bdc1dda8c73fdda9de4da030ef5ff26b14f1de4225`
- status: `APPLIED`
- all five blocking validators: `PASS`
- affected trips: 2
- skipped stop-times: 4

### Revision 2 → 3

Operations:

- `KEEP=Cumberland`
- `END=10`

Observed:

- before hash equals the exact revision-2 after hash;
- after hash: `320221743ffda8433ac5abfbd5a5565aed96c166e87360955a51961dd7ca6f64`
- status: `APPLIED`
- all five blocking validators: `PASS`
- affected trips: 3
- skipped stop-times: 3

This establishes a continuous hash chain across both live mutations.

## Independent state-hash verification

Using the canonical `ServiceChange.state_hash` algorithm from runtime SHA `6efbd603...`, the two archived state snapshots were independently re-hashed during audit.

- revision 2 recomputed hash: `8d6f83a9a20df286548030bdc1dda8c73fdda9de4da030ef5ff26b14f1de4225` — **MATCH**
- revision 3 recomputed hash: `320221743ffda8433ac5abfbd5a5565aed96c166e87360955a51961dd7ca6f64` — **MATCH**

The receipt chain, snapshot hashes, and canonical hashing algorithm therefore agree.

## Revision-3 semantic result

The archived revision-3 snapshot confirms:

- same `change_id = ERR-LIVE-001`
- route `R55`
- direction `1`
- end time `10:00:00`
- only `S_KING_EDWARD` remains skipped
- Cumberland is restored
- no unresolved items
- no pending calls
- revision `3`

This is sufficient evidence for the bounded same-identity amendment mechanism and controlled Streaming live core.

## Evidence gaps

The original archive is **not fully self-contained** for every gate:

1. It does not contain `runtime_manifest.json`; the exact git SHA is bound through synchronized GitHub/terminal context rather than embedded in the archive.
2. The original JSONL records do not contain local `observed_at` timestamps.
3. `state-rev-003.json` is `STAGED`. The stale-commit refusal, accepted current-hash commit, and final `COMMITTED` snapshot were observed in the operator terminal after this state file was written, but were not persisted by the original runner.
4. No explicit `Terminate` / final-run receipt is present in the original archive.
5. The two `ForceEndpoint` commands followed already-final turns, so live forced-endpoint efficacy remains unproven.

These gaps do not invalidate the central live state-transition proof. They prevent the original archive alone from serving as a complete proof packet for runtime binding, commit authority, and forced-endpoint behavior.

## Corrective instrumentation

The branch has been hardened after this audit so subsequent controlled runs generate:

- `runtime_manifest.json` with git SHA, branch, tracked-worktree cleanliness, runtime/package versions, and Streaming configuration;
- UTC `observed_at` on raw events and receipts;
- `HUMAN_APPLY` receipts;
- `CONTROLLED_CAPTURE_PREPARED` receipts;
- stale commit refusal receipts;
- accepted human commit receipts;
- committed-state snapshot;
- final-state snapshot;
- explicit Terminate event;
- `evidence_manifest.json` with per-file SHA-256 hashes.

## Gate result

**PROVEN in bounded LIVE scope:**

- Technical Reality Check
- Controlled Streaming STT Capture
- Human-Controlled Mutation Admission
- Same Identity / Revision Semantics
- Minimal Correction
- Live Core Loop
- canonical hash continuity

**Terminal-observed but not contained in the original ZIP:**

- stale reviewed-hash rejection
- human commit authority
- final `COMMITTED` state

**Still open:**

- self-contained evidence-to-runtime binding on a newly instrumented run
- live forced-endpoint efficacy
- interruption/barge-in side-effect safety
- disconnect/recovery
- voice-vs-keyboard baseline
- external GTFS-RT validation / independent consumer
- external operator evidence
