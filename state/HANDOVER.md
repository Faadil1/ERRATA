# ERRATA — HANDOVER

## Completed on this branch

A live AssemblyAI workstream has been layered on top of the already-promoted deterministic core **without changing reducer semantics**.

New components:

- `errata/live/tool_schema.py` — bounded semantic tool contract;
- `errata/live/coordinator.py` — PREPARE / APPLY / DISCARD transaction coordinator;
- `errata/live/audio.py` — 24 kHz PCM16 microphone/speaker transport;
- `errata/live/session.py` — Voice Agent API WebSocket/session lifecycle;
- `scripts/run_live_assemblyai.py` — interactive Prototype Killer runner;
- `tests/test_live_coordinator.py` — local transaction-contract tests;
- `docs/LIVE-ASSEMBLYAI-PROTOTYPE-KILLER-v0.1.md`;
- `docs/CONDITIONAL-GATEWAY-REGISTRY-v0.2.md`;
- `requirements-live.txt` and `.env.example`.

## Transaction invariant

The live adapter enforces:

`tool.call → PREPARE only → terminal reply boundary → completed: dry-run + APPLY / interrupted: DISCARD`

No tool call directly mutates canonical state.

The observed final user transcript is bound by the client and becomes the provenance text. The LLM's arguments are semantic proposals only.

## Credentialed run still required

A real microphone + AssemblyAI API key are external protected inputs unavailable to repository CI. No live gate is promoted merely because the adapter exists.

Run locally with headphones:

```bash
python -m pip install -r requirements-live.txt
cp .env.example .env
# add ASSEMBLYAI_API_KEY
python scripts/run_live_assemblyai.py --service-date 20260929 --start-time 09:00:00
```

During the run:

1. state the Route 55 change;
2. produce an actual barge-in/correction;
3. use `snapshot`;
4. use `drop` once to exercise session resume;
5. attempt a stale hash commit and capture refusal;
6. commit only the current reviewed hash;
7. stop the run and preserve the evidence directory unchanged.

## Required evidence before promotion

- exact git SHA;
- real AssemblyAI `session_id`;
- raw event stream;
- real `reply.done: interrupted`;
- pending discard receipt with unchanged canonical hash;
- live amendment receipt on the same change ID;
- dynamic-keyterm receipt;
- deliberate resume receipt;
- stale-commit refusal;
- current-hash human commit receipt;
- baseline comparison.

## Next promotion decision

If the live evidence passes audit, decide whether `Interruption Side-effect Safety — LIVE`, `Failure / Recovery — LIVE`, `AssemblyAI Load-Bearing Integration`, `Live Core Loop`, and `Prototype Killer` can advance.

The Living PRD remains downstream of that decision.
