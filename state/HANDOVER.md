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

### Commit-authority proof completed

In the same run:

- `commit 8d6f83a9a20d` → refused as stale;
- `commit 320221743ffd` → accepted;
- receipt authority: `human_terminal_command`;
- final snapshot: `status=COMMITTED`, revision `3`, no pending calls, same `change_id`, final hash `320221743ffda8433ac5abfbd5a5565aed96c166e87360955a51961dd7ca6f64`.

Promotable in bounded LIVE scope:

- stale reviewed-hash rejection;
- human commit authority;
- current-state binding at commit.

Preserve `evidence/controlled-streaming-v0.1/20260929-143810` unchanged for audit and ingest it before claiming the evidence packet itself is canonical.


## Evidence archive audit completed

The uploaded controlled-Streaming ZIP was audited.

Archive SHA-256:

`bd0866451ec4eecc97484f80173665d062b92fbfab79b7eb7a33aaa70a8136b0`

The file-backed core proof is internally consistent:

- two final live transcripts;
- two finalized mutation receipts;
- continuous rev1→rev2→rev3 hash chain;
- all blocking validators PASS;
- independent recomputation of rev2/rev3 canonical state hashes matches the archive;
- rev3 semantics match the intended amendment.

The original archive does **not** contain the later stale-commit refusal / accepted human commit or a runtime git manifest. Those remain supported by the terminal evidence from the same run, not by the ZIP alone.

The branch now includes hardened evidence instrumentation for the next run. Do not repeat the old runner merely to reconfirm the same transition; the purpose of the next controlled pass is to produce a self-contained evidence packet.

See:

- `evidence/controlled-streaming-v0.1/20260929-143810/AUDIT.md`
- `evidence/controlled-streaming-v0.1/20260929-143810/AUDIT-MANIFEST.json`


## Next workstream: Voice-native Necessity baseline

Implemented:

- `errata/live/direct_entry.py` — deterministic direct-entry application core;
- `scripts/run_keyboard_baseline.py` — timed keyboard baseline using the same parser/coordinator/reducer;
- `scripts/compare_voice_keyboard.py` — compares instrumented voice timing with keyboard timing and checks semantic-operation convergence;
- `docs/VOICE-VS-KEYBOARD-BASELINE-v0.1.md`.

Required order:

1. pull the latest branch;
2. run the hardened controlled Streaming scenario and complete stale/current hash commit tests;
3. quit normally so final evidence/manifest files are written;
4. run the keyboard baseline and type the same two sentences;
5. run the comparator against both evidence directories.

Do not promote `Voice-native Necessity` from speed alone. The result must be interpreted together with correction friction, error/refusal behavior, and the value of hands/eyes-free operation.


## Immediate-ENTER finding: partial correction leakage

The first immediate-ENTER live run is **not promotable** as a clean voice-native result.

A misheard correction `Wait, keep Cumberland, make it turn.` produced only `KEEP=Cumberland`. Because the existing end time remained valid, that subset advanced revision 2 → 3. This violated the intended all-or-review behavior for an utterance that explicitly signaled a second field change.

Do not commit or use that final state as evidence of a correct correction.

The branch now adds an unresolved-cue guard:

- explicit `make it` without a parsed END → REVIEW_REQUIRED;
- explicit `until` without a parsed END → REVIEW_REQUIRED;
- explicit SKIP/KEEP without a resolved stop target → REVIEW_REQUIRED;
- exact repeated operations from retry fragments are deduplicated;
- observed `ouest` is mapped to west.

Next live run should prove that the same misheard `make it turn` transcript leaves the canonical hash/revision unchanged.


## Atomicity retest finding: U-turn STT variant

The first unresolved-cue guard did not catch `make U-turn`, which was the provider transcript for the intended malformed time correction.

Observed bad transition:

`rev2 KEEP=Cumberland + unresolved make cue → partial KEEP applied → rev3`

That state must not be committed or treated as a valid correction result.

The parser now treats any unsupported `make ...` phrase with no resolved END value as review-only. A regression test covers the exact `make U-turn` transcript.

Next retest target:

- from clean rev2, transcript `Wait, keep Cumberland, make U-turn.`
- expected: `REVIEW_REQUIRED`
- expected revision/hash: unchanged at rev2
- then clean `Wait, keep Cumberland, make it 10.`
- expected: APPLIED rev3.
