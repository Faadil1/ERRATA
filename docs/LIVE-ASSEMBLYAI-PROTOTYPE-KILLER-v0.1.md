# ERRATA — LIVE AssemblyAI Prototype Killer v0.1

**Lifecycle:** DESIGN  
**Workstream:** Technical Reality / Prototype Killer  
**Promotion target:** live speech transaction semantics, not product completeness.

## Purpose

This workstream tests the first load-bearing sponsor claim:

> A candidate mutation produced during live speech must remain non-canonical until the Voice Agent API reaches the terminal reply boundary. If the reply is interrupted, the candidate is discarded. If it completes, the candidate may enter deterministic resolution, validation, and the canonical reducer.

This is the live counterpart to the already-promoted `LOCAL_STUB` deterministic core.

## Current AssemblyAI protocol assumptions

The implementation follows current AssemblyAI Voice Agent API guidance:

- one WebSocket at `wss://agents.assemblyai.com/v1/ws`;
- Bearer authorization;
- wait for `session.ready` before audio;
- 24 kHz PCM16 microphone audio;
- `transcript.user` is the final user transcript;
- `tool.call` arguments are semantic proposals only;
- tool results are held until `reply.done`;
- `reply.done.status == "interrupted"` discards pending tool results;
- `session.resume` is used for recovery within the server grace window;
- `session.update` can change input configuration mid-session.

These are capability assumptions, not proof that ERRATA's implementation behaves correctly.

## Transaction protocol

```text
transcript.user
     ↓ bind observed final speech
tool.call
     ↓
PREPARE typed candidate batch
     ↓                 (canonical hash unchanged)
reply.done
  ├─ interrupted ───► DISCARD pending batch
  │                    canonical hash must remain identical
  └─ completed ─────► dry-run reducer
                       ↓
                    deterministic validators
                       ├─ fail ─► REVIEW_REQUIRED / no mutation
                       └─ pass ─► APPLY ONCE atomically
                                  ↓
                              new revision
                                  ↓
                         deterministic impact
                                  ↓
                         dynamic route keyterms
```

The LLM never receives commit authority.

## Human commit

The terminal runner exposes:

`commit <reviewed-state-hash-prefix>`

The prefix must contain at least 12 hexadecimal characters and must match the current canonical hash. Pending voice mutations or blocking validators refuse commit.

This is a prototype interaction, not a production authorization model.

## Canonical live task

Use headphones.

1. Say naturally:  
   **“Route 55 west, skip King Edward and Cumberland until 9:30.”**
2. Let ERRATA stage the change.
3. During a subsequent reply, barge in and correct:  
   **“Wait — keep Cumberland. Make it 10.”**
4. Confirm:
   - same `change_id`;
   - new revision;
   - Cumberland restored;
   - King Edward still skipped;
   - end time 10:00;
   - only targeted fields changed;
   - old artifacts stale if present.
5. Use `drop` once to deliberately close the socket and exercise `session.resume`.
6. Use `snapshot` to inspect current truth.
7. Attempt a stale hash commit and capture refusal.
8. Commit only the current reviewed hash.

## Required live receipts

A promotable run must capture:

- exact git commit SHA;
- AssemblyAI `session_id`;
- raw server/client JSON events except raw microphone payload duplication;
- final user transcript item IDs;
- `tool.call` IDs and arguments;
- PREPARED candidate receipts;
- interrupted DISCARD receipt with identical before/after canonical hash;
- applied revision receipts;
- dynamic keyterm update receipt;
- state snapshot per revision;
- deliberate disconnect and resume receipts;
- stale commit refusal;
- current-hash human commit receipt.

The evidence directory labels itself `LIVE_CANDIDATE` until audit. A run is not automatically promoted to `LIVE` merely because it reached AssemblyAI.

## Run

Install system PortAudio first, then:

```bash
python -m pip install -r requirements-live.txt
cp .env.example .env
# set ASSEMBLYAI_API_KEY in .env
python scripts/run_live_assemblyai.py --service-date 20260929 --start-time 09:00:00
```

The current fixture is deliberately bounded. A later gate must replace it with a verified public GTFS dataset before any claim of public-network realism.

## Falsification

The live mechanism fails or requires redesign if any of these occur:

- an interrupted tool call changes canonical state;
- a tool call mutates state before `reply.done`;
- a self-repair forks a new change identity;
- a correction changes an unrelated field;
- an unresolved stop is accepted;
- stale hash commit succeeds;
- the model supplies an operational ID that bypasses deterministic resolution;
- reconnect causes canonical-state divergence;
- evidence cannot be tied to the exact runtime commit.

## Truth boundary

This branch adds an executable live adapter, but until a real microphone/API-key run is audited:

- `Live Core Loop` = BLOCKED
- `AssemblyAI Load-Bearing Integration` = BLOCKED
- `Interruption Side-effect Safety — LIVE` = BLOCKED
- `Failure/Recovery — LIVE` = BLOCKED
- `Voice-native Necessity` = BLOCKED
- `Prototype Killer` = BLOCKED
