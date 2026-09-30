# ERRATA — Video Presentation Script v0.1

Target duration: **3:55**. Internal ceiling: **4:00**.

Use the production candidate UI unless the final browser proof forces a fallback.

## 0:00–0:24 — Hook / problem

Narration:

> Transit controllers correct themselves while handling radio, maps, incidents and service pressure. In normal voice automation, every utterance can become another instruction. ERRATA is built around a stricter rule: one operational change, one identity, and every correction repairs that same truth.

Visuals:

- On Air view first viewport.
- Highlight “Speech is a draft. Truth is versioned.”
- Show dashed draft vs solid canonical caption semantics.

## 0:24–1:50 — Live core: base amendment and correction

Action 1:

```text
Route 55 west, skip King Edward and Cumberland until 9:30.
```

Show:

- AssemblyAI live transcript;
- non-mutating draft;
- Apply button near caption;
- rev1 → rev2.

Action 2:

```text
Wait — garde Cumberland. Make it 10.
```

Show:

- candidate rev3 while canonical remains rev2;
- same `change_id`;
- Apply;
- Cumberland restored;
- King Edward still skipped;
- end time 10:00.

Narration:

> AssemblyAI owns live speech understanding. ERRATA deliberately keeps mutation authority outside the probabilistic layer. Speech first becomes a preview. Only explicit human Apply can advance canonical state.

## 1:50–2:25 — Negative path

Action:

```text
Wait, keep Cumberland. Make it.
```

Show:

- NEEDS_CLARIFICATION;
- Apply disabled;
- dropped frame / ghost speech;
- zero canonical effect;
- hash unchanged.

Narration:

> The same rule holds when speech is incomplete. ERRATA can display what it heard without letting that draft leak into operational state. The revision and canonical hash stay unchanged.

## 2:25–2:54 — Authority

Show:

- stale reviewed hash;
- REFUSED / STALE_REVIEW;
- current reviewed hash;
- COMMITTED.

Narration:

> Review authority is version-bound too. A stale reviewed hash is refused. Only the current reviewed state can commit.

## 2:54–3:14 — AssemblyAI / architecture

Show:

- architecture overlay or Timeline / Ledger view;
- microphone → AssemblyAI → draft → Apply → reducer → GTFS-RT.

Narration:

> The live path uses AssemblyAI Universal-3.5 Pro Realtime with English and French correction behavior, transit keyterms and contextual updates. ERRATA then passes the interpreted operation through deterministic validation, reduction, evidence generation and a hash-bound commit boundary.

## 3:14–3:30 — Downstream consequence

Show:

- Feed view;
- decoded GTFS-Realtime candidate;
- public-network / external acceptance evidence.

Narration:

> The result is not just a chat response. ERRATA serializes a GTFS-Realtime candidate, then an independent wire consumer decodes those protobuf bytes so the downstream consequence is visible and testable.

## 3:30–3:44 — Business value

Narration:

> The user is a transit controller who needs hands-free speed without giving probabilistic speech direct authority over service truth. ERRATA is a control layer for high-consequence voice operations, not a passenger chatbot.

Visuals:

- On Air or Timeline view with one `change_id`.
- Quick text overlay: “fast speech / deliberate truth / current hash”.

## 3:44–3:55 — Close / truth boundary

Narration:

> The browser path is the proven primary demo. Phone transport is shown only when separately proven. Speech is fast and fallible. ERRATA keeps one operational truth.

Visuals:

- production URL;
- repository URL;
- truth boundary: bounded demo, no live agency deployment claim.

## Required captures

1. `01-base-voice.mp4`
2. `02-correction-en-fr.mp4`
3. `03-negative-ghost.mp4`
4. `04-stale-current-commit.mp4`

Capture from the exact production candidate runtime used for final proof.

## Final QA

- under 4:00 preferred;
- under 5:00 hard limit;
- no unsupported production/agency claim;
- no provider secrets in video;
- captions/readable text visible at 1080p;
- final runtime URL and repo visible near the end.