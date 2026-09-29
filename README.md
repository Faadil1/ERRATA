# ERRATA

**Working concept:** spoken amendments for transit service changes.

ERRATA explores a narrow mechanism: self-correcting live speech should amend **one versioned staged service change**, not fork a new truth. Interrupted or superseded speech must not leak side effects; corrections must be minimal; outputs derived from an older revision must become stale; and a stale reviewed hash must never commit.

> One change. One identity. Every spoken correction stays on the same truth.

## Current project state

Lifecycle: **DESIGN**  
Workstream: **Technical Reality / Prototype Killer**  
Concept lock: **v2, relocked**  
Brand: **ERRATA is a working name; Naming / Collision Gate remains ACTIVE**

The repository currently contains a bounded `LOCAL_STUB` falsification harness. It does **not** prove a live AssemblyAI loop, controller desirability, agency publication, or production readiness.

## Local falsification harness

The current executable assertions cover:

- same `change_id` across revisions;
- minimal correction (only intended fields change);
- supersession history preservation;
- interrupted candidate discard with zero canonical side effect **in LOCAL_STUB only**;
- stale derived-artifact invalidation;
- stale reviewed-hash rejection;
- deterministic unknown-entity refusal and a bounded transit conflict;
- idempotent duplicate operation handling;
- semantic convergence with direct final entry;
- deterministic GTFS-Realtime-shaped protobuf serialization and an independent wire parser.

Run:

```bash
python -m pip install -r requirements.txt
python -m pytest
python -m errata.experiment
```

## Truth boundary

Current evidence label: **`LOCAL_STUB`**.

Do not claim yet:

- `Live Core Loop`;
- AssemblyAI load-bearing behavior;
- real barge-in safety;
- external/canonical GTFS-RT validator acceptance;
- third-party consumer acceptance;
- real agency integration or publication;
- operator desirability;
- production-ready transit operations.

## Next executable gate

The next required experiment is the live AssemblyAI path:

`mic → AssemblyAI → candidate op → PENDING → reply.done completed/interrupted → APPLY/DISCARD → canonical reducer → GTFS-RT → independent validation/consumer → voice-vs-keyboard baseline`

The canonical technical spec is in [`docs/TECHNICAL-REALITY-EXPERIMENT-SPEC-v0.1.md`](docs/TECHNICAL-REALITY-EXPERIMENT-SPEC-v0.1.md).
