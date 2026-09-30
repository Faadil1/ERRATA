# ERRATA

**Working concept:** versioned spoken amendments for transit service changes.

ERRATA converts self-correcting live speech into minimal, typed amendments to **one staged ServiceChange**. Speech recognition may be probabilistic; canonical mutation, validation, revisioning, artifact invalidation, and commit authority are deterministic and human-controlled.

> One change. One identity. Spoken corrections amend the same truth — they never fork it.

## Current project state

Lifecycle: **DELIVER**  
Concept lock: **v2, relocked**  
Bounded Technical Reality / Prototype Killer: **PROVEN**  
Living PRD: **PROVEN**  
Post-Vertical-Slice Depth Gap Review: **PROVEN**  
Brand: **ERRATA is still a working name; Naming / Collision Gate remains ACTIVE**

Canonical product requirements:

- [Living PRD v0.1](docs/PRD-v0.1.md)
- [Post-Vertical-Slice Depth Gap Review v0.1](docs/POST-VERTICAL-SLICE-DEPTH-GAP-REVIEW-v0.1.md)
- [Conditional Gateway Registry v0.2](docs/CONDITIONAL-GATEWAY-REGISTRY-v0.2.md)

## What is proven

In bounded credentialed runs, ERRATA has demonstrated:

- live AssemblyAI Streaming STT feeding the shared deterministic core;
- one `change_id` across spoken amendments;
- revision/hash-bound canonical state;
- human-owned mutation boundaries using immediate ENTER + ForceEndpoint;
- minimal correction on the canonical Route 55 scenario;
- review/refusal on unresolved explicit cues;
- stale reviewed-hash rejection and explicit human commit authority;
- self-bound runtime/evidence manifests;
- exact state continuity across deliberate streaming reconnect;
- successful post-reconnect amendment;
- voice/direct-entry semantic convergence;
- near aggregate timing parity in one local two-phase voice-vs-keyboard comparison.

These are bounded prototype claims, not production claims.

## Current architecture

```text
microphone
  ↓
AssemblyAI Streaming STT
  ↓
provider transcript fragments
  ↓
human transaction boundary
  ↓
bounded parser
  ↓
typed pending operations
  ↓
deterministic resolution + validation
  ↓
pure reducer
  ↓
ServiceChange(change_id, revision, state_hash)
  ↓
consequences / artifacts
  ↓
human hash-bound commit
  ↓
transit output adapter
  ↓
external validator + independent consumer   ← next P0
```

The managed Voice Agent path is retained as a sponsor-native comparison surface, not the authoritative mutation boundary.

## Current truth boundary

Do **not** claim:

- production voice reliability;
- live agency integration;
- controller adoption;
- production safety;
- public-network mutation;
- external/canonical GTFS-RT acceptance;
- independent consumer acceptance;
- general voice superiority.

## Next P0 — External Acceptance Slice

The next delivery workstream is:

```text
ERRATA serializer
  → external/canonical GTFS-RT validation
  → independent consumer assertion
  → evidence receipt
```

This is deliberately ahead of visual polish. The terminal prototype already proves the central mechanism; the next risk is whether the generated transit artifact is independently valid and consumable.

After that:

1. operator review surface;
2. public-network scenario;
3. external operator/user evidence;
4. judge-ready deterministic demo and hostile Q&A;
5. as-built reconciliation.

## Run deterministic tests

```bash
python -m pip install -r requirements.txt
python -m pytest
```

## Run the controlled live harness

```bash
python -m pip install -r requirements-live.txt
python scripts/run_controlled_streaming.py --service-date 20260929 --start-time 09:00:00
```

The live harness is an experiment surface, not the final operator UX.
