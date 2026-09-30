# ERRATA — Official GTFS-Realtime Bindings Consumer CI Evidence

**Scope:** bounded synthetic fixture / independent consumer  
**Evidence state:** LOCAL CI / independent external library  
**Workflow run:** `36664709491`  
**Branch head:** `dfd41b4c986b99d42db668269d504ea3b7bb40b4`  
**Job:** `external-acceptance` — SUCCESS  
**Artifact:** `errata-external-acceptance-evidence`  
**Artifact ID:** `11075074423`  
**Artifact digest:** `sha256:c2c695af3b6fb5cbf71de27dff54ed686a3dde7559a8a12c20048fba2f894537`

## Independent consumer

Consumer package:

`gtfs-realtime-bindings==2.0.0`

This is MobilityData's official Python GTFS-Realtime bindings package. It was selected because the current ERRATA deterministic core pins `protobuf<7`; bindings v3.0.0 requires protobuf >=7.34.0.

The consumer does **not** import:

- `errata.protobuf_subset`
- `errata.serializer`
- `errata.consumer_wire`

It parses the generated protobuf through:

`google.transit.gtfs_realtime_pb2.FeedMessage`

## Input binding

`TripUpdates.pb`:

- bytes: `202`
- SHA-256: `bb5e6bd94acd01a61b2ad70e96047bda5f2bad27b1bc5d6824eb8915920591be`

Packaged static GTFS ZIP:

- bytes: `898`
- SHA-256 in CI package manifest: `a62154399c5534f56c836bc41e3c56e3b23e47359765e0abd7389d0a528b2a26`

## Observed official-bindings decode

The official bindings decoded:

- GTFS-Realtime version `2.0`
- 3 TripUpdate entities
- route `R55`
- direction `1`
- trips `T5501`, `T5502`, `T5503`
- `S_KING_EDWARD` as SKIPPED
- `S_CUMBERLAND` absent from the skipped-stop set

Assertions:

- expected King Edward skip: PASS
- expected Cumberland not skipped: PASS
- missing expected skips: none
- unexpected skips: none

## Gate interpretation

This is sufficient for:

`Independent Consumer → PROVEN`

in the bounded fixture scope, because an official external bindings implementation—not ERRATA's own parser—decoded the protobuf and observed the intended corrected state.

It is **not** sufficient for:

`External / Canonical GTFS-RT Validation → PROVEN`

The official bindings prove that the protobuf is parseable and that the expected semantics are observable. They do not execute MobilityData's validation-rule engine against both the static GTFS and realtime feed.

Canonical validator execution remains the next P0 gate.
