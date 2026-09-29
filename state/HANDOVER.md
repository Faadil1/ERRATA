# ERRATA — HANDOVER

## What the live runs established

Credentialed local microphone runs reached AssemblyAI successfully.

Observed:

- real `session.ready`;
- live speech start/stop;
- real final user transcripts;
- one real `stage_transit_change` tool call;
- safe deterministic rejection of a bad direction transcript (`West Cape`);
- a later correct tool call;
- `PREPARED → APPLIED` on the same deterministic reducer, advancing revision 1 → 2;
- dynamic session update after the successful apply.

The same runs also showed that the managed Voice Agent API's conversational turn boundaries are too irregular for ERRATA's primary structured operational-dictation path in this terminal experiment. Commands and corrections were repeatedly split into separate final turns.

## Current architectural decision

Keep the managed Voice Agent adapter as:

- a sponsor-native integration;
- an interruption / barge-in experiment surface;
- a comparison baseline.

Move the primary Prototype Killer capture experiment to **AssemblyAI Universal-3.5 Pro Realtime streaming with ERRATA-owned controlled boundaries**.

New components:

- `errata/live/controlled_parser.py` — bounded operation extraction from accumulated transcripts;
- `errata/live/controlled_streaming.py` — raw Streaming STT transport, turn accumulation, ForceEndpoint, evidence capture;
- `scripts/run_controlled_streaming.py` — human-controlled apply runner.

The transaction boundary is now:

`speech fragments → AssemblyAI Streaming STT → accumulated transcript buffer → human apply / ForceEndpoint → bounded parser → PREPARE → validators → APPLY`

Provider end-of-turn decisions are transcription segmentation only; they do not authorize mutation.

## Next run

```bash
git pull
python -m pytest
python scripts/run_controlled_streaming.py --service-date 20260929 --start-time 09:00:00
```

Then:

1. speak the complete Route 55 instruction;
2. type `apply`;
3. require `APPLIED rev=2`;
4. speak the Cumberland/time correction;
5. type `apply`;
6. require `APPLIED rev=3`;
7. type `snapshot`.

The expected invariant is the same:

- same `change_id`;
- revision 1 → 2 → 3;
- King Edward remains skipped;
- Cumberland is restored on revision 3;
- end time becomes 10:00;
- unrelated fields do not drift.

## What remains separate

Do not conflate this controlled Streaming proof with:

- real barge-in side-effect safety;
- Voice Agent API session-resume proof;
- external GTFS-RT validation;
- operator desirability;
- public-network realism;
- production voice UX.

Those remain separate gates.


## Successful controlled Streaming run

A credentialed run on exact SHA `6efbd6036647998aeb4d9efe0974c194a9819d35` completed the central mechanism:

- revision `1 → 2`: Route 55 west; skip King Edward + Cumberland; end 09:30;
- revision `2 → 3`: KEEP Cumberland; end 10:00;
- same `change_id = ERR-LIVE-001`;
- final skipped set contains only King Edward;
- final end time = `10:00:00`;
- no unresolved items;
- no pending tool calls.

Final observed state hash:

`320221743ffda8433ac5abfbd5a5565aed96c166e87360955a51961dd7ca6f64`

This is sufficient to promote the bounded **Technical Reality Check** and controlled-Streaming **Live Core Loop**. It is not sufficient for production, adoption, recovery, or barge-in claims.

### Immediate next checkpoint

Before ending the current process:

1. `commit 8d6f83a9a20d` → must refuse stale reviewed state;
2. `commit 320221743ffd` → must accept current reviewed state;
3. `snapshot`;
4. `quit`.

Preserve `evidence/controlled-streaming-v0.1/20260929-143810` unchanged for audit.
