# ERRATA — Vercel Public Runtime v0.1

**Status:** IMPLEMENTED / DEPLOYMENT BLOCKED BY CREDENTIAL  
**Primary purpose:** fastest public product runtime for the current bounded browser demo  
**State model:** signed compressed browser-session snapshot  
**Shared business logic:** canonical ERRATA Python core  
**Stronger-state alternative:** Cloudflare Worker + Durable Object

## Decision

Vercel is an acceptable public-runtime path for the bounded hackathon product **if** its state model is represented truthfully.

ERRATA does not assume that a Vercel Python Function keeps process memory across requests or cold starts.

Instead:

```text
browser
  stores signed session token
      ↓
Vercel FastAPI
  verifies HMAC
      ↓
OperatorSurfaceSession.from_snapshot(...)
      ↓
shared parser / resolver / validators / reducer
      ↓
new canonical snapshot
      ↓
HMAC sign + return to browser
```

This gives deterministic continuity for one browser session while preserving one shared product core.

## State truth

### What it provides

- exact revision/hash restoration after stateless function rehydration;
- history and reducer operation restoration;
- commit behavior after restoration;
- tamper detection through HMAC-SHA256;
- browser-refresh / server-cold-start continuity;
- no dependency on ephemeral Python globals for canonical state.

### What it does not provide

- shared multi-operator database semantics;
- server-side authoritative session ownership independent of the browser;
- rollback resistance if a client intentionally replays an older still-valid signed token;
- cross-device shared session state;
- production agency persistence.

Therefore the evidence label is:

`SIGNED_BROWSER_SESSION`

not:

`DURABLE_SHARED_BACKEND`.

## Public API

Implemented in `app.py`:

- `GET /api/health`
- `GET /api/change`
- `GET /api/evidence`
- `GET /api/session-receipt`
- `GET /api/voice-capabilities`
- `GET /api/voice-token`
- `POST /api/preview/voice`
- `POST /api/amend/direct`
- `POST /api/amend/voice`
- `POST /api/commit`
- `POST /api/reset-demo`
- `POST /api/tts/guidance`

Static operator assets are served from `web/operator` through the same FastAPI runtime.

## Secret boundary

### Required for state integrity

`ERRATA_SESSION_HMAC_KEY`

This key is dedicated to session-token integrity. Provider keys are not reused as signing keys.

The automated preview deployment generates an ephemeral signing key per deployment.

### Required for browser STT

`ASSEMBLYAI_API_KEY`

The browser receives only a temporary streaming token.

### Required for natural spoken guidance

`AI33_API_KEY`

The browser receives only generated audio.

No long-lived provider secret or HMAC key is returned to the client.

## Runtime health contract

`GET /api/health` returns only non-secret readiness:

- runtime type;
- exact git SHA;
- deployment URL when available;
- state model;
- session signing readiness;
- AssemblyAI readiness;
- AI33 readiness;
- full-public-voice readiness;
- explicit truth boundary.

A deployment is not promoted merely because `/api/health` is reachable.

## Deployment automation

`.github/workflows/deploy-vercel.yml`:

1. checks for `VERCEL_TOKEN`;
2. creates/links project `errata` in scope `faadil1s-projects`;
3. generates an ephemeral `ERRATA_SESSION_HMAC_KEY`;
4. forwards provider keys only if corresponding GitHub secrets exist;
5. deploys the exact git SHA;
6. calls `/api/health`;
7. asserts runtime git SHA matches `GITHUB_SHA`;
8. writes and uploads a deployment receipt.

### Current observed preflight

Run `36695606628`:

- `VERCEL_TOKEN`: missing;
- `ASSEMBLYAI_API_KEY`: missing in GitHub Actions secrets;
- `AI33_API_KEY`: missing in GitHub Actions secrets;
- verdict: `BLOCKED_MISSING_VERCEL_TOKEN`;
- artifact: `11087222278`;
- digest: `sha256:aee74d48a6911aa096d6fcf364966ca1fa549f883204f56e4090c5a1a3f61e74`.

No public URL was created.

## Promotion gates

### Vercel Signed Session Continuity → PROVEN

Requires:

- signed snapshot roundtrip preserves exact revision/hash;
- tampered token rejected;
- canonical rev3 token remains safely below practical request-header limit;
- commit can occur after restore.

CI covers these requirements.

### Vercel Public Runtime → PROVEN

Requires:

- public Vercel URL;
- `/api/health` binds exact deployment to git SHA;
- signed-session state survives a browser refresh/new function invocation;
- static surface and APIs load from the public URL;
- no secret appears in browser source/responses;
- deployment receipt preserved.

### Public Voice Runtime → PROVEN

Requires, on the deployed URL:

- AssemblyAI temp token minted server-side;
- real browser microphone connects;
- base change rev1→2;
- malformed correction preview refuses atomically with zero state drift;
- valid correction rev2→3;
- stale reviewed hash refused;
- current reviewed hash committed;
- AI33 guidance plays or truthfully falls back;
- voice reply does not self-transcribe;
- exported receipt contains client preview/latency evidence and runtime SHA.

### Live Product Integration → PROVEN

Requires the public voice proof above plus post-build reconciliation.

## Why Cloudflare remains registered

Cloudflare Durable Objects provide a stronger server-owned shared-state model. That path remains registered and BLOCKED rather than deleted.

Vercel is currently favored for speed-to-public-runtime; Cloudflare remains the upgrade path if shared state, rollback resistance, or multi-operator semantics become material to the judged product.

## Truth boundary

Do not describe the Vercel signed-session architecture as:

- a production state store;
- multi-user durable persistence;
- agency-integrated storage;
- rollback-resistant server authority.

It is a bounded, integrity-protected public demo state model that preserves the deterministic ERRATA core across serverless rehydration.
