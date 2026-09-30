# ERRATA /brag — HyperFrames draft

A 28-second judge/social teaser inspired by the **narrated explainer** grammar of Scrimba Explain: typed content, diagrams, evidence surfaces, narration, no stock-footage filler.

The specific Scrimba claim URL supplied by the project owner is not fetchable from automated tooling, so this draft intentionally copies the **format principles**, not any unseen shot-for-shot content.

## Story

1. Problem: a spoken correction should not create a second truth.
2. AssemblyAI live utterance.
3. Preview before mutation.
4. Same change ID, rev1 → rev2.
5. Bilingual self-repair, rev2 → rev3.
6. Ghost speech, zero canonical effect.
7. Stale hash refused / current hash committed.
8. GTFS-RT downstream consequence.
9. Tagline.

## Preview

From this folder:

```powershell
npx hyperframes doctor
npx hyperframes lint
npx hyperframes check
npx hyperframes preview
```

Do **not** render final delivery until the UI/UX pass is approved. HyperFrames' own guidance recommends preview/review before final render.

## Final render after approval

```powershell
npx hyperframes render --quality high --fps 30 --output renders/errata-brag-16x9.mp4
```

## Narration

Generate with the repository's proven AI33 Pro → ElevenLabs route:

```powershell
python ..\scripts\generate_ai33_video_narration.py --track brag
```

The generated MP3 belongs under `audio/`. Add it to the composition only after timing is locked.

## Final UI capture

The final Opus 5.5 UI can replace selected programmatic mock surfaces with real screenshots or 2–4 second live clips. The current draft is deliberately independent of unfinished UI so motion/story work can proceed in parallel.
