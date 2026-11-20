# Cycle12: small onset/gate experiment on a fixed outcome space

## Before scoring

Fixed PPQ384 and the timing-pair outcome space: onset delta0..12288ticks,
sounding gate1..12288ticks (151,007,232 possible pairs). Sparse counting models
avoid allocating that Cartesian table. Joint model uses empirical pair counts
plus total uniform prior mass1; factorized model multiplies two separately
smoothed marginals, each with prior mass1. Same outcomes, but different prior
structure: do not attribute the difference to factorization alone without that
qualification. Both are small timing models, not neural or phrase models.

Fit only the old four training works376/888/889/789,364 notes total. Brahms580
was previously rights-reviewed and representation-inspected, but predictive-
unscored. It is not untouched/blind data. Its composer/contributor differs from
training; source infrastructure remains shared. Cornelius583 stays reserved in
the same contributor/publisher family as580, not a second independent cohort.

Before evaluation, four source comparisons find zero exact8-onset pitch-interval
matches and zero exact pitch/rhythm phrase matches. Whole-interval edit
similarities0.1758..0.2532 are below both the independent review's0.80 threshold
and the predeclared0.90 threshold. Protocol deviation: the driver used the reviewer's stricter0.80 stopping
threshold rather than the plan's0.90. The reviewer declared0.80 before its
similarity computation; both thresholds give the same admission result. The
original plan is retained, not rewritten after seeing scores.

No local-approximate/perceptual originality
clearance follows from this screen. Plan, code and source hashes were saved
before scoring. No tuning or training reassignment followed the results.

## Timing prediction result

Brahms580 has92 events, all exactly representable with no rounding or unsupported
values. Of these,51 joint pairs,86 onset deltas and89 gates occurred in training.

| Timing model | Unconditional NLL per pair |
|---|---:|
| Joint empirical/prior |12.599041|
| Factorized marginal priors |4.613662|

Factorized smoothing can combine familiar components into unseen pairs. This
is one inspected new-family work, not broad generalization. It is also a
DIFFERENT task from previous REST/HOLD/pitch-duration event evaluations, so their
NLL numbers cannot be directly ranked. No pitch likelihood or human preference
is measured.580 is now predictive-observed and must never be relabeled fresh.

## Bounded generation

Both models use seeds0..9, training-only pitch vocabulary sampled uniformly,
eight6/8bars (9216ticks), max256notes and64 attempts per note. Conditional timing
sampling retains only pairs fitting the remaining target. Same-pitch active
retrigger and a fourth simultaneous note reject; no gate clipping or forced
advancement. Completing means a gate ends exactly at target, not a learned
cadence. Generation constraints are not applied to the evaluation likelihood.

- Joint:10/10 complete,19..45 notes.
- Factorized:9/10 complete,22..33 notes; seed1 blocked by the per-note attempt
  limit (81 cumulative rejections, not81 attempts in one note). Keep the failed
  attempt, do not replace it with a different seed.
- All19 complete outputs pass modeled MIDI roundtrip and zero exact8-onset
  pitch-interval copying checks against training plus580. The latter is only
  an output safety reference, never training or parameter selection.
- Exact report/MIDI hashes reproduce in two full runs. Generated MIDI stays
  outside Git; no audio or learned-model release.

Important failure of interpretation: even the joint timing model generates
many overlaps (6..29 overlapping onsets per joint sample). It pairs the current
onset delta with the current gate, but has no learned dependency between the
previous gate and the next onset. Therefore it has not learned when a notated
grace ornament should overlap. Uniform pitch vocabulary also provides no
coherent melody/harmony model. Better test likelihood does not make these
samples musically better or safer to publish.

Diversity is not optimized here: previous constrained-selection results remain
separate. A next experiment should learn the previous-gate/next-onset dependency,
compare duration/pitch/overlap statistics and human listening without tuning on
580. Source-specific ornament interpretation must not become guessed labels.

## Verification and failures

174 tests discovered,173 passed, one existing actual AudioAnalyzer integration
skip. Seven new tests verify exact normalization/support, unseen probabilities,
legal deterministic conditional sampling, active-pitch/polyphony limits,
bounded failures and invalid inputs. Compileall and whitespace checks pass.
Dependency-free suite also checked; optional integrations remain skipped.

The initial comparison report is retained outside Git. Subsequent driver edits
only added support/overlap/failure counts and corresponding code hashes; no
model, support, prior, seeds or evaluation set was changed after the first score.
Source and score review was independently checked. No main merge, live Cantabile
mutation, raw source publication, large compute or paid action.

Reproduce with `tools/compare_onset_gate_models.py --corpus REVIEWED_CORPUS
--source REVIEWED_580_MIDI --output NEW_DIRECTORY`. Fixed source hashes and
rights-backed manifest validation precede fitting/scoring.
