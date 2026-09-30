# ERRATA — Judge Live Capture v1

## Frozen visual source

- branch: `judge-video-capture-ui-v1`
- presentation commit: `46e1d5de31794af0c29474bd5de7bb51bffa20c7`
- CI-smoke update: `8eef4695c973860e527bf5a6238ec78e02e59d7b`

These recordings are `DRAFT_LIVE_FOOTAGE` until V1 is selected as final UI or replaced by recordings from the final chosen UI.

## Why record V1 now

The long film can be edited, timed, narrated and reviewed now. A later UI only requires replacing the four live files with the same filenames.

## Recorder

Serve this folder locally:

```powershell
cd video\live-capture-v1
python -m http.server 8899
```

Open `http://127.0.0.1:8899/recorder.html`.

The recorder uses browser-native screen/window capture plus microphone audio. No recording is uploaded.

## Capture runtime

Use a deployed preview of `judge-video-capture-ui-v1` so AssemblyAI browser voice and AI33 behave like the judged runtime.

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

Before final judge export: bind runtime to exact git SHA, rerun real browser proof with mic + AssemblyAI, reconcile receipt, and replace V1 clips if another UI is selected.
