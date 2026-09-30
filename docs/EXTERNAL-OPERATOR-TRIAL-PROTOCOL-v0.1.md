# ERRATA — External Operator Trial Protocol v0.1

**Gate:** External Operator Evidence  
**Status:** READY / human participant required  
**Scope:** usability + workflow-value evidence, not adoption

## Objective

Test whether a representative transit-operations user can understand and operate the ERRATA review model without developer coaching, and whether voice-assisted amendment would provide material workflow value relative to structured/direct entry.

This protocol must not be used to manufacture an endorsement. One participant is evidence, not adoption.

## Participant

Preferred:

- transit controller / dispatcher / service-planning or control-centre practitioner;
- adjacent transit operations professional if a controller is unavailable.

Record role category only unless the participant explicitly agrees to attribution.

## Session length

10–15 minutes.

## Setup

Use the local operator review surface:

`python scripts/run_operator_surface.py`

The facilitator may explain only:

> ERRATA stages one service change, lets corrections amend that same change, and requires explicit human review before commit.

Do not explain where buttons are or what outcome to expect before each task.

## Tasks

### T1 — Stage a change

Participant receives:

`Route 55 west, skip King Edward and Cumberland until 9:30.`

Observe:

- time to first successful staged state;
- whether revision/hash concept is understood;
- whether current route/window/skips are found without coaching.

### T2 — Correct the same change

Participant receives:

`Wait, keep Cumberland. Make it 10.`

Ask after completion:

- “What changed?”
- “Did this create a new change or amend the existing one?”

Expected conceptual answer:

- Cumberland restored;
- end time 10:00;
- same change identity, new revision.

### T3 — Handle an incomplete correction

Participant receives:

`Wait, keep Cumberland. Make it.`

Observe whether REVIEW_REQUIRED is understood as a safe non-mutation rather than a crash.

Ask:

- “Did ERRATA change the operational state?”

### T4 — Stale review

Use the prior-hash affordance.

Ask participant to attempt commit.

Observe whether STALE_REVIEW is understandable.

### T5 — Current commit

Participant commits the current reviewed hash.

Observe:

- whether the protected-human-action framing is clear;
- whether the final sealed state is understandable.

## Voice-value questions

After the direct-entry tasks, ask:

1. In your real work, when would speaking this correction be easier than typing/form entry?
2. When would voice be inappropriate?
3. Would a short correction such as “keep Cumberland, make it 10” reduce a context switch?
4. Would you trust voice more, less, or the same if the semantic diff must be reviewed before commit?
5. What information would have to be visible before you would authorize a change?

Do not ask whether the participant “likes AI.”

## Measures

Capture:

- task completion: pass/fail;
- completion time per task;
- facilitator interventions;
- retries;
- misunderstood fields;
- whether participant correctly identifies same change identity;
- whether participant correctly identifies REVIEW_REQUIRED as no mutation;
- whether participant understands stale-hash refusal;
- qualitative voice-value statements;
- top missing information before commit.

## Evidence labels

Allowed:

- `OBSERVED_EXTERNAL_USER`
- `INFERRED_WORKFLOW_VALUE`
- `UNKNOWN`

Do not convert one participant’s positive reaction into “operator demand,” “adoption,” or “validated product-market fit.”

## Promotion rule

`External Operator Evidence → PROVEN` only in a bounded evidence sense when:

- at least one representative external participant completes the session;
- the participant is not the builder;
- results are preserved;
- facilitator interventions are recorded;
- negative feedback is preserved;
- no endorsement is fabricated.

Voice-native Necessity remains separate. A trial can support or weaken that hypothesis but does not automatically prove it.

## Trial receipt template

Create:

`evidence/operator-trials/<date>-<participant-code>/trial.json`

with:

- participant role category;
- external_to_build_team: true;
- start/end timestamps;
- task outcomes;
- intervention count;
- participant quotes only with permission;
- voice-value answers;
- final interpretation with OBSERVED / INFERRED / UNKNOWN labels.
