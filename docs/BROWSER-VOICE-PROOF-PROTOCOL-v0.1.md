# ERRATA — Integrated Browser Voice Proof Protocol v0.1

**Status:** READY FOR HUMAN EXECUTION  
**Gate:** Integrated Browser Voice Surface  
**Environment:** local browser product surface  
**Provider:** AssemblyAI Streaming v3 / Universal-3.5 Pro Realtime  
**Mutation authority:** explicit human `Apply spoken turn`

## Purpose

Prove that the actual browser product, not a separate terminal harness, uses AssemblyAI live capture and then routes the finalized spoken instruction through the same ERRATA parser, resolver, validators, reducer, revision/hash model, and protected commit flow.

This protocol does not prove Cloudflare deployment, external operator validation, agency integration, or production readiness.

## Prerequisites

- checkout branch `technical-reality-live-assemblyai-v0.1`;
- install `requirements-live.txt`;
- local environment contains `ASSEMBLYAI_API_KEY`;
- for AI33-guidance proof, local environment also exposes the already-owned `AI33_API_KEY`; without it, the browser TTS path is fallback-only and AI33 Guidance Voice remains ACTIVE;
- use a Chromium-family browser with microphone permission enabled;
- headphones are preferred if other audio is playing.

Never put the API key into browser code, DevTools, query strings, or screenshots.

## Start

From the repository root:

```bash
python -m pip install -r requirements-live.txt
python scripts/run_operator_surface.py
```

Open:

`http://127.0.0.1:8765`

Expected terminal truth:

- `truth=SYNTHETIC_FIXTURE_LOCAL_SURFACE`
- `browser_voice=READY`
- `neural_tts=READY_AI33` for the AI33-guidance proof, otherwise `neural_tts=FALLBACK_BROWSER`

If `browser_voice=BLOCKED_NO_API_KEY`, stop. The gate remains ACTIVE.

## Scenario A — initial spoken change

1. Click **Start microphone**.
2. Grant microphone permission.
3. Require UI status `VOICE CONNECTED`.
4. Require ERRATA to greet the operator and explain that nothing changes until explicit Apply.
5. Speak exactly:

   `Route 55 west, skip King Edward and Cumberland until 9:30.`

6. Confirm the transcript appears once under **BUFFERED TRANSCRIPT — NOT YET APPLIED**; formatted updates for one AssemblyAI turn must not duplicate the same utterance.
7. Require the **ERRATA OPERATOR GUIDE** to summarize the interpretation and indicate that nothing has changed yet.
8. Before pressing Apply, verify canonical revision is still 1.
9. Require **Apply spoken turn** to become enabled only after `READY_TO_APPLY` preview.
10. Click **Apply spoken turn**.

Expected:

- AssemblyAI boundary uses `ForceEndpoint`;
- transaction source = `assemblyai_browser_voice_human_boundary`;
- source metadata contains a non-empty AssemblyAI session ID;
- transaction = `APPLIED`;
- revision `1 → 2`;
- King Edward and Cumberland are skipped;
- end time = `09:30:00`.

Failure conditions:

- canonical state changes before the human Apply action;
- no AssemblyAI session ID is captured;
- direct-entry provenance is recorded for a voice transaction;
- rev2 semantics differ from the intended bounded instruction.

## Scenario B — same-identity spoken correction

Speak:

`Wait, keep Cumberland. Make it 10.`

Then click **Apply spoken turn**.

Expected:

- same `change_id`;
- revision `2 → 3`;
- Cumberland restored;
- King Edward remains skipped;
- end time = `10:00:00`;
- current state hash changes exactly once.

## Scenario C — atomic negative path

Reset the demo and reach rev2 again using voice.

Speak:

`Wait, keep Cumberland. Make it.`

Expected **before any mutation call**:

- non-mutating preview status = `NEEDS_CLARIFICATION`;
- raw bounded-core preview outcome = `REVIEW_REQUIRED`;
- guidance explains that the new end time is incomplete and suggests a complete time such as `Make it 10`;
- **Apply spoken turn** remains disabled;
- revision remains 2;
- canonical hash remains unchanged;
- Cumberland remains skipped.

The operator should then restate a complete correction. Any partial KEEP leak or enabled unsafe Apply is a gate failure.

## Scenario D — stale/current commit

After a valid rev3 correction:

1. use **Load prior hash to test refusal**;
2. confirm review;
3. attempt commit.

Expected:

- `STALE_REVIEW`;
- state remains STAGED and unchanged.

Then:

1. restore the current hash;
2. confirm review;
3. commit.

Expected:

- `COMMITTED`;
- authority = `human_web_review`;
- committed hash matches the reviewed current state.

## Scenario E — interactive guidance behavior

During the same session verify:

- when `AI33_API_KEY` is available, **VOICE ENGINE** shows `AI33 PRO · Zach / George V2` (or the configured AI33 voice) and the UI discloses **AI-generated voice**;
- **AI33 VOICE** reflects the server-configured AI33 voice identity;
- request-to-playback latency is measured for greeting and one interpretation response;
- greeting is spoken once when the voice stream connects;
- ERRATA speaks an interpretation summary only after a completed provider turn;
- while guidance audio is playing, no microphone frame is sent to AssemblyAI;
- after playback, a 750 ms echo cooldown occurs before listening resumes;
- guidance playback is not appended to the operator transcript;
- **Repeat guidance** replays the current guidance;
- **Voice guidance off** stops spoken output without disabling visual guidance;
- an AI33 TTS failure falls back to the selected browser voice without granting any mutation authority;
- a connection or preview error produces a visible recovery instruction rather than silent failure.

## Scenario F — evidence export

Click **Export proof receipt**.

The JSON receipt must contain:

- schema `errata-browser-voice-receipt-v0.1`;
- exact local git SHA;
- tracked-worktree-clean flag;
- final canonical state;
- full transaction history;
- at least one voice transaction with:
  - provider = AssemblyAI;
  - transport = streaming_v3;
  - non-empty session ID;
  - human boundary = ForceEndpoint;
- negative-path receipt;
- commit receipt if Scenario D was completed.

The receipt itself contains no API key.

## Promotion rule

Promote:

`Integrated Browser Voice Surface → PROVEN`

only if Scenarios A–F pass in one clean evidence-backed run or in an explicitly reconciled pair of runs bound to the same exact git SHA.

Do not promote:

- `Cloudflare Public Runtime`;
- `Cloudflare State Continuity`;
- `Live Product Integration`;
- `DEMO`;

from this local run alone.

## After promotion

Next workstream:

`Cloudflare Worker runtime + state continuity + secret binding → public deployed browser-voice proof`
