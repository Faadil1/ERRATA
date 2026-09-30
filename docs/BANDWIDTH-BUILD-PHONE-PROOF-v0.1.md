# ERRATA — Bandwidth Build Phone Proof v0.1

## Status

`Bandwidth Phone Transport = ACTIVE`.

This is an optional hackathon proof path. The browser AssemblyAI flow remains the primary product demo. Do not present the phone path as live/proven until the real-call protocol below passes.

## Why Bandwidth Build

Current Bandwidth Build documentation advertises a self-serve Voice API trial with:

- no credit card;
- 3,000 trial credits;
- one included US local number;
- access to the full Voice API rather than a sandbox.

ERRATA uses Bandwidth only as a phone/media transport. AssemblyAI remains load-bearing for speech recognition and ERRATA remains the only mutation authority.

## Runtime flow

```text
real phone
  -> Bandwidth inbound Voice webhook
  -> BXML StartStream (bidirectional, inbound track)
  -> PCMU / G.711 mu-law / 8 kHz WebSocket media
  -> AssemblyAI Universal-3.5 Pro Realtime
  -> ERRATA /api/preview/voice
  -> NO MUTATION
  -> Bandwidth Update Call BXML
  -> spoken review inside the same call
  -> DTMF 1 = Apply / DTMF 2 = Discard
  -> same ERRATA parser / validators / reducer
```

The bounded phone proof intentionally performs one reviewed amendment. The canonical browser demo remains responsible for the richer same-identity rev1 -> rev2 -> rev3 correction story.

## Bandwidth account setup

1. Create a Bandwidth Build trial account.
2. Provision the included US local number.
3. Find the Bandwidth Account ID.
4. Create OAuth 2.0 API credentials with the minimum Voice permissions needed for active-call BXML updates.
5. Create or open the Voice Application associated with the trial number.
6. Set its inbound/call-initiated callback to:

```text
https://errata-beige.vercel.app/bandwidth/voice
```

7. Configure HTTP Basic Auth on the Voice Application callback. Choose your own high-entropy username/password and store the same values locally as:

```text
BANDWIDTH_WEBHOOK_USERNAME
BANDWIDTH_WEBHOOK_PASSWORD
```

8. Create a second independent high-entropy username/password for the WebSocket destination:

```text
BANDWIDTH_STREAM_USERNAME
BANDWIDTH_STREAM_PASSWORD
```

These are ERRATA-created credentials. They are not Bandwidth API credentials.

9. Store the OAuth values locally:

```text
BANDWIDTH_ACCOUNT_ID
BANDWIDTH_CLIENT_ID
BANDWIDTH_CLIENT_SECRET
```

Never paste any secret into chat or commit it.

## Local secret contract

The final required local group is:

```text
BANDWIDTH_ACCOUNT_ID
BANDWIDTH_CLIENT_ID
BANDWIDTH_CLIENT_SECRET
BANDWIDTH_WEBHOOK_USERNAME
BANDWIDTH_WEBHOOK_PASSWORD
BANDWIDTH_STREAM_USERNAME
BANDWIDTH_STREAM_PASSWORD
```

`BANDWIDTH_PHONE_HMAC_KEY` is generated automatically by the ERRATA deployment script when the group above is complete.

The optional trial number may be recorded locally as:

```text
BANDWIDTH_PHONE_NUMBER
```

## Deployment safety

`scripts/deploy_vercel_local.ps1` behaves fail-closed:

- zero Bandwidth secrets found -> phone transport is skipped;
- only some required Bandwidth secrets found -> deployment aborts and lists missing variable names;
- complete group -> secrets are provisioned to the selected Vercel environment without printing values.

## Real-call proof

After an exact-head production deployment:

1. Verify `/api/health` reports:
   - `bandwidth_phone_transport_configured=true`;
   - `assemblyai_ready=true`;
   - exact expected git SHA.
2. Call the Bandwidth trial number from the allowed/verified destination.
3. Hear the ERRATA greeting.
4. Speak:

```text
Route 55 west, skip King Edward and Cumberland until 9:30.
```

5. The caller must hear a concise review containing route/direction/skips/end time and the explicit statement that nothing has been applied.
6. Before DTMF, canonical state must remain revision 1.
7. Press `2` on one run:
   - caller hears discard;
   - no canonical mutation is assumed or claimed.
8. Repeat the call, same spoken instruction, then press `1`:
   - the signed review token must bind the same call ID, transcript and canonical rev/hash;
   - ERRATA re-previews against fresh rev1;
   - mismatch -> refusal;
   - match -> `BandwidthDTMF1` boundary and revision 1 -> 2.
9. Preserve Vercel/Bandwidth evidence needed to bind:
   - exact git SHA;
   - Bandwidth call ID;
   - AssemblyAI session/capture;
   - reviewed transcript;
   - DTMF boundary;
   - canonical result.

## Promotion rule

Promote `Bandwidth Phone Transport` to `PROVEN` only when a real credentialed call demonstrates the full sequence above.

Code presence, a provisioned phone number, successful OAuth, or an open WebSocket alone are not sufficient.
