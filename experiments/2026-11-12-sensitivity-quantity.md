# Cycle 20: screen sensitivity, and a tiny training-quantity comparison

## Synthetic sensitivity, not a new acceptance rule

Fifteen authored cases compare the unchanged eight-onset interval-window guard,
whole-line interval edit similarity, exact interval/onset/gate matching, and
onset/gate matching normalized by the first positive onset interval. Cases cover
identity, transposition, origin shift, uniform time scaling, one-tick onset/gate
edits, pitch alteration, insertion/deletion, common scale/constant contours,
seven-note identity and an eight-note excerpt embedded in a longer sequence.

The formal batch plan was saved before the batch, but transform identities had
already been exercised in unit tests. This is transparent synthetic validation,
not blind preregistration or empirical labels of plagiarism. The current real
source gate is directly imported, not confused with an older grid-based screen.

Findings:

- Pitch-only matching ignores rhythm, so it flags common contours too. Adding
  exact timing distinguishes the constructed different rhythms, but a one-tick
  local edit also breaks exact timing. That is sensitivity, not automatically
  better discrimination of meaningful musical similarity.
- Uniform time normalization restores the scaled example but also matches a
  scaled common contour. It does not measure distinctiveness or human judgment.
- Seven-note identity has no eligible eight-note window yet whole-line similarity
  equals1. An exact eight-note core embedded in a longer line scores0.777778
  globally but still matches locally. Length and coverage matter.
- Tempo metadata is not part of these tick descriptors; a tempo-only change is
  invisible, while scaling ticks is a different transformation. Original
  absolute speed and performance intent are not recovered by normalization.

All15 case results reproduce. Counts are distinct matching signatures, not
occurrence counts. No threshold was selected, no new metric was applied to
Telemann or other real sources, and Telemann's blocked decision remains intact.
Constructed provenance is not a copyright ground truth or proof of musical
meaning. The companion interpretation document separates source independence,
output reproduction review and within-output recurrence.

## User-requested quantity comparison

The owner asked to try learning from more material. Start with the authorized
small corpus instead of silently admitting the newly pending sources. Freeze
all seven nonempty subsets of the existing three conservative families before
new calculations:376;888+889 kept together;789. This gives three one-family,
three two-family and one three-family combinations. The last uses all4works and
364notes. One-family subsets contain85,120or159notes, and one contains2works:
family count is not the same as work count or event count.

Use identical factorized timing and previous-gate k4 models, supports and priors
for every subset. Evaluate both already observed580and640, report both separately
and their equal-work NLL mean. No diagnostic is fitted, no fresh validation is
claimed, and no model is selected. This is14tinyCPU fits/28evaluations, not
large-scale training; timing prediction says nothing directly about generated
melodic appeal.

Equal-subset mean of equal-diagnostic-work NLL (lower predicts timing better):

| Training families | Subsets | Factorized | Previous-gate k4 |
|---|---:|---:|---:|
| 1 | 3 | 8.660327 | 7.983022 |
| 2 | 3 | 6.933649 | 6.005101 |
| 3 | 1 | 6.024472 | 4.994781 |

Averages improve with more of this small corpus, but this is not a causal
sample-size result: content, number of notes, number of works and family mix
change together. Subsets overlap and are not independent replications. Adding
material need not improve every individual comparison. All subset outcomes are
retained, including unfavorable additions, rather than only the average trend.
The full-corpus condition is a reproduction of existing model results.

## Additional material: no uncertain data used

New Burgmüller/Bas Wassink candidates202and214 have explicit legacy typesetter PD
dedication and historical composition evidence. For202, an early Benoît-edition
incipit matches, but the actual cited Litolff edition is not independently
identified;214's incipit is not yet visually corroborated. Both remain pending,
not trained or scored. Two works in one Op.100/contributor/edition family are
not two independent families. Their right-hand MIDI tracks also contain chords,
not an isolated melody; no forced extraction is performed.

## Limits and next step

A larger, rights-cleared, stylistically varied corpus may improve coverage or
may introduce mismatched rhythms/styles. The next quantity study should separate
fixed note-budget comparisons from whole-family additions, keep calibration and
future evaluation distinct, and retain exact source rights. Human listening is
still needed to assess whether improvements matter musically. No new audio,
public release, main merge, live Cantabile change, GPU or paid operation.

## Independent reproduction and negative additions

The independent reviewer reproduced all7subset rows and summaries. The4full-data
NLL values (two models ×580/640) exactly match historical reports. A separately
labeled **post-hoc** diagnostic enumerates all9 single-family-addition edges:
for each model, equal-work NLL worsens on3of9edges. For example, adding789to the
888+889family increases events85→205 but worsens Adam640NLL from9.6924→10.7108
for factorization and9.0565→9.9673for context. These are dependent comparisons,
not18independent trials or a prespecified hypothesis test. They directly caution
against saying that every extra training example improves the model.

Six synthetic sensitivity tests and one family-subset test are new. Full suite
222discovered,221passed,1existing actual AudioAnalyzer integration skip;
dependency-free222discovered,184passed,38expected optional skips. Compileall and
diff checks pass. Repeated synthetic results and quantity results match; source
and model hashes are retained. No candidate rights or fixed admission threshold
was relaxed to make the results look better.
