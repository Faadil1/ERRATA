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


## External Acceptance Slice — consumer subgate closed

The official MobilityData Python bindings now consume the bounded ERRATA TripUpdates.pb in CI.

Promoted:

`Independent Consumer = PROVEN`

Still open:

`External / Canonical GTFS-RT Validation = BLOCKED`

Do not treat successful protobuf parsing as validator acceptance.

Next implementation target is MobilityData's `gtfs-realtime-validator` batch rule engine against:

- the packaged `gtfs_static.zip`;
- the exact `rt/TripUpdates.pb` SHA already consumed by official bindings.

Preserve validator source/version identity, command, stdout/stderr, JSON results, exit code, and input hashes.


## External Acceptance Slice closed

The bounded output now has two independent external checks:

- MobilityData official Python bindings parse + semantic assertions: PASS;
- MobilityData canonical validator rule engine: PASS with zero ERROR groups.

Two warnings remain intentionally visible: vehicle_id absent and deterministic CI timestamp freshness.

The next P0 is the operator review surface. It must use the existing shared product core and expose:

- change_id;
- revision/hash;
- input transcript/direct entry;
- pending / applied / review-required state;
- semantic diff;
- validation/refusal reason;
- consequence summary;
- artifact freshness;
- explicit human commit;
- evidence/truth label.

After the surface, run the hero scenario on public/representative non-synthetic GTFS data before making broader product claims.


## Operator surface handover

The local operator review UI is implemented over the shared Python core.

Run:

`python scripts/run_operator_surface.py`

Then open:

`http://127.0.0.1:8765`

Required human visual check before promoting the surface:

1. initial instruction renders rev2 + semantic diff;
2. correction renders rev3, Cumberland restored, end 10:00;
3. malformed correction renders REVIEW_REQUIRED with no hash/revision drift;
4. prior hash commit renders STALE_REVIEW;
5. current reviewed hash commits with authority `human_web_review`;
6. external validator evidence and warning truth boundary are legible above the fold / evidence rail;
7. responsive layout does not hide current truth or commit context.

After this visual check, the next depth target is the representative public-network GTFS scenario.


## Human visual review delta

The first browser recording showed that the core was correct but the UI encouraged the wrong reference-demo order: rev2 was committed before the correction.

The corrected surface now:

1. shows the hero walkthrough explicitly;
2. keeps current operational truth above the fold;
3. warns that committing rev2 will intentionally seal the change before the correction;
4. disables authoring after COMMITTED;
5. shows protected-action receipts clearly;
6. preserves the real backend rule that a valid rev2 may still be committed if an operator truly intends that.

Next human check should follow the visible stepper rather than relying on external instructions. If the corrected recording reads cleanly without explanation, promote `Operator Review Surface` / local `Real-user Surface` within the synthetic-fixture scope.


## Operator surface promotion

The corrected human browser recording passes the bounded local visual/runtime checkpoint.

Promoted:

- `Operator Review Surface = PROVEN`
- `Real-user Surface = PROVEN`

Scope is explicitly local + synthetic fixture.

Do not reinterpret this as:

- external controller validation;
- production usability evidence;
- live agency integration.

Next P0 is the **Representative Public-Network Scenario**:

1. select a public/non-synthetic GTFS source;
2. bind exact dataset provenance/version;
3. identify a route/direction/stops/time window that supports the hero mechanism;
4. run same-identity amendment + correction;
5. serialize output;
6. run official bindings consumer;
7. run canonical validator;
8. preserve evidence and update truth boundary.


## Public-network P0 closed

The public/non-synthetic GTFS depth gate is now closed using the STO public planned feed.

Canonical public scenario:

- Route 15 / DES ÉRABLES
- service date 20260930
- trip 62759262
- stop 3396 remains skipped
- stop 7051 is restored
- corrected end 17:52
- final rev3 hash eb433070258612cba763d66937fee11c0c3c1aeea897da764a38eb2bf1be9664

The same public-data-derived TripUpdates.pb passed:

- MobilityData official bindings;
- pinned MobilityData canonical validator;
- zero ERROR groups.

Keep the STO attribution and disclaimer attached whenever this source is shown.

Next workstream should target **external operator evidence / voice workflow value**. If representative operator access cannot be obtained within the remaining submission window, preserve that gate as BLOCKED and move to deterministic judge demo + hostile Q&A rather than inventing user validation.


## Human checkpoint

External operator evidence cannot be self-generated by the build team.

Protocol is ready at:

`docs/EXTERNAL-OPERATOR-TRIAL-PROTOCOL-v0.1.md`

If a representative external transit-operations participant is available, run the 10–15 minute protocol and preserve both positive and negative observations.

If no representative participant is available in the submission window, leave `External Operator Evidence = BLOCKED` and proceed with judge-demo rehearsal using:

`docs/JUDGE-DEMO-SCRIPT-v0.1.md`

Do not fabricate or substitute builder feedback for external operator evidence.


## Judge packaging checkpoint — 2026-09-30

The strengthened CI rerun on functional head `d03db942513e30501a7e68bf037a36dcb4701cf8` completed successfully:

- workflow: `technical-reality`;
- run: `36674855222`;
- jobs: `local-stub`, `live-adapter-contract`, `public-network-sto`, and `external-acceptance` all SUCCESS.

Latest revalidation artifacts from that run:

- public-network STO: `11079153984`, digest `sha256:bd4754995ef216500f7f91ff1fc437dbec1a2fedb46aa78cd5f14da94c0239f9`;
- external acceptance: `11079179121`, digest `sha256:468e61a6392cfb84ce212946a6d05816594e8d8319ece0a815888af1536bc0c6`;
- local stub: `11079029513`, digest `sha256:ad736dad62b4dade9e56e7d8ca6c7caa3f7f1c84fb87b138826089754c7e1827`.

The original public-network closure receipt `11078928665` / `sha256:4998dd...` remains the historical canonical closure artifact. The latest rerun is a separate revalidation package and does not overwrite that history.

Judge packaging is now materialized in:

- `docs/JUDGE-DEMO-PACK-v0.1.md`
- `docs/JUDGE-HOSTILE-QA-v0.1.md`

Gate truth remains:

- `External Operator Evidence = BLOCKED` until a representative external participant executes the protocol;
- `Voice-native Necessity = ACTIVE`;
- `DEMO = ACTIVE` until a complete 90–120 s rehearsal/recording passes the demo-pack checklist;
- `Agency Live Integration = BLOCKED`.

The next human action is a full judge-demo rehearsal. Do not substitute builder rehearsal for external operator evidence.


## Live Product Integration correction — 2026-09-30

A product-depth gap was identified before judge rehearsal: the existing browser operator surface was a local review/direct-entry interface, while the credentialed AssemblyAI voice proofs lived in separate terminal experiments. The product therefore **was not yet an integrated voice web application**, and no Cloudflare public runtime had been deployed.

This changes the next P0.

Implemented in the local browser surface on the feature branch:

- server-minted short-lived AssemblyAI Streaming v3 token;
- browser microphone capture;
- AudioWorklet PCM16/16 kHz path;
- direct browser WebSocket to AssemblyAI using the temporary token;
- provider transcript buffering with zero automatic mutation;
- explicit human ForceEndpoint / Apply spoken turn boundary;
- `POST /api/amend/voice`;
- voice transcript routed through the same existing ERRATA parser/resolver/validators/reducer as direct entry;
- distinct transaction provenance `assemblyai_browser_voice_human_boundary`;
- CI coverage of the shared-core voice mutation endpoint.

Truth boundary:

- this implementation is **not yet credentialed-browser proven**;
- the prior terminal AssemblyAI evidence remains valid bounded technical proof;
- the local operator surface remains valid direct-entry/review proof;
- neither proof may be substituted for integrated product evidence.

Cloudflare remains not deployed.

Canonical deployment target is now documented at:

`docs/LIVE-PRODUCT-INTEGRATION-CLOUDFLARE-v0.1.md`

Current gates:

- `Integrated Browser Voice Surface = ACTIVE`;
- `Cloudflare Public Runtime = BLOCKED`;
- `Cloudflare State Continuity = BLOCKED`;
- `Live Product Integration = BLOCKED`;
- `DEMO = BLOCKED`;
- `External Operator Evidence = BLOCKED` independently.

Next checkpoints in order:

1. credentialed local browser microphone run proving voice → same core → revision semantics;
2. Cloudflare Worker + static assets + stateful session implementation;
3. public deployment with AssemblyAI key stored only as secret;
4. public-runtime end-to-end voice / negative / stale-review / commit proof;
5. only then judge-demo rehearsal.


## Integrated browser voice proof harness ready

The local browser voice path is now ready for a credentialed human run.

Implementation hardening completed before the run:

- AssemblyAI Streaming v3 temporary token remains server-minted; permanent API key is never returned to the browser;
- browser audio is PCM16 mono 16 kHz;
- AudioWorklet output is buffered into ~100 ms frames rather than tiny render-quantum packets;
- Streaming connection uses `universal-3-5-pro`, `mode=max_accuracy`, and formatted turns;
- human `Apply spoken turn` sends `ForceEndpoint`;
- provider turns remain non-mutating until that human boundary;
- voice mutation records AssemblyAI session ID and boundary metadata;
- `/api/session-receipt` exports exact git SHA, worktree-clean flag, state, validation, history, and voice provenance;
- browser exposes **Export proof receipt**.

Execution protocol:

`docs/BROWSER-VOICE-PROOF-PROTOCOL-v0.1.md`

Gate remains:

`Integrated Browser Voice Surface = ACTIVE`

until a real microphone run produces the required receipt. Static/CI coverage is not sufficient for promotion.


## Interactive voice guidance correction

Human browser review showed that the first integrated voice surface behaved like a capture harness rather than a true operator copilot: it transcribed and buffered speech but did not greet, interpret, guide, or recover conversationally enough.

The product-depth correction is now implemented locally:

- spoken greeting on successful voice connection;
- AssemblyAI provider turns reconciled by turn identity instead of blindly concatenated;
- non-mutating `POST /api/preview/voice` runs the transcript against a disposable copy of canonical state;
- safe interpretation is summarized to the operator before Apply;
- incomplete/ambiguous input produces contextual guidance and keeps Apply disabled;
- browser voice guidance can be repeated or muted;
- microphone frames are suppressed while browser guidance speech is playing to reduce self-capture;
- canonical revision/hash remain unchanged during preview/guidance;
- explicit human Apply remains the only mutation boundary.

Truth boundary:

- this is implemented and CI-testable;
- it is **not yet PROVEN by a credentialed human microphone run**;
- Cloudflare Public Runtime, Cloudflare State Continuity, Live Product Integration, DEMO, and External Operator Evidence remain BLOCKED.

Next checkpoint remains the credentialed local browser run, now using the upgraded interactive protocol in `docs/BROWSER-VOICE-PROOF-PROTOCOL-v0.1.md`.


## Neural guidance voice + echo guard correction

Human review of the Edge `Microsoft Aria Online (Natural)` fallback confirmed that browser Web Speech remains audibly synthetic and that spoken guidance can still be picked up again by the microphone in some conditions.

Implemented local product delta:

- server-side `POST /api/tts/guidance` using OpenAI `gpt-4o-mini-tts`;
- default neural voice `cedar`, alternate `marin`;
- server-only `OPENAI_API_KEY`; the browser receives only generated audio;
- `GET /api/voice-capabilities` truthfully reports whether neural TTS is available;
- visible `AI-generated voice` disclosure when the neural engine is active;
- Edge/Windows voice remains an automatic fallback when neural TTS is unavailable;
- strict half-duplex echo guard suppresses microphone frames while guidance is being prepared/played;
- 750 ms post-playback cooldown before microphone frames resume;
- overlapping guidance requests are cancelled/invalidated so stale TTS cannot play over a newer operator state.

Current truth:

- implementation + fallback CI path can be proven automatically;
- `Neural Guidance Voice = ACTIVE` until a real browser run with `OPENAI_API_KEY` proves neural playback;
- `Echo / Self-Capture Guard = ACTIVE` until a human run shows that ERRATA's own speech is not re-transcribed;
- Integrated Browser Voice, Cloudflare Public Runtime, Live Product Integration, and DEMO are not promoted by this implementation alone.


## AI33 Pro guidance provider substitution

The previously planned OpenAI TTS dependency is superseded. The user already owns and has a proven AI33 Pro integration, so ERRATA now reuses that provider instead of requiring a new OpenAI API key.

Canonical implementation:

- secret: `AI33_API_KEY`;
- base URL: `https://api.ai33.pro`;
- TTS create: `POST /v3/text-to-speech` with multipart `text`, `voice_id`, `speed`;
- task polling: `GET /v1/task/{task_id}` until `status=done`;
- audio source: `metadata.audio_url` / compatible output URL;
- default ERRATA voice: `Zach / George V2` (`elevenlabs_yG30oCchdy9JCUsKqYfV`);
- speed: `0.98`;
- browser receives generated audio only, never the AI33 key;
- Windows persistent User/Machine `AI33_API_KEY` is reused automatically when not already present in the current process;
- Edge/Windows TTS remains fallback-only;
- UI surfaces AI33 generation latency and credit cost when returned;
- half-duplex speech guard + 750 ms echo cooldown remain mandatory.

Truth boundary:

- code path and no-key fallback are CI-testable;
- `AI33 Guidance Voice = ACTIVE` until a credentialed local browser run proves actual AI33 generation/playback and measures latency;
- `Echo / Self-Capture Guard = ACTIVE` until a human run confirms ERRATA speech is not re-transcribed;
- no Cloudflare/public-runtime promotion occurs from this local provider substitution alone.

## AI33 live browser review — retry semantics + latency correction

Human browser video review confirmed:

- AI33 Pro guidance audio now plays successfully through Zach / George V2;
- observed generation examples were approximately 6.80 s / 104 credits and 9.24 s / 176 credits;
- this is functionally successful but too slow to treat as conversationally complete;
- AssemblyAI sometimes misheard Cumberland as Cubberland and skip as keep;
- after a rejected interpretation, subsequent spoken retries were appended to the prior rejected buffer, producing repeated Route 55 transcripts and making recovery worse.

Implemented correction:

- rejected / clarification-required attempts mark the next spoken turn as a fresh attempt;
- the next utterance clears the rejected buffered turns instead of concatenating indefinitely;
- AssemblyAI streaming now receives keyterms for King Edward and Cumberland;
- repeated AI33 guidance audio is cached in-process after first successful generation;
- cache hits report 0 new credits and are labeled in the UI;
- first-generation latency remains an ACTIVE product concern and must be measured rather than hidden.

Truth:

- AI33 Guidance Voice is functionally observed locally but remains ACTIVE pending a clean proof run with retry behavior and latency evidence;
- Echo / Self-Capture Guard remains ACTIVE pending explicit proof;
- Conversational Latency / Operational Economics remains ACTIVE.

## Live browser semantic-time regression + draft reset correction

Human browser video review exposed a blocking semantic bug even though AI33 guidance audio was functioning:

- AssemblyAI formatted `9:30` as `9: 30` in the completed transcript;
- the bounded parser treated that spaced clock separator as hour-only `9`, causing ERRATA to preview and stage `09:00` instead of `09:30`;
- the operator then repeated the full instruction while the first preview was already READY_TO_APPLY, and the browser appended the second completed turn to the first draft.

Corrections implemented:

- controlled transcript normalization now collapses numeric clock separators with surrounding whitespace (`9:30`, `9: 30`, `9 : 30` -> equivalent);
- regression tests prove spaced realtime STT clock formatting preserves `09:30:00` and never degrades to `09:00:00`;
- every new spoken turn after a completed preview starts a fresh draft until the prior preview is explicitly applied;
- UI now exposes `AI33 GENERATING VOICE` -> `ERRATA SPEAKING` -> `ECHO COOLDOWN` -> `VOICE CONNECTED` so the operator knows listening is intentionally suspended during the slow AI33 reply.

Truth:

- the observed video does NOT promote Integrated Browser Voice because it staged the wrong end time;
- STT Clock-Time Fidelity remains ACTIVE until a clean human rerun proves `9: 30` -> `09:30` end-to-end;
- AI33 Guidance Voice remains ACTIVE pending clean latency/playback evidence;
- Echo / Self-Capture Guard remains ACTIVE pending explicit no-self-transcription evidence.
