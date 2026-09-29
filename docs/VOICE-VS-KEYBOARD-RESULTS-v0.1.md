# ERRATA — Voice vs Keyboard Baseline Results v0.1

**Paired runtime SHA:** `9bf768bd77200b8363fa8cc9ab57fbd4993ccdc6`  
**Voice evidence:** `evidence/controlled-streaming-v0.1/20260929-171731`  
**Keyboard evidence:** `evidence/keyboard-baseline-v0.1/20260929-172009`

## First paired measurement

Both paths produced the exact same semantic operations and the same revision trajectory for the bounded scenario.

### Initial change

Voice:

- speech → human apply: `22,249.2 ms`
- speech → canonical applied: `23,787.2 ms`

Keyboard:

- entry: `6,127.5 ms`
- entry → canonical applied total: `6,130.0 ms`

Semantic operations: exact match.

### Correction

Voice:

- speech → human apply: `15,296.1 ms`
- speech → canonical applied: `16,815.7 ms`

Keyboard:

- entry: `7,853.3 ms`
- entry → canonical applied total: `7,854.8 ms`

Semantic operations: exact match.

## Immediate interpretation

On the first end-to-end paired run, voice safe-stage latency was materially slower than keyboard:

- initial: about `3.88×` the keyboard total;
- correction: about `2.14×` the keyboard total.

However, this headline comparison is not yet a fair measure of **speech capture speed** because the voice timing includes the human delay between provider-final transcript and typing `apply`. The initial voice trial also included an `Unknown command` / re-entry of `apply`, which further inflates that phase.

Therefore this run does **not** prove that voice is intrinsically slower at capture, nor does it prove Voice-native Necessity.

## What is proven

- semantic convergence between voice and keyboard for the bounded scenario;
- same reducer/revision behavior across both input modalities;
- direct keyboard entry is a credible baseline and cannot be ignored;
- the current voice UX adds meaningful confirmation friction.

## Gate result

`Voice-native Necessity` remains **ACTIVE / NOT PROVEN**.

Current evidence is negative for a simple speed-based voice argument. Any promotion now requires a material benefit beyond headline latency, such as:

- hands/eyes availability during concurrent operational work;
- lower interaction burden when the operator is already speaking;
- faster correction once confirmation UX is improved;
- better workflow continuity under realistic operator conditions.

The comparator has been upgraded to separate:

1. speech start → provider final;
2. provider final → human apply;
3. human apply → canonical applied;
4. speech start → canonical applied.

Re-running the comparator against the same evidence is sufficient to decompose this first paired run; no new live voice capture is required for that decomposition.
