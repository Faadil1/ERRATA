# ERRATA — Judge Demo Pack v0.1

**Status:** READY FOR REHEARSAL  
**Branch:** `technical-reality-live-assemblyai-v0.1`  
**CI head verified:** `d03db942513e30501a7e68bf037a36dcb4701cf8`  
**Latest strengthened CI:** workflow run `36674855222` — SUCCESS  
**Target:** 90–120 seconds  
**Truth boundary:** judge packaging only; no external-operator validation claim

## 1. Judge thesis

ERRATA treats a spoken operational correction as a revision to one controlled change, not as a second request. Probabilistic speech capture may propose intent, but deterministic validation, revision/hash binding, and explicit human commit authority govern mutation.

The signature sequence is:

`initial intent → same-identity correction → REVIEW_REQUIRED on incomplete correction → stale-hash refusal → current-hash human commit → externally consumable consequence artifact`

## 2. Required demo mode

Preferred mode:

- operator review surface for the human-review/state story;
- credentialed AssemblyAI receipts for live speech-capture evidence;
- deterministic direct entry through the same parser/resolver/reducer core when live microphone reliability would add judge risk.

Never narrate deterministic fallback as live voice.

## 3. 90–120 second run order

### 0–15 s — Operational risk

Show the operator surface with change identity, revision/hash, current truth, and protected commit visible.

Narration:

> Transit intent changes while people are speaking. The dangerous failure is applying the understood half of a correction or authorizing a version that is already stale.

### 15–40 s — Same change, corrected

Apply:

`Route 55 west, skip King Edward and Cumberland until 9:30.`

Then:

`Wait, keep Cumberland. Make it 10.`

Required visible facts:

- same change ID;
- revision increments;
- Cumberland restored;
- end time becomes 10:00;
- semantic diff is visible.

Narration:

> The correction amends the same operational truth. It does not fork a second request.

### 40–58 s — Atomic negative path

Apply:

`Wait, keep Cumberland. Make it.`

Required result:

- `REVIEW_REQUIRED`;
- unresolved cue visible;
- revision/hash unchanged.

Narration:

> ERRATA can understand part of the sentence and still refuse the whole atomic amendment.

### 58–75 s — Review/commit binding

Attempt commit with the prior reviewed hash.

Required result:

- `STALE_REVIEW`;
- canonical state unchanged.

Then commit with the current reviewed hash.

Narration:

> Commit authority belongs to the human and is bound to the exact state they reviewed.

### 75–95 s — Public-network proof

Show the STO evidence summary.

Canonical closure proof:

- public planned STO GTFS;
- service date `2026-09-30`;
- Route 15 / DES ÉRABLES;
- `direction_id = 0`;
- real trip `62759262`;
- stop `3396` remains skipped;
- stop `7051` is restored;
- corrected end `17:52`;
- official MobilityData bindings: PASS;
- canonical MobilityData validator: 0 ERROR groups;
- retained warning: `W002 vehicle_id not populated`.

Required truth line:

> This is a local derived artifact over public STO schedule data. ERRATA did not publish to STO systems.

Preserve STO attribution and last-update notice wherever this source is shown.

### 95–110 s — Why AssemblyAI is load-bearing

Show credentialed evidence, not a marketing claim:

- AssemblyAI Streaming STT was used in the authoritative controlled-capture path;
- human ENTER / ForceEndpoint owns the consequential boundary;
- the bounded atomicity packet preserved revision/hash on an incomplete correction;
- deliberate reconnect preserved the exact canonical revision/hash;
- a valid post-reconnect correction continued the same ServiceChange;
- the bounded paired trial showed near aggregate parity, with voice faster only on the short correction.

Narration:

> AssemblyAI is load-bearing for live capture, but the provider never owns mutation authority.

Do not claim general voice superiority.

### 110–120 s — Close

> ERRATA is not an autonomous dispatcher. It is a controlled compiler for operational corrections: probabilistic speech in, deterministic reviewed change out.

## 4. Exact evidence anchors

### Public-network canonical closure

- source evidence: `docs/PUBLIC-NETWORK-STO-EVIDENCE-v0.1.md`
- closure workflow run: `36674052762`
- closure artifact: `11078928665`
- closure artifact digest: `sha256:4998dd1c8a42cb136ec8b86be7600c95c649b6040f087db32729bc9a9e5ce339`
- TripUpdates.pb SHA-256: `c486f610ab6faddac3ff83104f43233a1f13cc053720f6b50108ad6e62cfb87e`

### Latest strengthened CI revalidation

- workflow run: `36674855222`
- head: `d03db942513e30501a7e68bf037a36dcb4701cf8`
- public-network artifact: `11079153984`
- digest: `sha256:bd4754995ef216500f7f91ff1fc437dbec1a2fedb46aa78cd5f14da94c0239f9`
- external-acceptance artifact: `11079179121`
- digest: `sha256:468e61a6392cfb84ce212946a6d05816594e8d8319ece0a815888af1536bc0c6`
- local-stub artifact: `11079029513`
- digest: `sha256:ad736dad62b4dade9e56e7d8ca6c7caa3f7f1c84fb87b138826089754c7e1827`

The revalidation artifact is a new CI package. It does not replace the historical closure receipt; both are retained with their own run/head identity.

### Credentialed AssemblyAI evidence

Use the existing self-bound and recovery anchors:

- atomicity packet: `evidence/controlled-streaming-v0.1/20260929-175753`
- embedded runtime SHA: `c83f750cc3b7f8d26c936d92a0c2f6525605be30`
- recovery run: `evidence/controlled-streaming-v0.1/20260929-231455`

Truth boundary:

- credentialed live capture and bounded recovery are evidenced;
- external operator desirability is not;
- production agency integration is not;
- voice-native necessity remains ACTIVE, not PROVEN.

## 5. Preflight checklist

Before recording or presenting:

- [ ] CI for the exact demo head is green.
- [ ] Operator surface starts cleanly.
- [ ] Reset returns to the deterministic starting state.
- [ ] Initial amendment produces rev2.
- [ ] Correction produces rev3 on the same change ID.
- [ ] Malformed correction returns REVIEW_REQUIRED with no revision/hash drift.
- [ ] Prior reviewed hash returns STALE_REVIEW.
- [ ] Current reviewed hash commits successfully.
- [ ] STO attribution is visible with source/date.
- [ ] Public-network receipt is locally available.
- [ ] AssemblyAI evidence summary is locally available.
- [ ] No API key, token, or secret appears on screen or in logs.
- [ ] Deterministic fallback is explicitly labeled if used.
- [ ] Browser zoom/layout keeps current truth and protected commit context visible.
- [ ] Final truth line states no STO publication/agency integration.

## 6. Rehearsal scoring

A rehearsal passes only if all are true:

1. 90–120 seconds without skipping the negative path.
2. Same-identity correction is visually obvious without narration alone.
3. REVIEW_REQUIRED is shown as non-mutation.
4. STALE_REVIEW is shown before successful current-hash commit.
5. Public STO proof is readable and truth-bounded.
6. AssemblyAI evidence is presented as credentialed evidence, not generalized superiority.
7. No claim depends on an unshown terminal log.
8. No external-operator/adoption claim is made.
9. The close lands on the controlled-compiler framing.

## 7. Promotion rule

`DEMO` remains `ACTIVE` until at least one full rehearsal/recording completes this checklist.

`External Operator Evidence` remains `BLOCKED` until a representative participant executes `docs/EXTERNAL-OPERATOR-TRIAL-PROTOCOL-v0.1.md`.

Do not trade one gate for the other.
