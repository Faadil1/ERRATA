# ERRATA Evidence Index

This directory contains submission-relevant runtime, voice and downstream validation artifacts.

The goal is to make runtime and validation evidence easy to inspect from one reviewer-facing index.

## Browser voice

<code>browser-voice-v0.1/</code>

Preserves exported browser voice receipts. Each run documents its own classification and exact limitations. Older receipts remain historical evidence and must not be silently promoted to final exact-head proof.

## Controlled streaming

<code>controlled-streaming-v0.1/</code>

Artifacts from controlled AssemblyAI streaming experiments used to verify transcript handling and correction behavior.

## External GTFS-Realtime acceptance

<code>external-acceptance-v0.1/</code>

- <code>OFFICIAL-CONSUMER-CI.md</code> — independent consumption through official GTFS-Realtime bindings
- <code>CANONICAL-VALIDATOR-CI.md</code> — canonical validator summary
- <code>CANONICAL-VALIDATOR-CI.json</code> — machine-readable validator output

## Public-network scenario

<code>public-network-v0.1/</code>

Contains the audit manifest for the scenario built from official STO GTFS source data.

See also:

- [Public-network source boundary](../docs/PUBLIC-NETWORK-SOURCE-STO-v0.1.md)
- [Public-network evidence](../docs/PUBLIC-NETWORK-STO-EVIDENCE-v0.1.md)

## Deployment

<code>deployment/</code>

Deployment receipts and runtime-binding artifacts. A deployment receipt proves only the runtime and SHA it names; it does not automatically prove the full browser voice scenario.

## Deterministic local evidence

- <code>local-stub-v0.1/</code>
- <code>controlled-streaming-v0.1/</code>

These are useful for reproducibility and regression evidence, but they are not substitutes for live browser proof.

## Evidence rule

No artifact is promoted beyond what it directly demonstrates.

- local or simulated evidence is not relabeled as live;
- a historical receipt is not presented as final exact-head proof;
- provider readiness is not the same as a successful real user interaction;
- downstream serialization is verified independently from the voice UI;
- no provider secret belongs in any receipt or committed artifact.
