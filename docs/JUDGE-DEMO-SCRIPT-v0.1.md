# ERRATA — Judge Demo Script v0.1

**Status:** ACTIVE  
**Target length:** 90–120 seconds  
**Demo principle:** live interaction where useful, deterministic proof where load-bearing

## Judge takeaway

> A spoken correction does not create a new change. ERRATA amends the existing revision, invalidates stale review, recomputes consequences, and refuses stale commits.

## 0–15 s — Problem

Show the operator review surface.

Say:

> “Transit control intent changes while people are speaking. The dangerous failure is applying the understood half of a correction or authorizing a stale version.”

Point to:

- change identity;
- revision/hash;
- protected human commit.

## 15–40 s — Same change, correction

Apply:

`Route 55 west, skip King Edward and Cumberland until 9:30.`

Then:

`Wait, keep Cumberland. Make it 10.`

Show:

- same change ID;
- revision increment;
- semantic diff;
- Cumberland restored;
- end time changed to 10:00.

Say:

> “The correction amends the same truth. It does not fork a second request.”

## 40–58 s — Negative path

Reset or use a prepared deterministic state.

Apply:

`Wait, keep Cumberland. Make it.`

Show:

- REVIEW_REQUIRED;
- unresolved cue;
- unchanged revision/hash.

Say:

> “ERRATA can understand part of the sentence and still refuse the whole atomic amendment.”

## 58–75 s — Stale review

Load the prior hash and attempt commit.

Show:

- STALE_REVIEW;
- canonical state unchanged.

Then restore the current hash and commit.

Say:

> “Commit authority belongs to the human and is bound to the state they actually reviewed.”

## 75–95 s — Public-network proof

Show the public-network evidence receipt.

Facts to display:

- STO public GTFS;
- service date 2026-09-30;
- Route 15 / DES ÉRABLES;
- real trip 62759262;
- real stop 3396 remains skipped;
- real stop 7051 restored;
- official GTFS-Realtime bindings PASS;
- MobilityData validator: 0 ERROR groups.

Required truth line:

> “This is a local derived artifact over public STO schedule data. ERRATA did not publish to STO systems.”

Preserve the STO attribution notice.

## 95–110 s — Why AssemblyAI

Show the credentialed live evidence summary:

- Streaming STT;
- explicit human ENTER boundary;
- ForceEndpoint observed;
- reconnect preserves revision/hash;
- short correction faster than typed correction in the bounded paired trial.

Say:

> “AssemblyAI is load-bearing for live capture, but the provider never owns mutation authority.”

Do not claim voice is generally faster.

## 110–120 s — Close

> “ERRATA is not an autonomous dispatcher. It is a controlled compiler for operational corrections: probabilistic speech in, deterministic reviewed change out.”

## Deterministic fallback

If live microphone/STT is unreliable during judging:

1. use direct entry through the same parser/resolver/reducer core;
2. show the credentialed AssemblyAI receipts separately;
3. never pretend the deterministic fallback is live voice;
4. preserve the exact same revision/hash/commit story.

## Demo-killing mistakes

Do not:

- commit rev2 before showing the correction unless intentionally demonstrating sealed-state behavior;
- hide the truth label;
- show only terminal logs;
- claim agency integration;
- claim the STO-derived TripUpdates were published;
- say “voice is faster” without the bounded comparison qualifier;
- skip the malformed correction;
- let a lucky transcript be the only proof of atomicity.

## Required pre-demo checks

- CI green;
- operator surface loads;
- reset works;
- initial + correction works;
- malformed correction yields REVIEW_REQUIRED;
- stale review yields STALE_REVIEW;
- current commit works;
- public-network evidence receipt available;
- AssemblyAI evidence summary available;
- no secrets in browser/logs.
