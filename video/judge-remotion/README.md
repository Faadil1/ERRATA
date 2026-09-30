# ERRATA Judge Film — Remotion master

## Duration

**4:40 (280 seconds)** at 30 fps.

This is intentionally longer than the earlier 90–120 second concept. Lablab's current submission guidance permits a video presentation **up to 5 minutes** and under 300 MB, so 4:40 uses the available judging window while preserving ~20 seconds of safety.

## Production stack

- **Live video recordings:** final public ERRATA runtime, recorded after the Opus 5.5 UI/UX pass and regression proof.
- **HyperFrames:** deterministic motion inserts (architecture, revision identity, evidence transitions).
- **Remotion:** final edit/master timeline, compositing, captions, live footage, audio, export.
- **AI33 Pro → ElevenLabs:** narration tracks generated locally from `video/narration.json`.
- **Egaki:** storyboard/previsualization only; never the sole evidence layer.

## Why a hybrid film

The judge must see the product actually work. Programmatic video gives us typography, diagrams, controlled pacing and evidence callouts; it must never replace the live proof.

Final film target:
- ~55–65% live product footage;
- ~20–25% HyperFrames explanatory inserts / transitions;
- ~10–15% business/truth framing;
- AI33 narration bridges the sections without talking over critical live interactions.

## Install

From `video/judge-remotion`:

```powershell
npm install
npm run studio
```

Draft mode renders without live assets or narration:

```powershell
npm run render:draft
```

## Generate AI33 narration

From the repository root:

```powershell
python video\scripts\generate_ai33_video_narration.py --track judge_intro --track judge_bridge --track judge_negative --track judge_authority --track judge_architecture --track judge_consequence --track judge_business --track judge_close
```

No API secret is printed.

## Live recording slots

Place final clips under `public/live/`:

- `01-base-voice.mp4`
- `02-correction-en-fr.mp4`
- `03-negative-ghost.mp4`
- `04-stale-current-commit.mp4`

Record these only **after** the Opus 5.5 UI pass is merged and the affected browser gates are rerun.

## Final render

Once assets and narration exist:

```powershell
npm run render:final
```

Final QA:
- duration < 5:00;
- file size < 300 MB;
- no unsupported claim;
- all live footage from the exact final production build;
- captions readable at 1080p;
- final 20 seconds contain the truth boundary and CTA, not roadmap filler.
