# ERRATA — Controlled Streaming Failure / Recovery Test v0.1

## Goal

Prove that a deliberate live AssemblyAI transport interruption does not mutate canonical state and that ERRATA can reconnect in-process and continue the **same ServiceChange** from the exact same revision/hash.

This is the remaining hard Technical Reality / Prototype Killer delta for the authoritative controlled-Streaming path.

## Invariant

At the recovery boundary:

1. canonical revision/hash are recorded;
2. the live streaming transport is deliberately terminated;
3. transcript fragments are cleared;
4. no canonical operation is prepared or applied during the disconnect;
5. a new AssemblyAI streaming session is established;
6. revision/hash after reconnect must exactly equal the pre-disconnect values;
7. the same in-memory `ServiceChange` continues;
8. a subsequent clean spoken correction must apply normally.

## Operator run

Start:

```powershell
python scripts/run_controlled_streaming.py --service-date 20260929 --start-time 09:00:00
```

Then:

1. Speak `Route 55 west, skip King Edward and Cumberland until 9:30.`
2. Press ENTER immediately after speaking.
3. Require `APPLIED rev=2`.
4. Type `snapshot` and note the rev2 hash.
5. Type `reconnect`.
6. Require a new `[stt] Begin id=...` and:
   `[recovery] RECONNECTED same_revision=True same_hash=True ...`
7. Type `snapshot`; it must still be rev2 with the identical hash.
8. Speak `Wait, keep Cumberland. Make it 10.`
9. Press ENTER immediately.
10. Require `APPLIED rev=3`.
11. Type `snapshot`, then `quit`.

## Evidence receipts

The hardened recorder emits:

- `HUMAN_RECONNECT_REQUEST`
- client `Terminate`
- `TRANSPORT_DISCONNECTED`
- a second `STREAM_BEGIN`
- `TRANSPORT_RECONNECTED`
- `same_revision`
- `same_hash`
- normal post-recovery ForceEndpoint and mutation receipts
- final evidence manifest containing all observed stream session IDs

## Promotion rule

`Failure / Recovery — LIVE → PROVEN` only if:

- pre-disconnect and post-reconnect revision are identical;
- pre-disconnect and post-reconnect state hash are identical;
- no mutation occurs during the gap;
- a new stream session is observed;
- a valid post-reconnect correction applies on the same change identity.

This proves bounded in-process transport recovery only. It does not establish process crash recovery, machine restart recovery, or production high availability.
