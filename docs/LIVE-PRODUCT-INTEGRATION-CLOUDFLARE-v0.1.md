# ERRATA — Live Product Integration / Cloudflare v0.1

**Status:** ACTIVE  
**Priority:** P0 before judge-demo rehearsal  
**Truth boundary:** technical live proofs exist, but the integrated web product is not yet proven or publicly deployed.

## Why this gate exists

ERRATA currently has two previously separate proof surfaces:

1. credentialed AssemblyAI live/controlled Streaming experiments in the terminal;
2. a browser operator review surface that exercises the shared deterministic core through direct text entry.

Those are useful proofs, but **technical proof is not live product integration**.

The product is not judge-ready until the browser itself can capture speech, use AssemblyAI live, preserve the explicit human mutation boundary, drive the same canonical reducer, and run on a public runtime.

## P0 target architecture

### Browser

The browser owns microphone UX only.

Required chain:

`getUserMedia → PCM16 16 kHz AudioWorklet → AssemblyAI Streaming v3 WebSocket → reconciled provider turn → non-mutating ERRATA preview/guidance → explicit human Apply spoken turn → ERRATA mutation API`

Rules:

- provider partial/final turns do not mutate canonical state automatically;
- repeated/formatted provider events for the same `turn_order` are reconciled instead of blindly concatenated;
- completed turns are interpreted first against a disposable copy of canonical state;
- ERRATA may greet, summarize, ask for missing detail, and recommend the next action, but guidance itself has no mutation authority;
- unsafe or incomplete previews keep **Apply spoken turn** disabled;
- browser spoken guidance is explicitly a UI guidance layer and is not represented as AssemblyAI output;
- the operator owns the consequential boundary;
- Apply spoken turn emits `ForceEndpoint`;
- only a finalized buffered transcript may be submitted to the ERRATA mutation endpoint;
- the browser never receives the long-lived AssemblyAI API key.

### AssemblyAI authentication

The application server mints a short-lived streaming token from:

`GET https://streaming.assemblyai.com/v3/token?expires_in_seconds=60`

The browser connects to:

`wss://streaming.assemblyai.com/v3/ws`

using that temporary token.

The permanent API key remains server-side as a secret.

### Shared ERRATA core

Both paths must converge before mutation:

- direct entry → shared parser/resolver/validators/reducer;
- AssemblyAI browser voice → shared parser/resolver/validators/reducer.

There must not be a second business-logic stack for the deployed UI.

The browser voice transaction provenance is:

`assemblyai_browser_voice_human_boundary`

### Cloudflare target

Use **Cloudflare Workers**, not a static-only Pages deployment, because the product needs server-side token minting and stateful API behavior.

Target composition:

- Cloudflare Worker with Static Assets for `web/operator`;
- Python Worker for the existing ERRATA Python core;
- one Durable Object per demo/session for strongly consistent canonical ServiceChange state;
- Worker secrets: `ASSEMBLYAI_API_KEY` and, when neural guidance is enabled, `AI33_API_KEY`; `AI33_BASE_URL` and `AI33_ERRATA_VOICE_ID` are non-secret configuration.
- public API routes:
  - `GET /api/change`
  - `GET /api/evidence`
  - `GET /api/voice-token`
  - `GET /api/voice-capabilities`
  - `POST /api/tts/guidance`
  - `POST /api/preview/voice`
  - `POST /api/amend/direct`
  - `POST /api/amend/voice`
  - `POST /api/commit`
  - `POST /api/reset-demo`.

Do not use ephemeral isolate globals as the source of truth for revision/hash state.

## Current implementation state

Implemented on the feature branch:

- browser voice controls;
- microphone permission request with browser echo cancellation/noise suppression;
- AudioWorklet PCM16 downsampling;
- direct WebSocket connection to AssemblyAI Streaming v3 using a temporary token;
- provider turn reconciliation keyed by AssemblyAI turn identity instead of blind transcript accumulation;
- provider transcript buffering without automatic canonical mutation;
- non-mutating voice preview against a disposable copy of the shared ERRATA core;
- contextual operator guidance: spoken greeting, interpretation summary, missing-detail guidance, next-action guidance, and repeat/mute controls;
- AI33 Pro v3 server-side guidance through `POST /v3/text-to-speech`, using the previously proven `Zach / George V2` voice by default (`elevenlabs_yG30oCchdy9JCUsKqYfV`) when `AI33_API_KEY` is configured;
- visible disclosure that neural guidance is an AI-generated voice;
- browser/Edge natural voice remains an automatic fallback when neural TTS is unavailable;
- strict half-duplex echo guard: outbound microphone frames are suppressed during TTS playback and for a 750 ms cooldown after playback;
- unsafe/incomplete previews keep Apply disabled;
- explicit human `ForceEndpoint` / apply boundary;
- `POST /api/amend/voice`;
- voice transactions routed through the same existing Python parser/resolver/validators/reducer as direct entry;
- distinct voice provenance in the operator transaction history;
- CI unit/smoke coverage for the shared-core voice mutation route.

Not yet proven:

- a credentialed microphone run through this browser surface;
- browser interruption/reconnect behavior;
- browser credential/token failure UX under real conditions;
- credentialed AI33 Pro v3 TTS playback in the real browser surface, including measured request-to-playback latency;
- observed proof that TTS speech plus the 750 ms cooldown is not re-transcribed as operator input;
- Cloudflare Worker port of the shared core;
- Durable Object state continuity;
- public Cloudflare deployment;
- exact deployed-commit/runtime binding;
- public-runtime voice → review → commit end-to-end evidence.

## Gate sequence

### Gate A — Integrated Browser Voice

Promotion to PROVEN requires one credentialed browser run that demonstrates:

1. microphone permission granted;
2. temporary token minted server-side;
3. AssemblyAI Streaming session begins;
4. initial spoken change buffered with no automatic mutation;
5. human Apply spoken turn advances rev1 → rev2;
6. spoken correction advances rev2 → rev3 on the same change ID;
7. malformed/incomplete correction is identified during non-mutating preview, guidance tells the operator what is missing, Apply remains disabled, and revision/hash stay unchanged;
8. at least one safe completed turn is summarized back to the operator before Apply;
9. if neural TTS is configured, guidance is produced by AI33 Pro v3 TTS using the configured ERRATA voice, the UI visibly discloses that the voice is AI-generated, and no AI33 API key reaches the browser;
10. all guidance playback uses half-duplex protection: no microphone frames are sent during speech or the 750 ms cooldown, and guidance is not re-transcribed as operator input;
11. if neural TTS is unavailable, the browser voice fallback remains functional and truthfully labeled;
12. provider/API keys are never exposed in browser source/network responses beyond the AssemblyAI short-lived token;
13. direct-entry path still works through the same core.

### Gate B — Cloudflare Public Runtime

Promotion to PROVEN requires:

1. public Cloudflare Worker URL;
2. deployment bound to exact git SHA;
3. static operator surface served by that Worker;
4. API endpoints served by the Worker;
5. AssemblyAI API key stored only as Cloudflare secret;
6. AI33 API key, if neural guidance is enabled, stored only as Cloudflare secret;
7. `/api/tts/guidance` returns audio only and never secret material;
8. session state survives separate HTTP requests through Durable Object storage;
9. reset creates a deterministic clean session;
10. no secret material appears in client assets/logs.

### Gate C — Live Product Integration

Promotion to PROVEN requires, on the public Cloudflare runtime:

1. voice initial change;
2. same-identity voice correction;
3. REVIEW_REQUIRED negative path with zero state drift;
4. stale reviewed-hash refusal;
5. current-hash human commit;
6. evidence/runtime/commit SHA binding;
7. truth boundary remains visible;
8. browser refresh/re-request does not silently reset canonical state;
9. public STO evidence may be displayed, but no agency-publication claim is made.

## Deployment evidence receipt

When Cloudflare is actually deployed, create:

`evidence/cloudflare-live-product/<date>/deployment.json`

with:

- public URL;
- git SHA;
- Cloudflare deployment/version identifier;
- deployment timestamp;
- browser test timestamp;
- voice session ID;
- change ID;
- rev/hash checkpoints;
- negative-path outcome;
- stale/current commit outcomes;
- secret-leak check;
- screenshots/video references if captured.

## Current gate verdicts

- Integrated Browser Voice Surface → ACTIVE
- AI33 Guidance Voice → ACTIVE
- Echo / Self-Capture Guard → ACTIVE
- Cloudflare Public Runtime → BLOCKED
- Cloudflare State Continuity → BLOCKED
- Live Product Integration → BLOCKED
- DEMO → BLOCKED by Live Product Integration
- External Operator Evidence → BLOCKED independently

The terminal AssemblyAI evidence remains valid bounded technical evidence. It must not be promoted into a claim that the browser product already uses voice end-to-end.
