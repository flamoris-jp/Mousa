# Cycle24: count pathways, work weights and fictional evidence states

## Separate added timing and pitch counts

Cycle23's single-pitch source augmentation worsened observed timing prediction
and changed generation. A frozen2x2comparison now adds583to timing counts only,
pitch counts only, both or neither. The adapter builds each path through the
unchanged validated contextmodel. The pitch intervention changes vocabulary,
initial unigram and interval counts together, not just repeated-note probability.

Allconditions use the same five seeds, priors/support, optimized feasibility,
uniformmix1/4andtail384. Neither/both reproduce the prior control/augmentation
scores and all10private note arrays. The two crossconditions are new diagnostic
interventions, not new independent evaluation data.640/921remain observed;
related580is excluded. No new source is fitted beyond the authorized five.

| 583count path | Same-pitch fraction | Notes | Distinct pitches | Overlap |
|---|---:|---:|---:|---:|
| Neither | .259 | 29.8 | 12.2 | .117 |
| Pitch only | .283 | 30.2 | 12.0 | .162 |
| Timing only | .240 | 30.6 | 11.4 | .301 |
| Both | .309 | 23.2 | 10.0 | .132 |

20/20complete, narrowcopyflags0. Timing-only addition reduces adjacent repetition
in this small sample while both additions increase it. The pathways interact
through stochastic sampling and feasibility; a single-pitch-source explanation
alone is insufficient. Timing NLL7.637873→7.859410changes only with the timing
path. Pitch-only invariance is built into a timing-only prediction task and does
NOT imply pitch is unimportant musically. No human appeal conclusion follows.

## Weighting control: prediction only

A separate exactFractionweighted-count diagnostic compares five predeclared
conditions. It implements the same marginalprior1andcontextk4formula, with
unit-weight probability parity tests. It has no generator. Both diagnostics
remain640/921, no fresh tests or post-result weight selection.

| Weighting | Factorized equal-work NLL | Contextk4 |
|---|---:|---:|
| Raw old4 | 8.506000 | 7.637873 |
| Raw augmented5 | 8.769905 | 7.859410 |
| Augmented5 rescaled to totalmass364 | 8.712011 | 7.834033 |
| Equal-work old4, totalmass364 | 8.727967 | 7.877249 |
| Equal-work augmented5, totalmass364 | 8.968114 | 8.113180 |

Rescaling totalmass removes part, not all, of the observed loss. Equalizing work
weight does not fix it here. Counts relative to prior1andshrinkagek4also change,
so these are not pure causal content or genre controls. Correlated888/889works
are still one source family; equal-work does not mean equal-family or equal-genre.
No weighting winner was adopted. A legitimate single-pitch composition is not
badmusic merely because a different prediction task fits worse after adding it.

The independent reviewer repeated all results and verified exact normalization
on200additional synthetic conditions. Unit-weight contextNLLmatches historical
values exactly; factorized floating differences are at most3.55e-15from operation
order. Fraction denominator bitlength is not bounded for arbitrary external
inputs: this is a controlled small research diagnostic, not a public service.

## Semantic prototype: exhaustive fictional state checks

The unchanged prototype was tested across216combinations:3evidence layers ×
4review states ×3actor roles ×2fictional flags ×3use strings.24schema-valid,
192rejected; actualhumanreports0, trainingeligible0. A schema-valid rejected/
approved/pending record is not authorized data: validity only describes its
structure. Even the approved string cannot admit it to training. No real
comment, semantic label, consent or human preference was invented.

## Independent-material screening

Clementi804's rights remain reviewed, but fixed exact8interval screening flags
training376andobserved2245, plus other references. It remains untrained and
predictively unscored; no new threshold or silent passage deletion. Current
screen status is separate from the historical rights snapshot. Same-work
movements/hands/editions cannot be substituted as independent samples. Common
pattern overlap is not a legal or perceptual copying verdict.

No main merge, publicmedia, liveproject changes, deployment, GPU or fees.

## Additional explanatory counts and checks

A post-hoc count audit (no new model fit) finds88/360zero intervals in the old
work-separated pitch transitions versus167/439after583adds79zero intervals.
B4unigram counts rise40/364→120/444. These directly change pitch proposal counts;
they do not equal realized output repetition because the uniform mixture,
feasibility and timing state intervene. No source lyric/intent label is inferred.

Independent repeat checks preserve20private note-array hashes and all non-time
results. Generation safety bounds pass; no actual MIDI/audio was emitted in this
cycle. Seven new tests cover pathway parity, weighted probabilities and the216
fictional-state matrix. Fullsuite243discovered,242passed,1existing actual
AudioAnalyzer integration skip; dependency-free243discovered,205passed,
38expected optional skips. Compileall/diff checks pass. Frozen old models remain
unchanged; new adapters/diagnostics are research-only and do not deploy anything.
