# ERRATA — Hostile Judge Q&A v0.1

**Status:** READY FOR REHEARSAL  
**Purpose:** bounded answers for likely judge attacks  
**Rule:** answer only what the evidence supports

## 1. “Why not just use a form?”

A form is still useful for deliberate entry. ERRATA targets the correction moment: an operator can revise an already-staged change without re-entering the whole structure. The current evidence does not prove voice is universally faster; the bounded paired trial showed near aggregate parity overall, with voice faster only on the short correction.

## 2. “Why AssemblyAI?”

AssemblyAI is load-bearing for live speech capture in the controlled Streaming path. ERRATA deliberately does not delegate mutation authority to the speech provider. Provider output is accumulated, then admitted through a human-controlled boundary into deterministic parsing, validation, revision, and commit logic.

## 3. “What happens if the transcript is only partly right?”

If an utterance signals an incomplete operation, ERRATA returns `REVIEW_REQUIRED` and preserves the current revision/hash. This behavior was added after live runs exposed partial-correction leakage variants, then retested with a bounded live atomicity proof.

## 4. “What if the operator reviews rev2 but the state changes before commit?”

The commit is hash-bound. A prior reviewed hash is refused as `STALE_REVIEW`; the current reviewed hash is required for commit.

## 5. “Did you integrate with STO?”

No. ERRATA used the STO public planned GTFS dataset to resolve real public route/trip/stop identifiers and generate a local derived GTFS-Realtime artifact. Nothing was published into STO systems and no real service change was created.

## 6. “So the consequence is fake?”

The operational mutation is local, but the schedule identifiers and affected scheduled trip are resolved against real public STO GTFS data. The derived artifact was independently decoded by official MobilityData bindings and accepted by the pinned MobilityData canonical validator with zero ERROR groups. That proves bounded interoperability over public schedule data, not agency production impact.

## 7. “Why is W002 still there?”

The validator warns that `vehicle_id` is not populated. ERRATA does not fabricate a vehicle identity for a locally authored service-change TripUpdate merely to silence a recommendation. The warning is retained intentionally.

## 8. “Is this production safe?”

No production-safety claim is made. The project proves bounded mechanisms: same-identity revision, atomic refusal classes, hash-bound human commit, controlled live capture, reconnect continuity, external consumer/validator acceptance, and public-data consequence generation.

## 9. “What if AssemblyAI disconnects?”

A deliberate live reconnect test preserved the exact canonical revision/hash across a new AssemblyAI stream session, then continued the same in-memory ServiceChange and applied a subsequent valid correction.

## 10. “Why not let the model call the mutation tool directly?”

Credentialed testing showed managed conversational turn ownership could split operational sentences unpredictably. ERRATA therefore moved the authoritative path to controlled Streaming: probabilistic segmentation may happen upstream, but the human owns the consequential capture boundary and deterministic code owns mutation admission.

## 11. “Did an actual transit operator use this?”

Not yet. The external operator protocol is ready, but `External Operator Evidence` remains `BLOCKED` until a representative external participant completes it. Builder testing is not substituted for external validation.

## 12. “Does one external trial prove demand?”

No. The protocol explicitly treats one participant as bounded workflow evidence, not adoption, endorsement, or product-market fit.

## 13. “Is voice actually necessary?”

Still an open question. The current paired measurement rejects a blanket “voice is faster” claim. It supports viability for short corrections, but `Voice-native Necessity` remains `ACTIVE` pending stronger workflow evidence.

## 14. “What is the core differentiator?”

Corrections amend one canonical operational change with explicit revision semantics, safe refusal of incomplete corrections, stale-review invalidation, recomputed consequences, and protected human commit. The value is not transcription alone; it is controlled correction semantics.

## 15. “What would you build next?”

The highest-value unresolved product proof is external operator evidence and stronger workflow-value validation. The technical core is already deep enough that more generic voice tuning would be lower-value than representative-user evidence and judge-ready proof packaging.

## Claim firewall

Allowed:

- bounded credentialed live capture;
- controlled Streaming architecture;
- same-identity revision semantics;
- REVIEW_REQUIRED on evidenced incomplete-correction classes;
- bounded reconnect continuity;
- official bindings consumption;
- canonical validator acceptance;
- public STO schedule identifiers used locally;
- human hash-bound commit;
- local/public-data consequence generation.

Not allowed:

- production safety;
- agency integration;
- actual STO publication;
- actual service disruption;
- operator adoption;
- product-market fit;
- universal voice superiority;
- general production reliability.
