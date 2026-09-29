# LOCAL_STUB evidence

The evidence in this workstream is generated from the exact checked-out code with:

```bash
python -m pytest
python -m errata.experiment
```

Generated artifacts include state snapshots, operation logs, receipts, impact reports, the bounded GTFS-RT protobuf, and independent wire-parser output.

The repository intentionally does not treat generated local artifacts as LIVE evidence. CI uploads the generated `evidence/` directory as the `errata-local-stub-evidence` workflow artifact.

Current boundary: **LOCAL_STUB**.
