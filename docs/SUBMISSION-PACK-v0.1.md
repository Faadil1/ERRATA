# ERRATA — Submission Pack v0.1

Use this file to copy/paste into the hackathon submission form.

## Basic information

### Project title

ERRATA

### Short description

Voice control for transit operations that turns live speech into non-mutating drafts, then lets a human apply and commit one versioned service change instead of creating conflicting operational truth.

### Long description

Transit controllers correct themselves while already handling radio, maps, incidents and service pressure. In many voice workflows, each correction can become another independent instruction. That is dangerous in operational settings: “skip King Edward and Cumberland until 9:30” followed by “wait — keep Cumberland, make it 10” should repair the same service change, not create a second alert.

ERRATA is a voice control layer for transit operations. AssemblyAI Universal-3.5 Pro Realtime transcribes the live microphone stream and supports the English/French correction flow. ERRATA converts what was heard into a non-mutating draft. Canonical state does not move until the operator explicitly applies the draft. The deterministic core then advances the same `change_id` from revision to revision, validates the change, regenerates the downstream GTFS-Realtime candidate, and requires a current hash before final commit.

The judge-facing Live Caption interface makes the truth boundary visible: dashed captions are drafts, solid yellow captions are canonical, and rejected or incomplete attempts become dropped frames with zero canonical effect and unchanged hash. The demo proves the core loop with Route 55: base amendment, bilingual correction, malformed correction refusal, stale-hash refusal, current-hash commit, and independently decoded GTFS-Realtime output.

ERRATA does not claim live STO publication, production agency deployment or production safety certification. It demonstrates a bounded, reproducible voice-to-operations workflow where speech is fast and fallible, but operational truth remains deliberate, deterministic and versioned.

## Technology tags

AssemblyAI, Universal-3.5 Pro Realtime, realtime speech-to-text, voice agents, FastAPI, Vercel, Python, JavaScript, GTFS-Realtime, protobuf, transit operations, deterministic state machines, human-in-the-loop, signed browser session, Bandwidth, AI33 / ElevenLabs guidance.

## Category tags

Voice agents, operations, transportation, public transit, realtime AI, developer tools, safety-critical workflow, human-in-the-loop automation, data integrity, civic infrastructure.

## Cover image

Recommended repository image:

`docs/ui/01-on-air-first-viewport.png`

Submission copy:

> Live Caption operator view: speech is a draft, truth is versioned.

## Video presentation

Primary video target: **3:55**.

Use the long controlled judge film structure:

1. problem and user context;
2. live voice base amendment;
3. same-identity bilingual correction;
4. incomplete correction with zero canonical effect;
5. stale review refused and current hash committed;
6. decoded GTFS-Realtime consequence;
7. truth boundary close.

See: `docs/VIDEO-PRESENTATION-SCRIPT-v0.1.md`.

## Slide presentation

Use the 7-slide structure in:

`docs/SLIDE-PRESENTATION-OUTLINE-v0.1.md`

## App hosting and repository

### Public GitHub repository

https://github.com/Faadil1/ERRATA

### Demo application platform

Vercel

### Application URL

https://errata-beige.vercel.app

### Current production proof supplied by local deployment

- Production alias: `https://errata-beige.vercel.app`
- Production deployment URL: `https://errata-grk6xzdxl-faadil1s-projects.vercel.app`
- Verified runtime SHA: `5bc291c4efa7bfde4124988e7752f8f5beadccc8`
- `session_signing_ready=True`
- `assemblyai_ready=True`
- `ai33_ready=True`
- `bandwidth_phone_transport_configured=True`
- `full_public_voice_ready=True`

Note: the submission-facing README cleanup commits are documentation-only changes made after that production deployment. Redeploy the latest branch head before final submission if exact repository-head/runtime binding is required.

## Team

Team size allowed by the platform: 1–6 people.

Current submission can be entered as a solo/team project depending on final participant list.