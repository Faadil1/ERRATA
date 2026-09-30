# ERRATA — Post-Vertical-Slice Depth Gap Review v0.1

**Trigger:** bounded live vertical slice / Prototype Killer promoted  
**Lifecycle:** DELIVER  
**Purpose:** identify what remains between a technically valid prototype and a judge/operator-credible product slice.

## 1. Review decision

The vertical slice is real enough to continue.

The remaining risk is no longer “can the central mechanism work at all?” The main risks are now:

1. whether ERRATA's output is independently valid/consumable;
2. whether the terminal harness can become a credible operator surface;
3. whether voice delivers material workflow value in real operating context;
4. whether public-network data exposes resolver/consequence gaps;
5. whether evidence/story/demo make the product legible without overclaiming.

Therefore the correct next move is **depth expansion**, not more generic voice-turn tuning.

## 2. Gap matrix

| Priority | Gap | Current status | Why it matters | Promotion proof |
|---|---|---|---|---|
| P0 | External/canonical GTFS-RT validation | BLOCKED | ERRATA's own wire parser cannot prove independent correctness | external validator accepts generated artifact |
| P0 | Independent consumer | BLOCKED | final output must be useful outside ERRATA | separate consumer parses/observes corrected final state |
| P0 | Operator review surface | BLOCKED | terminal logs are not a product surface | real UI shows transcript, diff, rev/hash, validation, commit |
| P0 | Public-network realism | ACTIVE/BLOCKED by data path | synthetic fixture can hide entity/route edge cases | run bounded scenario on public/realistic network data |
| P1 | Voice-native necessity | ACTIVE | near timing parity is not necessity | operator/context trial shows compensating workflow benefit |
| P1 | External operator evidence | BLOCKED | intended user value is still inferred | at least one representative external operator/user walkthrough |
| P1 | UNBOUND_TIME_VALUE live isolation | ACTIVE | new guard exists but latest recovery run did not isolate it | credentialed malformed correction → REVIEW_REQUIRED/no drift |
| P1 | Deterministic judge demo | ACTIVE | evidence exists but is log-heavy | repeatable scripted demo with proof above the fold |
| P1 | Judge Performance Assurance | ACTIVE | hostile questions remain | evidence-backed claim matrix + Q&A rehearsal |
| P1 | As-built reconciliation | BLOCKED | design docs contain historical superseded paths | reconcile PRD, README, architecture, registry after UI/output work |
| P2 | AssemblyAI load-bearing ablation | ACTIVE | current use is real but broader dependency claim is not measured | compare with direct/alternative input while keeping shared core |
| P2 | Operational economics | ACTIVE | latency/API usage not decision-ready | scenario-level latency/cost measurements |
| P2 | Naming/collision | ACTIVE | ERRATA remains a working name | bounded naming check before packaging |
| P2 | Red-team runtime corpus | BLOCKED | current failure cases came opportunistically | deliberate corpus of STT corruption/ambiguity/retry cases |

## 3. P0 delivery sequence

### D1 — External acceptance path

Build/choose a validator path that is genuinely outside ERRATA's own parser.

Required output:

- serialized bounded GTFS-Realtime artifact;
- external validation result;
- immutable evidence receipt;
- explicit scope of what the validator checked.

### D2 — Independent consumer

Use a separate consumer implementation/library/process to read the artifact and assert the final service state.

It must not reuse ERRATA's own serialization/parser code as the only acceptance mechanism.

### D3 — Operator review surface

Build the smallest credible UI around the **existing shared core**, not a new logic stack.

Above-the-fold minimum:

- current change identity;
- revision/hash;
- transcript or direct-entry input;
- pending/applied/review-required state;
- semantic diff;
- validation/refusal reason;
- affected service/consequence summary;
- commit control;
- evidence/truth label.

### D4 — Public-network scenario

Run the hero flow against a real/public GTFS dataset or otherwise representative non-synthetic network dataset.

Do not imply agency production integration.

## 4. P1 validation sequence

### V1 — Isolate UNBOUND_TIME_VALUE live

Run a focused credentialed negative case where no earlier fragment contains a valid END cue.

Expected:

- `KEEP=Cumberland` may parse;
- `UNBOUND_TIME_VALUE` must be emitted;
- REVIEW_REQUIRED;
- identical before/after revision and hash.

### V2 — External user/operator walkthrough

Measure:

- task comprehension;
- time to initial staged change;
- time to correction;
- number of retries/context switches;
- whether voice helps when hands/eyes are occupied;
- whether the revision/diff model is understandable;
- whether refusal/review behavior increases or decreases trust.

One trial is evidence, not adoption.

### V3 — Judge-ready deterministic demo

Canonical story:

1. stage change;
2. show rev/hash;
3. correction amends same truth;
4. malformed correction refuses atomically;
5. stale commit refuses;
6. reconnect preserves state;
7. external validator/consumer sees final output.

The demo should never depend on a lucky live STT transcript for every judge-critical proof. Use live voice where useful, but preserve deterministic proof receipts.

## 5. What not to build yet

Do not expand into:

- broad conversational assistant features;
- multiple transit domains;
- autonomous publication;
- production authentication/agency IAM;
- route-planning/detour optimization;
- rich analytics dashboards;
- multi-agency tenancy;
- speculative passenger-impact models.

Those would increase surface area before the current P0 proof gaps are closed.

## 6. Kill / pivot conditions

Reconsider the product direction if any of these occur:

- external validator rejects the bounded artifact and the fix requires abandoning the current state model;
- independent consumer cannot reconstruct the intended final service state;
- operator surface requires modality-specific business logic that breaks the shared core;
- real/public network data produces frequent unresolved or silently wrong entity binding;
- representative operators find direct structured entry clearly preferable with no compensating voice benefit;
- judge-critical proof depends on manually explaining terminal logs.

## 7. Delivery gates after this review

The review itself is complete when this document is canonical.

Remaining gate progression:

- `Living PRD → PROVEN`
- `Post-Vertical-Slice Depth Gap Review → PROVEN`
- `Spec Kit → ACTIVE`
- `External / Canonical GTFS-RT Validation → next P0`
- `Independent Consumer → next P0`
- `Real-user Surface → next P0`

## 8. Immediate next workstream

**External Acceptance Slice**

Deliver one bounded artifact from the existing canonical state through:

`ERRATA serializer → external/canonical validation → independent consumer assertion → evidence receipt`

Do this before investing in visual polish.

The operator UI can then be built against a product core whose final artifact is independently proven, rather than merely visually persuasive.
