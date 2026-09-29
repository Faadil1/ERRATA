# ERRATA — HANDOVER

## Completed

The bounded deterministic Technical Reality harness was cleaned into a single canonical Python package (`errata/`) and executed from a fresh evidence directory.

Verification:

```bash
python -m pytest
python -m errata.experiment
```

Current pytest result: **1 passed**. The single test contains **19 explicit assertions** over the local mechanism.

## Canonical evidence

`evidence/local-stub-v0.1/` contains:

- `experiment_results.json`
- `state_rev1.json`
- `state_rev2.json`
- `impact_rev1.json`
- `impact_rev2.json`
- `operation_log.jsonl`
- `receipts.jsonl`
- `raw_assemblyai_stub_events.jsonl`
- `persisted_state.json`
- `errata_rev2.pb`
- `independent_consumer.json`

## Next action

Implement the live AssemblyAI adapter **without changing the canonical reducer semantics**.

Required transaction rule:

`tool.call → PREPARE only → wait for reply.done → completed: APPLY / interrupted: DISCARD`

The next promotion decision is whether live execution is sufficient to advance `Technical Reality Check` and `Prototype Killer`. Living PRD remains downstream of that decision.
