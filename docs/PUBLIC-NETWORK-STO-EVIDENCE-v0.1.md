# ERRATA — Public-Network STO Evidence v0.1

**Gate:** Representative Public-Network Scenario  
**Verdict:** PROVEN in bounded public-data / local-mutation scope  
**Provider:** Société de transport de l'Outaouais (STO)  
**Workflow run:** `36674052762`  
**Passing source head:** `af580504d26b00f51c1db954272597d8a82307a7`  
**Evidence artifact ID:** `11078928665`  
**Evidence artifact digest:** `sha256:4998dd1c8a42cb136ec8b86be7600c95c649b6040f087db32729bc9a9e5ce339`

## 1. Public source provenance

Official planned-service GTFS source:

`https://contenu.sto.ca/GTFS/GTFS.zip`

Downloaded in CI:

`2026-09-30T05:35:00.820608+00:00`

HTTP Last-Modified:

`Mon, 28 Sep 2026 03:49:00 GMT`

Source ZIP:

- bytes: `4,403,933`
- SHA-256: `a7e1f22955084828484cca5e8f1ebff9e785c70984ad5dd93b872a5d64ace6e4`

Service date under test:

`20260930`

The source is the STO's public planned GTFS dataset. The local ERRATA output is **not** an STO-published realtime feed and is not an agency production integration.

## 2. Required STO attribution

> Le présent service intègre les données ouvertes fournies par la Société de transport de l'Outaouais (STO). La STO n'est pas responsable de l'exactitude de l'information générée par cette application. Dernière mise à jour : 2026-09-28.

This attribution is preserved in the evidence manifest.

## 3. Canonical public-network scenario

Selected bounded route:

- route ID: `15`
- route short name: `15`
- route long name: `DES ÉRABLES`
- GTFS direction ID: `0`
- reference trip: `62759262`
- service date: `20260930`
- start time: `16:37:00`

Initial spoken/direct-entry-equivalent instruction:

`Route 15 direction 0, skip SAINT-LOUIS/Av. GATINEAU and ARRÊT DE COURTOISIE Érables/Tire until 17:22.`

Initial result:

- amendment applied;
- same canonical `ERR-PUBLIC-STO-001` change identity;
- both selected public GTFS stops staged as skipped.

Correction:

`Wait, keep ARRÊT DE COURTOISIE Érables/Tire. Make it 17:52.`

Final materialized intent:

- `SAINT-LOUIS/Av. GATINEAU` / stop `3396` remains skipped;
- `ARRÊT DE COURTOISIE Érables/Tire` / stop `7051` is restored;
- end time becomes `17:52:00`;
- revision becomes `3`;
- final state hash:
  `eb433070258612cba763d66937fee11c0c3c1aeea897da764a38eb2bf1be9664`.

## 4. Public-network consequence

The corrected state resolves against the actual public GTFS schedule and produces at least one affected scheduled trip and at least one skipped stop-time.

The generated GTFS-Realtime TripUpdates artifact:

- bytes: `105`
- SHA-256: `c486f610ab6faddac3ff83104f43233a1f13cc053720f6b50108ad6e62cfb87e`

This is a local derived artifact over public schedule data. It was not submitted to STO systems.

## 5. Independent official-bindings consumer

MobilityData official Python GTFS-Realtime bindings decoded the exact protobuf.

Observed:

- GTFS-Realtime version `2.0`;
- route ID `15`;
- direction ID `0`;
- trip ID `62759262`;
- stop `3396` as SKIPPED;
- stop `7051` absent from the skipped set.

Consumer assertions: **PASS**.

Consumer result SHA-256:

`5ea18f318cf4ee439fa2ae43a38ca279ebf3d4481b97ad68b16b5745b793f41e`

## 6. Canonical MobilityData validator

Validator:

`MobilityData/gtfs-realtime-validator`

Pinned source commit:

`7041fa3fcaf674bf730e17325c179d329cdff6f2`

The validator consumed:

- exact STO static GTFS SHA-256
  `a7e1f22955084828484cca5e8f1ebff9e785c70984ad5dd93b872a5d64ace6e4`;
- exact TripUpdates.pb SHA-256
  `c486f610ab6faddac3ff83104f43233a1f13cc053720f6b50108ad6e62cfb87e`.

Result:

- process exit code: `0`;
- blocking ERROR groups: `0`;
- WARNING groups: `1`;
- result SHA-256:
  `0a24f7f37f0bba2c0303a447a8aa19be27a4656dc194553f30c10d7d9b5c4234`.

Retained warning:

- `W002 vehicle_id not populated`.

ERRATA does not fabricate a vehicle identity for a locally authored service-change TripUpdate merely to silence a recommendation.

## 7. What this proves

In the bounded public-data scope, ERRATA now proves:

- deterministic entity resolution against non-synthetic GTFS route/stops;
- service-date-aware consequence selection;
- same-identity amendment/correction semantics on real schedule data;
- local GTFS-Realtime serialization using real public trip/stop identifiers;
- independent official-bindings consumption;
- canonical GTFS-Realtime validator acceptance with zero ERROR groups;
- evidence binding to the exact public source dataset.

## 8. What this does not prove

This does not establish:

- agency authorization to publish;
- live STO production integration;
- actual operational disruption;
- actual passenger impact;
- operator adoption;
- vehicle identity;
- realtime feed freshness/SLA;
- voice superiority.

## 9. Gate consequence

Promote:

- `Public-Network Scenario → PROVEN`
- public-data bounded `Entity Resolution → PROVEN`
- public-data bounded `Consequence Calculator → PROVEN`
- `Real Consequence — PUBLIC DATA / LOCAL MUTATION → PROVEN`

Keep:

- `Agency Live Integration → BLOCKED`
- `External Operator Evidence → BLOCKED`
- `Voice-native Necessity → ACTIVE`.
