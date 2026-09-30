# ERRATA — Claude Opus 5.5 UI/UX Final Pass Brief v0.1

## Purpose

This branch exists only for the final judge-facing UI/UX pass. It must make ERRATA understandable, memorable, and visually distinctive without changing canonical behavior.

## Non-negotiable product truth

ERRATA is a voice control layer for transit operations.

Core invariant:

> When a controller corrects themselves, ERRATA repairs the same versioned service change instead of creating a second conflicting truth.

Do not redesign ERRATA into:
- a passenger trip planner;
- a generic chatbot;
- a developer debugging assistant;
- a confidence-score recommender;
- an agency-live integration that does not exist.

## Files allowed to change

Primary:
- `web/operator/index.html`
- `web/operator/app.css`
- `web/operator/app.js` only for presentation/state rendering, never canonical semantics

Optional:
- static assets used by the operator surface
- judge-facing docs/screenshots

Do not modify:
- parser/reducer/validators;
- session signing;
- FastAPI routes;
- AssemblyAI authority boundaries;
- GTFS-RT serialization semantics;
- evidence labels;
- commit/refusal behavior.

Any UI change that requires behavior changes must stop and be reviewed separately.

## Judge objective

A judge should understand in the first 5 seconds:
1. who uses ERRATA;
2. what goes wrong without it;
3. what ERRATA uniquely does;
4. that voice input cannot directly mutate operational truth.

## Visual hierarchy

The first viewport should prioritize:
1. one-line product promise;
2. live voice state;
3. same `change_id` revision story;
4. current canonical change;
5. non-mutating preview / ghost speech;
6. downstream GTFS-RT consequence.

Internal governance terminology belongs below the fold.

## Signature visual sequence

The UI must make this sequence obvious without explanation:

```text
rev1
  ↓ voice amendment
rev2
  ↓ spoken correction
rev3
same change_id throughout
```

Then visibly show:

```text
incomplete correction
→ GHOST SPEECH
→ 0 canonical effect
→ hash unchanged
```

And:

```text
stale reviewed hash
→ REFUSED

current reviewed hash
→ COMMITTED
```

## Design direction

Avoid:
- generic dark-blue AI dashboard;
- neon gradients as decoration;
- excessive glassmorphism;
- dense card grids;
- fake terminal aesthetic;
- decorative AI particles;
- visual noise that hides evidence.

Prefer:
- domain-native operational control-room language;
- high-information editorial hierarchy;
- strong typography;
- clearly differentiated canonical vs preview vs stale states;
- memorable revision/evidence visualization;
- restrained motion tied to state changes;
- responsive desktop/mobile behavior;
- reduced-motion support.

## Required UI states

Design and verify:
- no microphone permission;
- disconnected;
- listening;
- partial transcript;
- READY_TO_APPLY;
- NEEDS_CLARIFICATION;
- GHOST / superseded speech;
- rev1 / rev2 / rev3;
- stale commit refusal;
- successful current-hash commit;
- downstream GTFS-RT decoded view;
- provider unavailable;
- narrow/mobile viewport;
- reduced motion.

## Motion

Use motion only when it communicates:
- transcript arriving;
- preview becoming canonical;
- revision transition;
- stale artifact invalidation;
- ghost speech disappearing from authority;
- downstream artifact refresh.

No animation should imply a mutation before Apply.

## Accessibility

- keyboard reachable controls;
- visible focus;
- high contrast;
- aria-live for voice/status events;
- no color-only meaning;
- reduced-motion behavior;
- readable at common laptop widths.

## Definition of Done

The UI/UX pass is not complete until:
- first-5-second comprehension is human-tested;
- no canonical behavior changed;
- browser proof still passes;
- exact judge scenario remains reproducible;
- responsive smoke test passes;
- reduced-motion smoke test passes;
- screenshots/video frames are clean enough for submission.
