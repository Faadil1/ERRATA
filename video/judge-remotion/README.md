# ERRATA Judge Film — Remotion master

## Duration lock

**Primary target: 3:55 (235 seconds)** at 30 fps.

The internal pacing ceiling is **4:00**. The submission allowance remains a hard ceiling, not a creative target.

Why 3:55:
- four planned live evidence clips = 137 seconds;
- 137 / 235 ≈ 58% live product footage;
- enough room remains for problem framing, architecture, consequence, business value and the truth boundary;
- 65 seconds of headroom remain below a 5-minute submission maximum.

The duration constant lives in `src/JudgeFilm.tsx` as `JUDGE_FILM_SECONDS` and `Root.tsx` consumes that same constant so the composition duration cannot silently drift from the authored timeline.

## Direction priority

The primary long film uses the **current selected V1 judge direction first**.

The alternative Opus UI/UX direction is exploratory and unapproved. It is not a prerequisite for capture, narration, editing or finalization of the V1 judge film. If time remains after the V1 master is proven, a second cut may reuse the same narrative and evidence structure with the alternative UI.

## Production stack

- **Live video recordings:** selected V1 ERRATA runtime, recorded after exact-build browser proof.
- **HyperFrames:** deterministic motion inserts (architecture, revision identity, evidence transitions).
- **Remotion:** final edit/master timeline, compositing, captions, live footage, audio, export.
- **AI33 Pro → ElevenLabs:** narration tracks generated locally from `video/narration.json`.
- **Egaki:** storyboard/previsualization only; never the sole evidence layer.

## Timeline

| Section | Start | Duration |
| --- | ---: | ---: |
| Hook | 0:00 | 0:10 |
| Problem | 0:10 | 0:14 |
| Live core | 0:24 | 1:26 |
| Negative path | 1:50 | 0:35 |
| Authority | 2:25 | 0:29 |
| AssemblyAI / architecture | 2:54 | 0:20 |
| Downstream consequence | 3:14 | 0:16 |
| Business value | 3:30 | 0:14 |
| Truth boundary | 3:44 | 0:11 |
| **End** | **3:55** | |

## Why a hybrid film

The judge must see the product actually work. Programmatic video gives us typography, diagrams, controlled pacing and evidence callouts; it must never replace the live proof.

Final film target:
- ~55–65% live product footage;
- ~15–20% architecture/evidence inserts and transitions;
- ~15–20% problem/business/truth framing;
- AI33 narration bridges sections without talking over critical live interactions.

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

Place selected-build clips under `public/live/`:

- `01-base-voice.mp4`
- `02-correction-en-fr.mp4`
- `03-negative-ghost.mp4`
- `04-stale-current-commit.mp4`

Record these only after the selected V1 capture build passes the browser/runtime proof required for final evidence.

## Final render

Once assets and narration exist:

```powershell
npm run render:final
```

Final QA:
- target duration = 3:55;
- internal pacing ceiling = 4:00;
- hard submission limit < 5:00;
- file size < 300 MB;
- no unsupported claim;
- all live footage from the exact selected proven build;
- captions readable at 1080p;
- final 11 seconds contain the truth boundary / close, not roadmap filler.
