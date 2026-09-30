# ERRATA — Spec Kit: External Acceptance Slice v0.1

**Lifecycle:** DELIVER  
**Parent:** `docs/PRD-v0.1.md`  
**Depth review:** `docs/POST-VERTICAL-SLICE-DEPTH-GAP-REVIEW-v0.1.md`  
**Scope:** P0 external acceptance only

## 1. Objective

Close the gap between “ERRATA can serialize bytes that its own code understands” and “the output is independently consumable and ready for canonical GTFS-Realtime validation.”

Target chain:

```text
canonical ServiceChange
  → ERRATA GTFS-RT serializer
  → official MobilityData GTFS-Realtime bindings consumer
  → canonical MobilityData GTFS-Realtime validator
  → immutable evidence
```

## 2. External authorities selected

### Independent consumer

Use the official MobilityData `gtfs-realtime-bindings` Python package.

This consumer must:

- import `google.transit.gtfs_realtime_pb2`;
- parse ERRATA's binary output without importing ERRATA's dynamic descriptor or wire parser;
- expose the decoded feed version, trip IDs, route IDs, direction IDs and skipped stops;
- assert the canonical corrected state from the bounded fixture.

### Canonical validator

Use MobilityData's `gtfs-realtime-validator`, pinned for this slice to commit `7041fa3fcaf674bf730e17325c179d329cdff6f2`.

The canonical batch validator requires:

- a GTFS static ZIP covering the realtime data;
- a directory containing GTFS-Realtime protobuf files;
- Java 17 for the pinned validator commit (the upstream project upgraded to Java 17 in that revision).

Its JSON output is the validation receipt.

The validator is external to ERRATA and must not be replaced by `errata.consumer_wire`.

## 3. Slice boundaries

### In scope

- existing synthetic GTFS fixture;
- existing deterministic final Route 55 state;
- existing GTFS-Realtime-shaped TripUpdate serializer;
- official bindings parse;
- canonical validator execution;
- evidence report and checksums.

### Out of scope

- real agency production feed;
- public-network data;
- service alerts / vehicle positions;
- agency publication;
- operator UI;
- broad GTFS-Realtime feature coverage.

## 4. Implementation steps

### A. Independent official consumer

Add:

- `requirements-external.txt`
- `scripts/consume_with_official_gtfs_rt_bindings.py`
- CI job `external-acceptance`

Pinned dependency for this slice (selected because v3.0.0 requires protobuf>=7.34.0 while ERRATA currently pins protobuf<7):

`gtfs-realtime-bindings==2.0.0`

The script must fail non-zero if:

- protobuf cannot be parsed by official bindings;
- feed header is missing or unexpected;
- no TripUpdate entity is present;
- expected King Edward skip is absent;
- Cumberland remains skipped in the corrected final artifact.

### B. Validator fixture packaging

Produce:

- static GTFS fixture ZIP;
- `TripUpdates.pb`;
- official-consumer JSON receipt;
- metadata containing runtime Git SHA and file SHA-256 values.

### C. Canonical validator

Run MobilityData `gtfs-realtime-validator` batch mode against the packaged static GTFS + `TripUpdates.pb`.

Preserve:

- exact validator source/version or image/JAR identity;
- command;
- stdout/stderr;
- JSON result;
- exit code;
- input SHA-256 values.

## 5. Acceptance criteria

### Independent Consumer → PROVEN

All of the following:

1. official MobilityData bindings parse the protobuf;
2. at least one TripUpdate entity is decoded;
3. Route 55 trip updates are observable;
4. King Edward is observed as SKIPPED;
5. Cumberland is not observed as SKIPPED in the corrected final state;
6. result is generated in CI from a clean checkout;
7. evidence artifact is uploaded.

### External / Canonical GTFS-RT Validation → PROVEN

All of the following:

1. MobilityData canonical validator actually executes;
2. validator consumes the same protobuf bytes whose SHA is recorded;
3. validator consumes the corresponding static GTFS ZIP;
4. validator output is archived;
5. blocking errors are understood and either absent or explicitly resolved;
6. no ERRATA-owned parser is used as the sole validator.

## 6. Truth boundary

Official bindings parse **does not equal canonical validation**.

Until the MobilityData validator is actually executed:

- `Independent Consumer` may be promoted;
- `External / Canonical GTFS-RT Validation` remains BLOCKED;
- `Real Consequence — LOCAL` remains BLOCKED.

## 7. Evidence layout

```text
evidence/external-acceptance-v0.1/
  gtfs_static.zip
  rt/
    TripUpdates.pb
  official_bindings_consumer.json
  validator/
    command.json
    stdout.txt
    stderr.txt
    validation-results.json
  evidence_manifest.json
```

## 8. Definition of Done

This slice is done only when the official consumer and canonical validator both consume the same bounded output and their evidence is bound to the generating runtime/state.

If the official consumer succeeds but the canonical validator has not run, mark the slice **PARTIAL**, not PROVEN.


## 9. Canonical validator reproducibility pin

For v0.1, GitHub CI checks out:

`MobilityData/gtfs-realtime-validator@7041fa3fcaf674bf730e17325c179d329cdff6f2`

and builds only the validator library plus required parent modules:

`mvn -q -pl gtfs-realtime-validator-lib -am -DskipTests package`

The shaded `withAllDependencies` JAR is executed in batch mode against the packaged synthetic static GTFS ZIP and the exact `TripUpdates.pb` already consumed by official Python bindings.

This source pin is evidence metadata, not a claim that the validator version is production-stable; upstream documents the project as actively developed.
