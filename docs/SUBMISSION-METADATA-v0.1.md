# ERRATA — Submission Metadata

This file records the submission-facing metadata that matches the implementation in this repository.

## Category

- Voice Assistant

## Technologies actually used

- AssemblyAI Universal-3.5 Pro Realtime
- AssemblyAI WebSocket Streaming v3
- AI33 Pro
- ElevenLabs TTS via AI33
- Python
- FastAPI
- JavaScript
- HTML / CSS
- Vercel
- GTFS-Realtime / Protocol Buffers
- Bandwidth phone transport adapter

## Public links

- Demo: https://errata-beige.vercel.app/
- Repository: https://github.com/Faadil1/ERRATA

## Product path

```text
Voice input
  → AssemblyAI realtime STT
  → ERRATA non-mutating draft
  → explicit human Apply
  → deterministic canonical revision
  → AI33 operator guidance
  → hash-bound commit
  → GTFS-Realtime consequence
```

## Truth boundary

The browser voice surface is the primary judge-facing product path. Bandwidth is a separate optional phone transport adapter into the same core and should not be treated as proven live-call evidence without a credentialed call receipt.

The Vercel production runtime was verified on code commit `5bc291c4efa7bfde4124988e7752f8f5beadccc8`. Later submission-facing commits only update documentation and submission packaging.
