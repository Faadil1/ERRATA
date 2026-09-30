# ERRATA — Public-Network Source: STO GTFS v0.1

**Status:** ACTIVE  
**Gate:** Public-Network Scenario  
**Source authority:** Société de transport de l'Outaouais (STO)

## Official source

Developer/open-data page:

`https://www.sto.ca/affaires/espace-developpeurs-donnees-ouvertes/`

Static GTFS download:

`https://contenu.sto.ca/GTFS/GTFS.zip`

The official STO page states that:

- planned GTFS data is publicly available without registration/authentication;
- the planned dataset is updated automatically every 24 hours;
- use is subject to STO's open-data terms.

ERRATA uses only the public scheduled GTFS ZIP for this slice. No STO GTFS-Realtime API key is required or used.

## Truth boundary

The downloaded network data is public/non-synthetic STO schedule data.

The service change created by ERRATA is **not** an STO production change, is not submitted to STO systems, and must not be described as an agency-issued disruption or live operational instruction.

Correct phrasing:

> ERRATA ran its amendment mechanism against a version-bound public STO GTFS schedule dataset.

Incorrect phrasing:

> ERRATA changed STO service.

## Scenario-selection rule

The CI runner selects a bounded route/direction/trip/stops/time window from the downloaded feed using deterministic constraints:

- service active on the requested service date;
- explicit GTFS `direction_id` rather than fabricated east/west semantics;
- at least one active trip in the effective window;
- two internal stops whose names resolve uniquely on the route/direction;
- final corrected state produces at least one real scheduled affected trip and at least one skipped stop-time.

The selected scenario is written to `scenario.json`; it is evidence, not a hard-coded agency claim.

## Required proof chain

`official STO GTFS ZIP → SHA/provenance → shared ERRATA core → correction on same change_id → TripUpdates.pb → MobilityData official bindings → MobilityData canonical GTFS-RT validator`

## Promotion criteria

`Public-Network Scenario → PROVEN` only if:

1. source download succeeds from the official STO URL;
2. source SHA and response metadata are preserved;
3. service-calendar filtering is applied for the scenario date;
4. initial amendment and correction both apply through the shared core;
5. final state restores the second stop and retains only the intended skipped stop;
6. public-network artifact is independently parsed;
7. canonical validator executes against the exact downloaded static GTFS source;
8. validator/consumer outputs are evidence-bound;
9. no agency-live/production claim is made.
