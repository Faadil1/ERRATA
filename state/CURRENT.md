# ERRATA — CURRENT

**Lifecycle:** DESIGN  
**Workstream:** Technical Reality / Prototype Killer — LIVE AssemblyAI v0.1  
**Concept:** v2 relocked  
**Brand:** ERRATA working name; Naming / Collision Gate remains ACTIVE.  
**Canonical feature branch:** `technical-reality-live-assemblyai-v0.1`

## Current truth

The deterministic `LOCAL_STUB` core is promoted on `main` and reproduced by GitHub Actions.

This branch adds the first executable **live AssemblyAI adapter** while preserving the same canonical reducer and truth boundaries.

The adapter implements:

- final-transcript binding;
- `tool.call → PREPARE` only;
- pending candidate batches with no canonical side effect;
- `reply.done.status == interrupted → DISCARD`;
- completed-reply dry-run validation before one atomic reducer apply;
- dynamic route-derived keyterms via `session.update`;
- microphone + speaker transport at 24 kHz PCM16;
- deliberate disconnect and `session.resume` path;
- raw event / receipt / state snapshot capture;
- hash-bound human commit command;
- unit tests for prepare/discard/amend/commit behavior.

## Runtime diagnostic delta

A first local launch reached the terminal harness but appeared non-responsive. Current AssemblyAI guidance has removed legacy English voice names from the recommended set; ERRATA previously defaulted to `ivy`. The live branch now defaults to `anna`, leaves adaptive silence windows unset, prints `session.ready`, speech start/stop, user/agent transcripts, `reply.done`, and `session.error` to the terminal, and fails fast if `session.ready` is not observed within 10 seconds. This is a corrective implementation change, not a promoted LIVE result.

## Live observation — fragmented correction path

A credentialed run proved the initial live path through `tool.call → PREPARED → APPLIED` for the canonical Route 55 command, including a safe deterministic rejection of a misheard direction before the successful retry.

The subsequent correction was repeatedly split by turn detection into separate final user turns such as `Wait.`, `Keep.`, and `Cumberland, make it 10.`. Native managed tool selection did not reliably reconstruct that fragmented correction.

Corrective architecture now under test:

- native AssemblyAI tool calls remain preferred when present;
- a bounded deterministic `RepairFragmentAssembler` accumulates only final `transcript.user` events;
- the fallback is correction-only, not a general free-form command parser;
- it may recover explicit `KEEP=<currently skipped stop>` and `END=<time>`;
- it deliberately never infers `SKIP` from fragmented fallback context, preventing a misheard KEEP→SKIP from creating a consequential mutation;
- any recovered correction still goes through the same deterministic resolver, validators, and canonical reducer.

This is a redesign response to real runtime evidence, not a promoted LIVE result.

## Evidence boundary

No credentialed microphone run has been observed yet.

Therefore all newly generated runtime evidence from this workstream is still **NOT YET PRESENT**, and the live runner labels future receipts `LIVE_CANDIDATE` until audit.

## Still blocked

- `Prototype Killer`
- `Live Core Loop`
- `AssemblyAI Load-Bearing Integration`
- `Voice-native Necessity`
- `Interruption Side-effect Safety — LIVE`
- `Failure / Recovery — LIVE`
- external/canonical GTFS-RT validation
- third-party consumer acceptance
- `Real Consequence — LOCAL`
- operator desirability

## Protected claims

Do not claim live agency integration, controller adoption, production safety, public-network mutation, external GTFS-RT acceptance, or a successful live AssemblyAI run until exact receipts exist.

## Next human checkpoint

Run the credentialed microphone test with headphones and a valid `ASSEMBLYAI_API_KEY` using:

```bash
python -m pip install -r requirements-live.txt
cp .env.example .env
# add ASSEMBLYAI_API_KEY to .env
python scripts/run_live_assemblyai.py --service-date 20260929 --start-time 09:00:00
```

The first canonical utterance remains:

> Route 55 west, skip King Edward and Cumberland until 9:30.

Then exercise a real barge-in/correction:

> Wait — keep Cumberland. Make it 10.
