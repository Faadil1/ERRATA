# ERRATA — Voice vs Keyboard Baseline v0.1

## Purpose

Test the `Voice-native Necessity` gate without assuming voice is better.

The comparison uses the same semantic scenario and the same deterministic parser/coordinator/reducer on both paths:

**Voice path**

`microphone → AssemblyAI Streaming → human apply → bounded parser → reducer`

**Keyboard path**

`typed natural-language instruction → bounded parser → reducer`

The comparison is descriptive. It measures time and semantic convergence; it does not declare a winner automatically.

## Required sequence

### 1. Instrumented voice run

Use the hardened controlled Streaming runner:

```bash
python scripts/run_controlled_streaming.py --service-date 20260929 --start-time 09:00:00
```

Run the same two phases:

1. `Route 55 west, skip King Edward and Cumberland until 9:30.`
2. `Wait, keep Cumberland. Make it 10.`

Type `apply` after each spoken instruction.

Then perform:

- stale commit attempt;
- current-hash commit;
- `snapshot`;
- `quit`.

This run now records runtime SHA, UTC timestamps, human apply, commit events, final state, and integrity hashes.

### 2. Keyboard baseline

Run:

```bash
python scripts/run_keyboard_baseline.py --service-date 20260929 --start-time 09:00:00
```

Type the same two sentences when prompted.

The runner measures:

- entry time;
- deterministic processing time;
- total time;
- parsed operations;
- revision/hash outcome.

### 3. Compare

```bash
python scripts/compare_voice_keyboard.py \
  --voice-dir <instrumented voice evidence directory> \
  --keyboard-dir <keyboard baseline evidence directory>
```

The comparator reports, per phase:

- voice speech-start → human apply;
- voice speech-start → canonical applied;
- keyboard entry time;
- keyboard total time;
- semantic operation match;
- resulting revision.

## Promotion rule

`Voice-native Necessity` remains `BLOCKED` until the evidence shows a material property that voice contributes in the target workflow.

Speed alone is not sufficient. The interpretation must consider:

- time to stage a change;
- correction friction;
- semantic error/refusal rate;
- whether voice keeps hands/eyes available for concurrent operational work;
- whether the explicit human apply boundary preserves safety without erasing the value of speech.

A single local comparison is a Prototype Killer signal, not operator-adoption evidence.
