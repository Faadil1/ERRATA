# ERRATA — Public-Network Scenario Spec v0.1

**Status:** ACTIVE / discovery phase  
**Source:** official STO scheduled GTFS  
**Official static GTFS URL:** `https://contenu.sto.ca/GTFS/GTFS.zip`  
**Truth boundary:** public non-synthetic scheduled data; no agency integration claim

## Objective

Replace the synthetic network fixture with a current public GTFS-static dataset while keeping ERRATA's already-proven amendment mechanics, external consumer, and canonical GTFS-Realtime validation chain.

## Source decision

Use Société de transport de l'Outaouais (STO) scheduled GTFS because:

- STO publishes planned GTFS as open data;
- no authentication is required for the scheduled dataset;
- the publisher states the scheduled dataset is updated every 24 hours;
- the project can bind exact download provenance, SHA-256, and source timestamp before deriving a scenario.

The scenario must retain STO's required source attribution and must not imply STO endorsement, production integration, or responsibility for ERRATA-generated information.

## Discovery gate

Before locking a route/scenario:

1. download the official GTFS ZIP in CI;
2. record exact URL, byte size, SHA-256, HTTP metadata, and download timestamp;
3. extract only source files from that immutable download;
4. determine service active on the test date;
5. identify a route/direction with enough active trips/stops for a two-stop amendment;
6. record route, direction_id, headsign, two stop IDs/names, representative trip, and bounded time window;
7. do not yet claim the hero scenario is valid until the selected candidate is inspected.

## Scenario promotion criteria

A candidate can be locked only when:

- route and stop IDs exist in the downloaded source;
- direction meaning is not fabricated;
- stop names resolve unambiguously enough for the bounded parser or the test uses explicit typed operations;
- at least one affected trip exists in the chosen time window;
- the correction restores exactly one skipped stop and changes the window;
- same change identity/revision/hash invariants hold;
- resulting GTFS-Realtime output passes official bindings and canonical validator against the same public static source.

## Required attribution

When STO data are presented in the public-network surface/evidence, include the source notice required by STO's terms and the actual dataset update/download date.

## Non-claims

This phase does not prove:

- STO production integration;
- STO endorsement;
- live operational authority;
- real passenger impact;
- controller adoption;
- correctness of STO realtime Custom TripUpdate behavior.
