# ERRATA — Technical Reality LOCAL_STUB Results v0.1

**Evidence state:** `LOCAL_STUB`  
**Purpose:** falsify the deterministic amendment mechanism before any live AssemblyAI claim.

## Verification result

`python -m pytest` → **1 passed**.

The single pytest test contains 19 explicit assertions covering the bounded local mechanism. This report intentionally does not convert the assertion count into a “test count.”

## Observed final state

- `change_id`: `ERR-204`
- correction produces revision `2`
- King Edward remains skipped
- Cumberland is restored
- end time becomes `10:00:00`
- the revision-1 hash differs from revision 2
- a stale reviewed hash is rejected
- artifacts derived from the earlier canonical hash become `STALE`
- the independent wire parser sees the corrected protobuf state
- direct final entry converges semantically with the corrected voice-path stub

## Evidence boundary

This local pass does **not** prove:

- live microphone input;
- AssemblyAI turn detection, barge-in, or tool-call lifecycle;
- audio-bound provenance;
- mid-session keyterm ablation;
- canonical/official GTFS-Realtime validator acceptance;
- third-party routing/consumer acceptance;
- voice advantage over keyboard/map input;
- operator desirability or agency deployment.

## Falsification status

**Not falsified locally.**

The deterministic core survives the bounded LOCAL_STUB experiment. `Prototype Killer` remains blocked pending the live experiment.
