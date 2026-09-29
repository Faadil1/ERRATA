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
