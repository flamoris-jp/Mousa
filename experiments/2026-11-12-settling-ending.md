# Cycle16: a settling-ending hypothesis, not learned tonal cadence

The current small model does not infer key, harmony or phrase function.
Inventing a tonic from mixed-key training material would confuse a pitch target
with a musically justified cadence. This experiment instead tests a narrower,
explicit ending proposal: a relatively long final generated note approached by
a small pitch movement, within the last bar-sized window. It is a structural
selection rule, not a claim of tonic/dominant understanding.

Use the frozen optimized generator with25% uniform pitch mixture and at most
384ticks of trailing silence. Generate the same four candidates per group for
both comparisons. Baseline chooses the first complete copy-safe candidate;
the intervention chooses the first such candidate meeting the fixed endpoint
conditions. Keep all candidate results, failures and required candidate counts.
A better selected metric is expected by construction and does not establish
musical improvement. Reusing a larger pool also consumes more generation work
than simply accepting the first result in deployment.

The endpoint proposal must have at least two onsets, last generated onset in
the final1152ticks, gate at least384ticks, absolute last pitch step at most two
semitones, and no other note ending later. These thresholds describe the
hypothesis, not a universal rule. Repeated pitches can qualify, long endings can
sound static, and stepwise motion can still end on a harmonically unstable note.
No key or chord labels are fabricated.

Old four training works remain the only fitted sources. Already-observed580 is
an explicit copying reference, not a new evaluation set;583 stays reserved.
Source rights and generated-output resemblance remain separate checks. No
human ratings are inferred from structural results or previous missing feedback.

## Fixed-pool results and failure accounting

All40 candidates generated successfully, with zero copy-guard failures. Only
five of10 groups contain an eligible candidate within the four-candidate limit.
The other five remain `no_eligible_candidate`, not repaired or omitted. Selected
seeds are2/4/9/none/none/20/none/28/none/none for groups0..9.

Matched groups0,1,2,5,7 give equal denominators5:

| Mean descriptor | First candidate | Ending-proxy selection |
|---|---:|---:|
| Last gate, ticks |441.6|537.6|
| Absolute final pitch interval |2.2|0.8|
| Whole-line absolute interval |3.591052|3.894323|
| Above-octave interval fraction |0.022685|0.049257|
| Distinct pitches |12.8|13.4|

The selected local endpoint descriptor improves because it is the selection
criterion, while large leaps elsewhere increase. Full-baseline means over10
must not be compared without qualification against selected means over5.
Failure reasons across candidates include22 short final gates,17 large final
intervals and2 final onsets outside the last-bar window; reason flags overlap.

Both analyses used all40 generated candidates. A sequential practical search
would inspect28 candidates including exhausted groups, versus10 for first-
success baseline, and still leave five groups without an eligible result. More
selection work is not free and does not establish better music.

## Post-plan simultaneity concern

An onset-order pitch difference is not necessarily a melodic approach if the
last two notes begin simultaneously. This concern arose after the initial plan
and run began, so the eligibility rule was not silently changed. A separate
post-run channel-event diagnostic finds zero such cases in all40 candidates;
requiring strictly increasing final onset times would leave these selected
seeds and counts unchanged. The generic rule still has this limitation and
must be amended explicitly before a future experiment that claims an actual
melodic approach. Even distinct onsets do not identify a voice in polyphony.

## New reserved independent material

Three source candidates were investigated. Adam's *Minuit Chrétiens* (Mutopia640)
has a new composer and contributor, Gérard Gréco, relative to used families.
The reviewed LilyPond carries an explicit legacy PD dedication, with its linked
MIDI. A separate historic Grus sixth-edition scan corroborates the cover, plate
and vocal incipit; the circa1852 date is catalog metadata, not a printed date.
Only the incipit was collated, not every note or the complete piano part.

Exact vocal track2 roundtrips98 notes,4/4, selected/global EOT40704/49152;
grace-note overlaps and source bytes remain untouched. The rights/evidence
ledger records authors, terms, URLs, acquisition time and hashes. Keep this
source **reserved, untrained and predictive-unscored**, not untouched. It still
needs a separately declared family/similarity screen and evaluation design
before use. Candidates586/1361 share the already-observed Johnson contributor
family and do not supply the requested independent-contributor evidence.

## Verification and next question

199 tests discovered,198 passed, one existing actual AudioAnalyzer integration
skip. Six new ending/selection tests cover thresholds, bounds, source screening,
fixed seeds/all candidates and no-eligible outcomes. Compileall, dependency-free
checks and whitespace checks pass. Full repeated groups/metrics/statuses and
all40 MIDI bytes match; exact EOT, trailing-rest bound, max3voices and no active
same-pitch overlap were checked. Original model/source hashes remain unchanged.

No listening result, tonal cadence, broad generalization or public-release
clearance is claimed. No main merge, live-project edit, raw corpus/model/audio
publication, GPU or fees. The next useful question is whether people actually
prefer these endings, and whether a separately justified key/harmonic context
improves them without merely optimizing another descriptor.

Reproduce `tools/compare_settling_ending.py --corpus REVIEWED_CORPUS --source
REVIEWED_580_MIDI --frozen-plan experiments/2026-11-12-efficient-ending-plan.json
--output NEW_DIRECTORY`. Media and raw source files remain outside Git.
