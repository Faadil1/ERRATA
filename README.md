# ERRATA

**Voice control for transit operations. When a controller corrects themselves, ERRATA repairs the same versioned service change instead of creating a second conflicting truth.**

> **Speech is fast and fallible. Operational truth must be deliberate and deterministic.**

## See it in 30 seconds

**Operator / user:** a transit service controller handling an active disruption while already working across radio, maps, and incident tools.

**Say:**

```text
Route 55 west, skip King Edward and Cumberland until 9:30.
```

ERRATA uses **AssemblyAI Universal-3.5 Pro Realtime** to transcribe the live microphone stream, previews the interpretation without changing canonical state, and waits for explicit human **Apply**.

Then correct yourself:

```text
Wait — garde Cumberland. Make it 10.
```

The result is not a second instruction:

```text
same change_id
rev1 → rev2 → rev3
King Edward = skipped
Cumberland = restored
end time = 10:00
GTFS-RT candidate regenerated from the current canonical hash
```

Try an incomplete correction:

```text
Wait, keep Cumberland. Make it.
```

ERRATA asks for the missing time and keeps the revision/hash unchanged. A stale reviewed hash is also refused before commit.

## Why this is a voice agent

AssemblyAI is load-bearing in the live product path:

```text
microphone
  → AssemblyAI Universal-3.5 Pro Realtime
  → provider turns + EN/FR code-switch bias + transit keyterms
  → non-mutating ERRATA interpretation
  → human Apply boundary
  → deterministic resolver / validators / reducer
  → one versioned ServiceChange
  → GTFS-RT candidate + evidence
  → hash-bound human commit
```

ERRATA deliberately does **not** let probabilistic conversational turn ownership become mutation authority. The voice layer proposes what was heard; deterministic code and the operator decide what becomes operational truth.

## What makes it different

Most voice workflows treat a correction as another message. ERRATA treats it as a **minimal repair to the same operational identity**. Rejected or superseded speech becomes visible as **ghost speech — 0 canonical effect, hash unchanged**. The UI also shows the downstream GTFS-RT consequence so the judge can see what another transit consumer would receive from the same canonical state.

The bounded demo uses synthetic/static transit fixtures plus public-network acceptance evidence. It is **not** a claim of live STO publication or production agency deployment.

## Product state

- Lifecycle: **DELIVER**
- Working name: **ERRATA** — Naming / Collision Gate remains ACTIVE
- Bounded Technical Reality / Prototype Killer: **PROVEN**
- Shared deterministic core: **PROVEN**
- Local browser operator surface: **PROVEN**
- Integrated browser voice: **ACTIVE** pending final negative/commit/receipt reconciliation on one exact head
- AI33 guidance voice: **PROVEN** for bounded local functional playback; conversational latency remains ACTIVE
- Public runtime: **implementation in progress**
- Agency live integration: **BLOCKED / not claimed**
- External operator evidence: **BLOCKED / not yet collected**

Canonical governance:

- [Living PRD v0.1](docs/PRD-v0.1.md)
- [Conditional Gateway Registry v0.2](docs/CONDITIONAL-GATEWAY-REGISTRY-v0.2.md)
- [Browser Voice Proof Protocol v0.1](docs/BROWSER-VOICE-PROOF-PROTOCOL-v0.1.md)
- [Vercel Public Runtime v0.1](docs/VERCEL-PUBLIC-RUNTIME-v0.1.md)
- [Cloudflare / Durable Object Runtime Spec v0.1](docs/LIVE-PRODUCT-INTEGRATION-CLOUDFLARE-v0.1.md)
- [Post-Vertical-Slice Depth Gap Review](docs/POST-VERTICAL-SLICE-DEPTH-GAP-REVIEW-v0.1.md)

## Core interaction

```text
microphone
  ↓
AssemblyAI Universal-3.5 Pro Realtime
  ↓
provider turn reconciliation + domain keyterms
  ↓
non-mutating ERRATA preview
  ↓
operator guidance
  ├─ visual guidance immediately
  └─ AI33 Pro voice guidance
       ├─ concise speech copy
       ├─ persistent cache
       └─ mic remains live while audio is being generated
  ↓
explicit human Apply spoken turn
  ↓
ForceEndpoint boundary
  ↓
shared bounded parser / resolver / validators / reducer
  ↓
ServiceChange(change_id, revision, state_hash)
  ↓
consequence + GTFS-RT artifact
  ↓
hash-bound human review / commit
```

AI33 playback uses a half-duplex safety boundary **only while audio is actually playing**, followed by a short echo cooldown. A slow AI33 generation no longer blocks operator speech; new operator speech invalidates a stale pending reply.

## What the browser path has demonstrated

Bounded local browser runs have observed:

- real microphone capture through AssemblyAI Streaming v3;
- one AssemblyAI session across the base amendment and same-identity correction;
- `ForceEndpoint` as the explicit human mutation boundary;
- rev1 → rev2 for:
  - Route 55 west;
  - skip King Edward + Cumberland;
  - end 09:30;
- rev2 → rev3 for:
  - restore Cumberland;
  - keep King Edward skipped;
  - end 10:00;
- clock-time normalization for realtime STT variants such as `9: 30` without degrading to 09:00;
- clarification with zero mutation when a correction is incomplete or misheard;
- clean retry isolation instead of accumulating rejected transcript attempts;
- AI33 Pro / ElevenLabs guidance playback;
- no observed self-transcription of ERRATA speech in the bounded echo-guard runs.

These are **bounded prototype claims**, not production or agency-integration claims.

## Voice latency hardening

The first AI33 integration exposed multi-second uncached generation latency. The current branch reduces latency and interruption cost through:

- short spoken copy separate from richer visual guidance;
- persistent AI33 audio cache outside the git worktree;
- client-side prefetch/reuse of generated audio;
- microphone + AssemblyAI token initialization in parallel;
- listening remains active while AI33 is generating;
- stale generated replies are cancelled when the operator starts a new turn;
- **Skip voice reply** keeps the session alive without disconnecting the microphone;
- visible telemetry for:
  - voice connection time;
  - deterministic interpretation time;
  - TTS generation time;
  - AI33 incremental credit cost;
  - cache hit/miss.

Uncached AI33 latency is still an explicit **Operational Economics / Conversational Latency** gate and must be remeasured after these changes.

## Local run

### Install

```powershell
python -m pip install -r requirements-live.txt
```

### Secrets

Required for live browser STT:

```text
ASSEMBLYAI_API_KEY=...
```

Optional but recommended for natural ERRATA speech:

```text
AI33_API_KEY=...
```

On Windows, the local runner can reuse persistent User/Machine environment variables for these server-side keys. Do not put API keys in browser code, URLs, screenshots, or proof receipts.

Optional AI33 configuration:

```text
AI33_BASE_URL=https://api.ai33.pro
AI33_ERRATA_VOICE_ID=elevenlabs_yG30oCchdy9JCUsKqYfV
AI33_ERRATA_VOICE_LABEL=Zach / George V2
AI33_ERRATA_SPEED=0.98
```

### Start

```powershell
python scripts/run_operator_surface.py
```

Open:

```text
http://127.0.0.1:8765
```

Expected terminal truth when both providers are configured:

```text
browser_voice=READY
neural_tts=READY_AI33
```

## Canonical browser scenario

1. Speak: **Route 55 west, skip King Edward and Cumberland until 9:30.**
2. Confirm the preview is correct and canonical revision is still 1.
3. Apply the spoken turn → revision 2.
4. Speak: **Wait, keep Cumberland. Make it 10.**
5. Confirm the preview is correct and revision is still 2.
6. Apply → revision 3.
7. Negative path: **Wait, keep Cumberland. Make it.**
   - Apply must remain disabled;
   - revision/hash must not move.
8. Test stale reviewed hash refusal.
9. Commit only the current reviewed hash.
10. Export the proof receipt.

## Evidence model

The browser receipt includes:

- exact runtime / git binding when available;
- canonical state and validation;
- full mutation/commit history;
- AssemblyAI session ID and human boundary metadata;
- client voice telemetry;
- external-acceptance reference evidence.

The receipt must never contain provider API keys.

## Vercel runtime

The repository now includes a FastAPI Vercel entrypoint in [`app.py`](app.py).

Because Vercel Functions are not a shared in-memory database, ERRATA does **not** rely on process globals for canonical continuity. The public runtime uses an integrity-protected, compressed browser session snapshot:

```text
browser snapshot
  ↓
HMAC verification on Vercel
  ↓
restore shared Python core
  ↓
apply / preview / commit
  ↓
new signed snapshot
```

This gives cold-start continuity for a single browser session without creating a second business-logic implementation.

Truth boundary:

- state model: **SIGNED_BROWSER_SESSION**;
- cold-start continuity: yes;
- shared multi-operator durable database: **no**;
- rollback resistance against replaying an older valid signed snapshot: **no**;
- production/agency state store: **no**.

For a stronger shared-state runtime, the Cloudflare Durable Object design remains available as a later promotion path.

### Vercel server secrets

The public runtime requires a **dedicated** server-side session signing secret:

```text
ERRATA_SESSION_HMAC_KEY
```

The automated Vercel preview workflow generates an ephemeral signing key for each deployment, so this value does not need to be committed or exposed. A manually managed production deployment should use its own strong dedicated secret.

For the full public voice loop, configure both provider secrets:

```text
ASSEMBLYAI_API_KEY
AI33_API_KEY
```

No secret is returned to the browser.

### Deployment automation status

`.github/workflows/deploy-vercel.yml` can create/link the `errata` project inside the `faadil1s-projects` Vercel workspace, deploy the exact Git SHA, verify `/api/health`, and emit a deployment receipt.

The first automated deployment preflight was intentionally blocked because the ERRATA GitHub repository currently has no `VERCEL_TOKEN` secret. That run produced:

- workflow run: `36695606628`;
- status: `BLOCKED_MISSING_VERCEL_TOKEN`;
- artifact: `11087222278`;
- artifact digest: `sha256:aee74d48a6911aa096d6fcf364966ca1fa549f883204f56e4090c5a1a3f61e74`.

This is a credential boundary, not a runtime failure. The deployment workflow now fails visibly while blocked so a green deployment check cannot be mistaken for an actual deployment.

For a full public voice deployment, GitHub Actions must be able to supply:

```text
VERCEL_TOKEN
ASSEMBLYAI_API_KEY
AI33_API_KEY
```

Do not paste these values into issues, commits, URLs, screenshots, or chat.

### Secure local Vercel deployment fallback

If GitHub does not have a `VERCEL_TOKEN`, the repository also includes:

```powershell
.\scripts\deploy_vercel_local.ps1
```

This path:

- uses the Vercel CLI authentication on the local machine;
- reuses the existing Windows process values for `ASSEMBLYAI_API_KEY` and `AI33_API_KEY`;
- generates a dedicated random `ERRATA_SESSION_HMAC_KEY`;
- writes provider/session values to Vercel as sensitive environment variables through stdin;
- deploys a preview by default;
- verifies `/api/health` and exact git SHA;
- never prints secret values.

After a preview is fully proven, production can be requested explicitly:

```powershell
.\scripts\deploy_vercel_local.ps1 -Production
```


## Deterministic tests

```powershell
python -m pip install -r requirements.txt
python -m pytest
```

CI additionally exercises:

- shared core semantics;
- live adapter contract;
- browser JavaScript syntax;
- operator HTTP surface;
- signed-session roundtrip/tamper rejection;
- public-network STO scenario;
- canonical MobilityData external acceptance.

## Current truth boundary

Do **not** claim:

- production voice reliability;
- live STO/agency publication;
- external operator adoption;
- production safety;
- shared multi-user durable state on the Vercel signed-session runtime;
- universal voice speed superiority;
- final judge/demo readiness until the remaining proof gates are reconciled.

The repository and [Conditional Gateway Registry](docs/CONDITIONAL-GATEWAY-REGISTRY-v0.2.md) are the source of truth.

### Current verified Vercel preview

The current proven preview runtime is:

- deployment: `dpl_3ntykUre5uPvrKWfacuPg21ftmUa`;
- URL: `https://errata-5hg3gfy46-faadil1s-projects.vercel.app`;
- exact git SHA: `36ccd03ab2b246a063855098115bc2c17f443dfa`;
- Vercel state: `READY`;
- `/api/health`: `runtime=vercel-fastapi`, session signing READY, AssemblyAI READY, AI33 READY, full server-side voice readiness TRUE.

Truth boundary:

- `Vercel Preview Runtime = PROVEN`;
- Deployment Protection / Vercel Authentication is still enabled;
- therefore permanent judge/public accessibility is not yet proven;
- browser voice core-loop proof must still be repeated on this deployed runtime before production promotion.
