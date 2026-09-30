# ERRATA — Slide Presentation Outline v0.1

Seven-slide submission deck.

## 1. Title

**ERRATA**

Speech is a draft. Truth is versioned.

Visual: Live Caption hero screenshot.

## 2. The problem

Transit controllers correct themselves under pressure.

Without a control layer, voice corrections can become separate conflicting instructions.

Key example:

- “Skip King Edward and Cumberland until 9:30.”
- “Wait — keep Cumberland. Make it 10.”

## 3. The core mechanism

ERRATA repairs one operational identity.

- AssemblyAI hears the live turn.
- ERRATA creates a non-mutating draft.
- Human Apply advances the same `change_id`.
- Deterministic reducer creates the next revision.
- Commit requires the current reviewed hash.

## 4. Live Caption UI

Visual language:

- dashed caption = draft / not on air;
- yellow caption = canonical;
- hatched struck caption = dropped / zero effect;
- Timeline view shows one `change_id` and revisions.

## 5. Signature proof

Route 55 scenario:

- rev1 → rev2 base amendment;
- rev2 → rev3 bilingual correction;
- malformed correction refused with hash unchanged;
- stale hash refused;
- current hash committed.

## 6. Downstream consequence

ERRATA is not a chatbot.

- canonical state serializes to GTFS-Realtime;
- independent consumer decodes the candidate;
- validators and evidence are visible in the repo.

## 7. Truth boundary and ask

Proven bounded workflow:

- live browser voice readiness;
- deterministic reducer and evidence;
- public Vercel runtime;
- GTFS-Realtime compatibility.

Not claimed:

- live agency deployment;
- production safety certification;
- external operator adoption.

Close:

> Speech may be fast and fallible. ERRATA keeps one versioned operational truth.