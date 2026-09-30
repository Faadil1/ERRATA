# ERRATA Judge Architecture Insert — HyperFrames

A deterministic 24-second architecture insert for the long judge film.

It exists to make the AssemblyAI / human-authority boundary visible without replacing live product footage.

## Preview

```powershell
npx hyperframes lint
npx hyperframes check
npx hyperframes preview
```

## Render after approval

```powershell
npx hyperframes render --quality high --fps 30 --output ../judge-remotion/public/hyperframes/architecture.mp4
```

The Remotion judge master can then composite this rendered insert during the sponsor-depth section.
