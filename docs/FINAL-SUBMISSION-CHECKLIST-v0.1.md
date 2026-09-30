# ERRATA — Final Submission Checklist v0.1

Do not call the submission final until every blocking item below is checked.

## Eligibility / submission

- [ ] Lablab dashboard shows **Submitted / Finalized**, not Draft.
- [ ] ERRATA appears from the account's submission page and opens the intended public project page.
- [ ] Discord membership/account connection is accepted by Lablab.
- [ ] Public GitHub repository is the repository linked in the submission.
- [ ] `main` contains the same product shown in the video and demo URL.

## Public runtime

- [ ] Deployment Protection is disabled for the judge-facing production URL.
- [ ] Production URL opens in a private/incognito browser with no Vercel login.
- [ ] `/api/health` binds the production runtime to the exact merged git SHA.
- [ ] `session_signing_ready = true`.
- [ ] `assemblyai_ready = true`.
- [ ] `ai33_ready = true`.
- [ ] No server secret appears in page source, network payloads, screenshots or receipts.

## Browser voice proof

- [ ] Microphone permission flow succeeds on the judge-facing URL.
- [ ] Base Route 55 speech previews without mutation, then Apply gives rev2.
- [ ] EN/FR correction previews against the same change, then Apply gives rev3.
- [ ] Incomplete correction produces ghost/refusal with zero revision/hash drift.
- [ ] Stale reviewed hash is refused.
- [ ] Current reviewed hash commits.
- [ ] Downstream panel independently decodes the current serialized GTFS-RT bytes.
- [ ] Final receipt contains exact runtime SHA and client voice events.
- [ ] Context-aware streaming events are present if claimed.
- [ ] Barge-in is shown only if Scenario I passes without self-capture.

## Twilio phone path

- [ ] If shown or mentioned as implemented in the submission, real Twilio credentials are configured server-side.
- [ ] Real call reaches `/twilio/voice` and signature validation passes.
- [ ] Media Stream reaches AssemblyAI using native μ-law 8 kHz.
- [ ] Review SMS arrives before DTMF Apply.
- [ ] DTMF 1 applies only a READY_TO_APPLY preview.
- [ ] DTMF 2 discards with zero canonical effect.
- [ ] Real-call evidence is preserved.
- [ ] If any item above fails, describe Twilio as an experimental/next transport, not a proven demo feature.

## Video / presentation

- [ ] 85–95 second main video recorded from the public production build.
- [ ] Product appears within the first 5 seconds.
- [ ] Live AssemblyAI transcript appears within the first 30 seconds.
- [ ] Same `change_id` / rev1→rev2→rev3 is visually legible.
- [ ] Ghost speech / zero canonical effect is visible.
- [ ] Stale refusal + current commit are visible.
- [ ] GTFS-RT downstream consequence is visible.
- [ ] No unproven claim is spoken or shown.
- [ ] Backup recording is retained in case live demo connectivity fails.

## README / metadata

- [ ] Demo URL is near the top of README.
- [ ] Video/GIF is near the top if the platform supports it.
- [ ] One-sentence problem and user are visible before governance details.
- [ ] AssemblyAI architecture is visible before internal assurance material.
- [ ] Exact phrases to try are visible.
- [ ] Installation and secret names are documented without exposing values.
- [ ] Cover image and tags match transit operations / voice / safety rather than generic AI.

## Provider readiness

- [ ] AssemblyAI quota/credits checked before submission.
- [ ] AI33/ElevenLabs credits checked before submission.
- [ ] Twilio balance/number/SMS capability checked if Twilio is shown.
- [ ] Fallback behavior is truthful if any optional provider is unavailable.
