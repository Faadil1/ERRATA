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


## Atomicity retest finding — U-turn STT variant

The first unresolved-cue guard did not catch `make U-turn`, which was the provider transcript for the intended malformed time correction. That caused a partial KEEP to apply at rev2 and advance to rev3. This state must not be committed or used as a correct-correction proof.

The parser now treats any unsupported `make ...` phrase with no resolved END value as review-only. A regression test covers the exact `make U-turn` transcript.

Next retest target: from clean rev2, `Wait, keep Cumberland, make U-turn.` must produce REVIEW_REQUIRED with unchanged revision/hash; then `Wait, keep Cumberland, make it 10.` should apply rev3.


## Partial correction atomicity retest passed

The next credentialed run preserved revision/hash when an incomplete explicit time correction was heard.

Key negative-path result:

- before malformed correction: rev2 / `8d6f83a9a20df286...`;
- parsed semantic subset: `KEEP=Cumberland`;
- unresolved cue: `END_TIME_AFTER_MAKE_IT`;
- outcome: `REVIEW_REQUIRED`;
- after malformed correction: still rev2 / same hash.

A clean retry then applied `KEEP=Cumberland + END=10` and advanced to rev3.

Before ending that same process, capture snapshot, stale/current commit behavior, final COMMITTED snapshot, and quit so the hardened recorder persists the full packet.


## Latest audited packet

`ERRATA-live-atomicity-20260929-175753.zip` is now the strongest self-bound controlled-Streaming evidence packet.

Runtime SHA: `c83f750cc3b7f8d26c936d92a0c2f6525605be30`.

Promoted from this packet:

- Evidence-to-Runtime Binding — LIVE
- ForceEndpoint Efficacy — LIVE
- Partial Correction Atomicity — LIVE
- bounded Evidence Integrity / Observability
- bounded Time to First Value measurement

Important limitation: the packet ended STAGED and contains no human commit receipts. Do not state that this ZIP proves commit authority; that claim remains tied to the earlier separate LIVE terminal run.

Voice-vs-keyboard is now characterized enough for the Prototype Killer: near aggregate parity in the one local immediate-ENTER trial, with faster keyboard initial entry and faster voice correction. Do not claim general voice superiority.

### Next workstream

Implement and run deliberate LIVE disconnect/reconnect recovery on the authoritative controlled-Streaming path. Required invariant:

1. reach a known canonical revision/hash;
2. disconnect the AssemblyAI transport deliberately;
3. no canonical mutation during transport failure;
4. reconnect without recreating the ServiceChange;
5. continue from the exact same revision/hash;
6. apply a clean subsequent correction successfully;
7. preserve evidence receipts for disconnect, reconnect, and state continuity.


## Recovery implementation ready

The controlled Streaming runner now accepts:

`reconnect`

Use it only after a known canonical checkpoint, preferably rev2.

Expected evidence sequence:

`HUMAN_RECONNECT_REQUEST → Terminate → TRANSPORT_DISCONNECTED → STREAM_BEGIN(new session) → TRANSPORT_RECONNECTED(same_revision=true, same_hash=true)`

Then continue with the clean correction and require APPLIED rev3.

This is bounded in-process transport recovery, not process-crash persistence.


## Recovery run result

The live reconnect mechanism itself passed:

- rev2/hash preserved exactly across deliberate transport shutdown;
- a new AssemblyAI stream session was established;
- same in-memory ServiceChange continued;
- post-reconnect snapshot matched pre-disconnect state.

But the first post-reconnect correction was mistranscribed as repeated `McKitten 10` variants. The parser saw only `KEEP=Cumberland` and allowed a partial mutation, so the broader Failure / Recovery gate remains open.

A new guard now treats KEEP/SKIP + an unbound time-like number/word with no parsed END as `UNBOUND_TIME_VALUE` → REVIEW_REQUIRED. The sender close race is also fixed.

Next credentialed test:

1. reach rev2;
2. reconnect and confirm same revision/hash;
3. say `Wait, keep Cumberland, ten.` and press ENTER;
4. require REVIEW_REQUIRED / unchanged rev2/hash;
5. say `Wait, keep Cumberland, make it 10.` and press ENTER;
6. require APPLIED rev3;
7. snapshot + quit.

That one run can re-prove broad partial-correction atomicity and close Failure / Recovery — LIVE.


## Prototype Killer promotion

The credentialed recovery retest passed the bounded recovery invariant.

Key facts:

- rev2/hash survived deliberate transport replacement exactly;
- a new AssemblyAI stream session was established;
- the same in-memory ServiceChange continued;
- a semantically complete post-reconnect correction applied rev3 successfully;
- repeated same correction attempts after rev3 were rejected without drift;
- normal quit no longer emitted the sender-close task exception.

Therefore:

- `Transport Recovery Continuity — LIVE = PROVEN`
- `Failure / Recovery — LIVE = PROVEN`
- bounded `Prototype Killer = PROVEN`

Do not overstate the latest run as a live proof of the new `UNBOUND_TIME_VALUE` guard. It was not isolated because accumulated fragments included valid END cues. That guard remains a focused follow-up, not a blocker for the bounded Prototype Killer.

Next workstream is no longer more voice-threshold tuning. Move to:

1. Living PRD;
2. Post-Vertical-Slice Depth Gap Review;
3. external GTFS-RT validation / independent consumer;
4. real-user/operator surface and evidence;
5. judge-ready deterministic demo / story / Q&A.


## DELIVER handover — product requirements locked

The living product source of truth is now:

- `docs/PRD-v0.1.md`
- `docs/POST-VERTICAL-SLICE-DEPTH-GAP-REVIEW-v0.1.md`

Do not widen scope before closing the P0 External Acceptance Slice.

Next implementation target:

`serializer → external/canonical validator → independent consumer → immutable evidence`

Acceptance for that slice:

1. generate the bounded final transit artifact from the existing shared core;
2. validate it using a path outside ERRATA's own parser;
3. consume it independently and assert the corrected final state;
4. bind validator/consumer output to runtime/state hash;
5. update the registry without implying agency production integration.

Spec Kit is now ACTIVE and should describe this P0 slice only, not the entire future product.
