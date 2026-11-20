# Cycle17: pre-fixed Adam timing validation and a repetition counterexample

## Independent-source conditions before predictive scoring

Adam640 was rights-reviewed and representation-inspected, but had not supplied
predictive scores or training examples. It was never untouched data. Before
scoring, fix the original four training works, three already implemented timing
models, their file hashes, PPQ384 Cartesian support, likelihood task, no-rounding
policy and similarity thresholds. Compare the cycle12 joint/factorized models
and cycle13 previous-gate context with strength4; do not tune after seeing this
source's scores. No pitch likelihood or musical appeal is measured.

Independent screening against13 previous inspected/observed/reserved works
finds zero exact eight-onset interval matches, zero exact interval/rational-
onset matches, and whole-interval similarities0.2062..0.2990, below0.80. Adam,
Gréco and the Grus edition have no identified family overlap with fitted works.
Anonymous contributors for2247/2245 prevent an absolute identity guarantee;
all sources share the Mutopia/LilyPond pipeline. These checks do not establish
perceptual or legal originality, or eliminate shorter/edited quotations.

## Ending and monotony: existing-pool reanalysis

A separate predeclared adaptive comparison uses only the old40 generated
cycle16 candidates, not Adam640 or Cornelius583. Both variants require distinct
final onset times. The first permits a repeated final pitch; the second requires
an actual one- or two-semitone final step. Other endpoint constraints and the
four-candidate budget stay fixed; there is no regeneration or model fitting.

Allowing repetition yields eligible choices in5/10 groups, whereas forbidding
it yields3/10 and raises practical candidate examinations28→33. Completed-choice
means have different denominators and must not be treated as an unbiased causal
comparison. The stricter local rule does not even imply globally less repetition:
whole-line repeated-interval means are0.183972 (five choices) versus0.240632
(three choices). Distinct-pitch means13.4 versus10 reflect changed selection sets,
not established musical superiority. Repeating a final tone can be expressive
and appropriate; neither rule substitutes for hearing the result.

The new comparison explicitly rejects simultaneous final onsets as a melodic
approach, with regression tests. This is separate from the unchanged historical
cycle16 rule and plan. Its reports repeat exactly on the verified existing MIDI
hashes. No human feedback or population preference is inferred.

## Frozen timing result and observation ledger

98/98 Adam events fit the pre-fixed support exactly. Training remains364 events
from the four original works.51 test pairs,82 deltas and90 gates were previously
seen in training.

| Frozen model | Timing-pair NLL/event |
|---|---:|
| Cycle12 joint |13.302415|
| Cycle12 factorized |7.435282|
| Cycle13 previous-gate context, strength4 |6.351487|

All three results are reported without refitting or post-result selection.
Factorized/context variants improve this one timing task, but their smoothing
structures differ. This is one new composer/contributor work, not broad
independent generalization, pitch accuracy, compositional ability or appeal.
No earlier580 scores are pooled as new evidence.

**640 is now predictive-observed.** The authoritative observation record is
`datasets/research-source-observations.json`; it supersedes the old reserved
label. The original rights snapshot stays immutable so pre-score hashes remain
reproducible. It is not current evaluation status and does not permit calling
640 fresh again. Source640 has not entered training.

## Verification and reproduction

The prepare stage writes a new frozen plan and coverage/similarity record
without predictive calls. Scoring requires explicit independent clearance and
unchanged source/training/model hashes. Unsupported outcomes would block the
entire score, not be dropped. First and repeat result reports are byte-identical;
no source files, model code, support, settings or fitted-source set changed.

205 tests discovered,204 passed, one existing actual AudioAnalyzer integration
skip. Three coverage tests and three ending-repetition tests added. Compileall,
dependency-free tests and whitespace checks pass. Independent audit checks
plan/source boundaries separately from the original implementation.

To reproduce frozen scoring, place the committed frozen plan and pre-score
record into a new plan directory as `plan.json` and `prescore-screen.json`, then
run `tools/evaluate_adam640_transfer.py --stage score --corpus REVIEWED_CORPUS
--source REVIEWED_640_MIDI --plan-dir PLAN_DIRECTORY --clearance
experiments/2026-11-12-adam640-clearance.json --output NEW_DIRECTORY`.
The committed clearance is a wording/path-normalized public view; its digest
differs from the original private record retained in initial-report provenance,
so only that metadata field changes on reproduction, not predictive scores.
Do not run prepare again and mistake a repeated evaluation for a first one.

No new media, human preference labels, raw corpus/model publication, live
Cantabile edit, main merge, deployment, GPU or paid operation.
