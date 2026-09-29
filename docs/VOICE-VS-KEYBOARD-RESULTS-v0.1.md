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


## Decomposed first-run latency

Using the same paired evidence:

### Initial change

- speech start → provider final: `12,114.7 ms`
- provider final → human apply: `10,134.5 ms`
- human apply → canonical applied: `1,538.0 ms`
- keyboard entry: `6,127.5 ms`

Interpretation: the voice capture itself was ~5.99 s slower than keyboard entry on this longer initial command, while an additional ~10.13 s came from waiting before the human confirmation action.

### Correction

- speech start → provider final: `5,804.1 ms`
- provider final → human apply: `9,492.0 ms`
- human apply → canonical applied: `1,519.6 ms`
- keyboard entry: `7,853.3 ms`

Interpretation: voice capture was ~2.05 s faster than keyboard entry for the short correction, but ~9.49 s of confirmation delay erased that advantage.

## Consequence for the next experiment

The evidence does not support a blanket statement that voice is faster or slower.

It does show that the **current confirmation UX is the dominant avoidable latency** in both phases.

The next experiment therefore changes only the human boundary:

- speak naturally;
- press **ENTER immediately when speech is finished**;
- ENTER becomes the explicit human transaction boundary;
- ERRATA sends `ForceEndpoint`;
- the same parser/validator/reducer path follows.

This preserves human authority while removing the artificial wait to read a provider-final transcript and type the word `apply`.

The recorder now also reports whether a new final turn appeared after `ForceEndpoint`, allowing the same run to test `ForceEndpoint Efficacy — LIVE`.


## Immediate-ENTER paired timing — 2026-09-29

The self-bound LIVE packet at runtime SHA `c83f750cc3b7f8d26c936d92a0c2f6525605be30` removes the prior ~9–10 s confirmation wait by making ENTER the explicit human boundary.

Against the existing keyboard baseline:

### Initial change

- voice speech start → human ENTER boundary: `8,450.5 ms`
- voice speech start → canonical APPLIED: `8,785.8 ms`
- keyboard entry: `6,127.5 ms`
- keyboard total: `6,130.0 ms`
- safe-stage delta, voice minus keyboard: `+2,655.8 ms`

### Clean correction

- voice speech start → human ENTER boundary: `4,896.4 ms`
- voice speech start → canonical APPLIED: `5,065.1 ms`
- keyboard entry: `7,853.3 ms`
- keyboard total: `7,854.8 ms`
- safe-stage delta, voice minus keyboard: `-2,789.7 ms`

Across the two successful phases:

- voice safe-stage total: `13,850.8 ms`
- keyboard total: `13,984.8 ms`

The aggregate difference is only ~`134 ms` in this single local trial.

### Interpretation

The immediate-ENTER boundary removes the dominant confirmation friction from the first paired run. The result is **near aggregate parity** for this bounded two-phase scenario, with keyboard faster on the longer initial instruction and voice faster on the short correction.

This does not prove that voice is necessary or generally faster. It does establish that the controlled voice path can be competitive with direct typing while preserving explicit human mutation authority. The strongest observed advantage is correction speed, not initial-entry speed.
