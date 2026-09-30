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

If `browser_voice=BLOCKED_NO_API_KEY`, stop. The gate remains ACTIVE.

## Scenario A — initial spoken change

1. Click **Start microphone**.
2. Grant microphone permission.
3. Require UI status `VOICE CONNECTED`.
4. Speak exactly:

   `Route 55 west, skip King Edward and Cumberland until 9:30.`

5. Confirm the transcript appears under **BUFFERED TRANSCRIPT — NOT YET APPLIED**.
6. Before pressing Apply, verify canonical revision is still 1.
7. Click **Apply spoken turn**.

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

Click **Apply spoken turn**.

Expected:

- `REVIEW_REQUIRED`;
- unresolved cue contains `END_TIME_AFTER_MAKE_IT`;
- revision remains 2;
- canonical hash remains unchanged;
- Cumberland remains skipped.

Any partial KEEP leak is a gate failure.

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

## Scenario E — evidence export

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

only if Scenarios A–E pass in one clean evidence-backed run or in an explicitly reconciled pair of runs bound to the same exact git SHA.

Do not promote:

- `Cloudflare Public Runtime`;
- `Cloudflare State Continuity`;
- `Live Product Integration`;
- `DEMO`;

from this local run alone.

## After promotion

Next workstream:

`Cloudflare Worker runtime + state continuity + secret binding → public deployed browser-voice proof`
