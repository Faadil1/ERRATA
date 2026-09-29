# ERRATA — Concept Lock v2

## Locked residual mechanism

ERRATA converts self-correcting live speech into minimal, versioned amendments to one staged transit service change. Interrupted or superseded speech must not leak into canonical operational state. Each amendment recomputes deterministic transit consequences, invalidates outputs derived from older revisions, and requires explicit human commit against the reviewed state hash.

## Defensible novelty boundary

The project does **not** claim novelty for the generic pipeline `stage → validate → preview → approve → publish`. Prior-art work found strong analogues in infrastructure change management, network automation, airline/rail OCC systems, and transit service-adjustment products.

The scoped residual under test is:

1. self-repair-aware spoken authoring as ordered state-diff operations;
2. a minimal-correction invariant over a single versioned change identity;
3. interruption-safe transaction semantics where abandoned speech cannot leak a side effect;
4. deterministic transit-domain repair and independently checkable output.

## Claim firewall

Do not claim:

- “first voice-native operational compiler”;
- “no system does this”;
- invention of blast-radius preview;
- automatic synchronization of every real agency channel;
- GTFS-RT as the agency operational source of truth;
- safety-critical dispatch authority;
- rider-impact counts without supporting demand data.
