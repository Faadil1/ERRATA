# ERRATA Video Production

This folder separates the hackathon video work into two different products.

## 1. /brag — short explainer

**Target:** 28 seconds.

**Renderer:** HyperFrames.

**Reference grammar:** narrated explainer rather than a conventional ad — typed content, diagrams, evidence surfaces, precise narration, no avatars or stock-footage filler. This matches the useful part of the Scrimba Explain format while keeping ERRATA's own visual language.

Source:
- `video/brag-hyperframes/index.html`

The draft is intentionally independent of the unfinished final UI. After the Opus 5.5 UI pass, selected programmatic panels can be replaced by real final-product frames without rebuilding the story.

## 2. Judge film — long controlled demo

**Target:** 4:40 / 280 seconds.

**Master renderer:** Remotion.

**Inputs:**
- real live browser recordings from the exact final production runtime;
- HyperFrames deterministic architecture/evidence inserts;
- AI33 Pro → ElevenLabs narration;
- real product audio where interaction matters;
- captions and evidence callouts;
- optional Bandwidth clip only if that gate becomes PROVEN.

Source:
- `video/judge-remotion/`
- `video/judge-hyperframes/`

The target is deliberately below the current lablab 5-minute maximum while using substantially more depth than the earlier 90–120 second idea.

## Egaki's role

Egaki remains useful for storyboard exploration, scene ideation and previsualization.

It is **not** the sole judge-film renderer because the final presentation needs:
- live recordings of the working product;
- deterministic overlays and diagrams;
- exact evidence/truth labels;
- controllable captions;
- repeatable final export.

## Rendering stack

```text
live final ERRATA runtime ───────┐
                                │
HyperFrames /brag + inserts ────┼──> Remotion judge master ──> MP4
                                │
AI33 Pro narration ─────────────┤
                                │
captions / evidence / SFX ──────┘
```

## Local workflow in VS Code

### HyperFrames

Requirements:
- Node 22+
- FFmpeg

```powershell
npx hyperframes doctor
cd video\brag-hyperframes
npx hyperframes lint
npx hyperframes check
npx hyperframes preview
```

Do the same from `video\judge-hyperframes` for the architecture insert.

### AI33 narration

From repo root:

```powershell
python video\scripts\generate_ai33_video_narration.py --track brag
```

Or generate all declared tracks:

```powershell
python video\scripts\generate_ai33_video_narration.py
```

### Remotion

```powershell
cd video\judge-remotion
npm install
npm run studio
npm run render:draft
```

Only run `npm run render:final` after:
1. final UI/UX pass;
2. production regression proof;
3. live recordings captured;
4. AI33 narration generated;
5. HyperFrames architecture insert approved and rendered.

## Capture rule

Every clip presented as live product evidence must be recorded from the exact final judge-facing runtime after the last behavior-affecting merge.

No captured preview or historical run may silently stand in for final production.

## Delivery constraints

Final judge film:
- under 5:00;
- under 300 MB;
- 1920×1080;
- H.264 MP4;
- captions burned in or clearly readable;
- no unsupported claim.

The /brag teaser is independent of the required judge video and can be exported in 16:9 first, then adapted to 9:16 if needed.

## V1 live rough cut

The first Opus judge UI is frozen on `judge-video-capture-ui-v1` so additional UI exploration can continue independently.

Use `video/live-capture-v1/recorder.html` to capture the four real interaction clips, then convert them with:

```powershell
.\video\scripts\convert_live_capture_v1.ps1
```

Then preview the long film with those real clips:

```powershell
cd video\judge-remotion
npm run render:v1-live
```

This rough cut is `DRAFT_LIVE_FOOTAGE`. It becomes final evidence only if V1 is selected as the final UI and the exact deployed capture runtime passes the final browser proof.
