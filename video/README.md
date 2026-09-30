# ERRATA Video Production

This folder separates the hackathon video work into two different products.

## 1. /brag — short explainer

**Target:** 28 seconds.

**Renderer:** HyperFrames.

**Reference grammar:** narrated explainer rather than a conventional ad — typed content, diagrams, evidence surfaces, precise narration, no avatars or stock-footage filler. This matches the useful part of the Scrimba Explain format while keeping ERRATA's own visual language.

Source:
- `video/brag-hyperframes/index.html`

The draft is intentionally independent of the final UI. Selected programmatic panels can later be replaced by real product frames without rebuilding the story.

## 2. Judge film — long controlled demo

**Primary target:** **3:55 / 235 seconds**.

**Internal pacing ceiling:** 4:00.  
**Submission ceiling:** 5:00. The 5-minute allowance is a limit, not a target.

**Master renderer:** Remotion.

**Direction lock:** build the long judge film first with the **current selected V1 direction**. The alternative Opus UI/UX direction is not approved and does not block this film. A second visual-direction cut is optional only if time remains after the V1 master is proven.

**Inputs:**
- real live browser recordings from the exact selected judge-facing runtime;
- HyperFrames deterministic architecture/evidence inserts;
- AI33 Pro → ElevenLabs narration;
- real product audio where interaction matters;
- captions and evidence callouts;
- optional Bandwidth clip only if that gate is separately proven.

Source:
- `video/judge-remotion/`
- `video/judge-hyperframes/`

### Duration budget

| Section | Time |
| --- | ---: |
| Hook + problem | 0:24 |
| Live core: base + bilingual same-identity correction | 1:26 |
| Negative path | 0:35 |
| Hash-bound authority | 0:29 |
| AssemblyAI / architecture | 0:20 |
| GTFS-RT consequence | 0:16 |
| Business value | 0:14 |
| Truth boundary / close | 0:11 |
| **Total** | **3:55** |

The four planned live clips total 137 seconds, so the 235-second master is ~58% live product footage. That is the intended balance: enough context to understand ERRATA, but the majority of the film is the product actually working.

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
live selected ERRATA runtime ────┐
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
1. the selected V1 direction is frozen for capture;
2. browser/runtime regression proof passes on that exact selected build;
3. live recordings are captured;
4. AI33 narration is generated;
5. HyperFrames architecture insert is approved and rendered.

The alternative UI exploration is not a prerequisite for the primary film.

## Capture rule

Every clip presented as live product evidence must be recorded from the exact selected judge-facing runtime after the last behavior-affecting change.

No captured preview or historical run may silently stand in for the selected final build.

## Delivery constraints

Final judge film:
- target 3:55;
- internal ceiling 4:00 unless a specific proven clip requires a deliberate exception;
- hard submission limit under 5:00;
- under 300 MB;
- 1920×1080;
- H.264 MP4;
- captions burned in or clearly readable;
- no unsupported claim.

The /brag teaser is independent of the required judge video and can be exported in 16:9 first, then adapted to 9:16 if needed.

## V1 live master path

The current judge capture UI is frozen on `judge-video-capture-ui-v1` so later UI exploration can continue independently.

Use `video/live-capture-v1/recorder.html` to capture the four real interaction clips, then convert them with:

```powershell
.\video\scripts\convert_live_capture_v1.ps1
```

Then preview the long film with those real clips:

```powershell
cd video\judge-remotion
npm run render:v1-live
```

This cut remains `DRAFT_LIVE_FOOTAGE` until the exact V1 capture runtime passes the final browser proof. Once it passes and the footage is bound to that proven build, V1 becomes the primary judge-film master. A later alternative-UI cut is a secondary option only.
