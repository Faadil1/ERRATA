# ERRATA — HANDOVER

## Completed

The bounded deterministic Technical Reality harness is now on the feature branch `technical-reality-local-stub-v0.1` as a single canonical Python package (`errata/`) with fixtures, tests, state files, truth-boundary documentation, and a CI workflow.

Local verification of the exact source blobs represented on this branch:

```bash
python -m pytest
python -m errata.experiment
```

Current local pytest result: **1 passed**. The single test contains **19 explicit assertions** over the bounded local mechanism.

## Evidence flow

Generated runtime evidence is intentionally reproducible rather than hand-edited into the source tree.

`python -m errata.experiment` generates:

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

The GitHub Actions workflow uploads the generated `evidence/` directory as an artifact. This remains `LOCAL_STUB` evidence even when CI reproduces it.

## Next action

Review the feature PR and CI result. Do not merge automatically.

After human promotion, implement the live AssemblyAI adapter **without changing canonical reducer semantics**.

Required transaction rule:

`tool.call → PREPARE only → wait for terminal reply state → completed: APPLY / interrupted: DISCARD`

The next substantive promotion decision is whether the live run is sufficient to advance `Technical Reality Check` and `Prototype Killer`. Living PRD remains downstream of that decision.
