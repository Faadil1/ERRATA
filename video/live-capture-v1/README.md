# ERRATA — Judge Live Capture v1

## Primary visual source

The long judge film is captured **first from the pre-Opus baseline**:

- branch: `bandwidth-phone-transport-v0.1`
- baseline head at duration lock: `7d7561efd16c18a27e7d83fdf3514e37a757d37e`

Do **not** use `judge-video-capture-ui-v1` as the visual-source label for the primary cut. That branch has advanced to the unapproved Opus UI head `8eef4695c973860e527bf5a6238ec78e02e59d7b`.

The Opus preview is technically deployable and healthy, but it is an alternative visual direction only. It does not replace the baseline film unless explicitly approved later.

These recordings remain `DRAFT_LIVE_FOOTAGE` until the exact baseline SHA used for capture passes the browser proof and the exported evidence is reconciled.

## Why record the baseline now

The long film can be edited, timed, narrated and reviewed now without waiting for a new UI decision. A later approved UI requires replacing only the four live files with the same filenames; the 3:55 master timeline, narration structure and evidence story remain reusable.

## Recorder

Serve this folder locally:

```powershell
cd video\live-capture-v1
python -m http.server 8899
```

Open `http://127.0.0.1:8899/recorder.html`.

The recorder uses browser-native screen/window capture plus microphone audio. No recording is uploaded.

## Capture runtime

Deploy the exact pre-Opus baseline SHA chosen for capture from `bandwidth-phone-transport-v0.1`.

Before recording: reset to rev1; verify deployed SHA; maximize a 1920×1080 browser window; browser zoom 100%; close notifications; confirm mic permission.

## Shot 01 — Base voice amendment

Target: 35–45 s. Start at canonical rev1.

Speak exactly:

```text
Route 55 west, skip King Edward and Cumberland until 9:30.
```

Show live AssemblyAI capture → final transcript → non-mutating preview → explicit Apply → rev1→rev2 → same change_id → GTFS-RT consequence.

## Shot 02 — EN/FR same-identity correction

Target: 35–45 s. Start at rev2.

Speak exactly:

```text
Wait — garde Cumberland. Make it 10.
```

Show candidate rev3 while canonical stays rev2 → Apply → rev3 → Cumberland restored → King Edward still skipped → 10:00.

## Shot 03 — Negative / ghost speech

Target: 25–35 s. Start at rev3.

Speak exactly:

```text
Wait, keep Cumberland. Make it.
```

Show NEEDS_CLARIFICATION → Apply disabled → ghost speech → `0 canonical effect · hash unchanged` → rev3 unchanged.

## Shot 04 — Stale refusal → current commit

Target: 25–35 s. Show stale reviewed hash → REFUSED/STALE_REVIEW → rev3 unchanged → current reviewed hash → confirmation → COMMITTED → decoded GTFS-RT / receipt.

## Raw files

Recorder filenames:

```text
01-base-voice.webm
02-correction-en-fr.webm
03-negative-ghost.webm
04-stale-current-commit.webm
```

Move them into `video/live-capture-v1/raw/`, then run:

```powershell
.\video\scripts\convert_live_capture_v1.ps1
```

The converted MP4s land in `video/judge-remotion/public/live/`.

## Truth boundary

Before final judge export: bind runtime to the exact baseline git SHA, rerun real browser proof with mic + AssemblyAI, reconcile the receipt, and replace these clips only if a different UI is explicitly approved.
