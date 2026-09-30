# ERRATA — Canonical MobilityData GTFS-Realtime Validator CI Evidence

**Scope:** bounded synthetic fixture / external acceptance  
**Evidence state:** LOCAL CI + canonical external validator  
**Workflow run:** `36665394082`  
**Source branch head:** `60a11393e5832d9264b3169c210c4156401e5ce9`  
**CI checkout/runtime merge SHA:** `8bf83c7bd9f2a4b55a83fe5d153db544cef4a0c9`  
**Job:** `external-acceptance` — SUCCESS  
**Artifact ID:** `11075618019`  
**Artifact digest:** `sha256:94f892077adcf332961025b9a3b6f337e979c3374593346b2bc2fd94c33debcd`

## Canonical validator identity

Repository:

`MobilityData/gtfs-realtime-validator`

Pinned commit:

`7041fa3fcaf674bf730e17325c179d329cdff6f2`

Java runtime: 17

The validator library was built from pinned source in CI:

`mvn -q -pl gtfs-realtime-validator-lib -am -DskipTests package`

Shaded validator JAR SHA-256:

`a7ff0a5ed1146e6f224347bd59f3dd8a3ade7c49806d46fa20c3d70a70e7760c`

## Exact inputs

Synthetic static GTFS ZIP:

- bytes: `1332`
- SHA-256: `93bacc260f6ce286cadc22c2773e7eae164cd9ec00b18960f82690ac24b1023b`

GTFS-Realtime TripUpdates protobuf:

- bytes: `234`
- SHA-256: `f7ceac24f2f6c4a380f0aa465c3bf4f13abe25a4d7753b7b02b04b8baf771eef`

The exact same protobuf SHA was also parsed successfully by MobilityData's official Python bindings in the same CI job.

## Validator result

Process exit code:

`0`

Blocking ERROR rule groups:

`0`

Warnings:

`2`

Validation result SHA-256:

`74abce167f10ff3d1047c0903f709d9fb1f5d29babaa7cc0c9cde561f34647e8`

### W002 — vehicle_id not populated

The validator recommends `vehicle_id` for TripUpdates.

ERRATA does not fabricate vehicle identity for this service-change fixture merely to silence the warning. This warning is preserved as an explicit boundary.

### W008 — header timestamp older than 65 seconds

The bounded CI artifact uses a deterministic nonzero generation timestamp for reproducibility. The validator observed it as approximately 10 minutes old at execution time.

This is a freshness warning, not a structural/semantic validation error. A live publishing path would use the actual generation timestamp.

## Independent consumer result

MobilityData official Python bindings decoded:

- GTFS-Realtime version `2.0`;
- three R55 TripUpdate entities;
- direction `1`;
- trips `T5501`, `T5502`, `T5503`;
- `S_KING_EDWARD` as SKIPPED;
- no `S_CUMBERLAND` in the skipped set.

Consumer assertions: PASS.

## Gate interpretation

This evidence is sufficient in the bounded synthetic-fixture scope for:

- `Independent Consumer → PROVEN`
- `External / Canonical GTFS-RT Validation → PROVEN`
- `External Acceptance Slice → PROVEN`
- `GTFS-RT Adapter → PROVEN`

It does not establish:

- agency production integration;
- live public-network correctness;
- vehicle-level truth;
- feed freshness/SLA;
- operator adoption;
- production readiness.

The two validator warnings are intentionally retained rather than hidden or converted into false operational facts.
