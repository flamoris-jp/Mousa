# Corpus expansion and human-readable eligibility review

This is preparation, not a new source-admission policy or an executed larger
training run. The current augmented corpus has five works, four conservative
families and 444 selected-track note events. The original frozen corpus remains
four works, three families and 364 events. These are not large-scale datasets.

## Required review packet for each candidate

Keep the original bytes privately, with source URL, acquisition time and SHA-256.
Separate composition, historical edition/arrangement, and MIDI encoding evidence.
Include exact selected track, meter changes, pickup/origin evidence, overlaps,
unsupported events and the distinction between a melody and a polyphonic hand.
A technically readable track does not certify the rest of the file or its rights.

For every similarity flag, give a reviewer:

- candidate and reference IDs, hashes, track and their current training,
  observed-evaluation, unused, blocked or uncertain-rights roles;
- zero-based note-window locations, window length, number of matching occurrences,
  pitch-interval agreement and exact relative-onset/rhythm agreement separately;
- whole-line similarity with its actual lengths, formula, bounds and coverage;
- source-family links independent of the numeric similarity and missing/failed
  reference comparisons, never replaced with a zero score;
- a clear statement of which frozen rule caused the block, plus the unchanged
  decision. A rhythm mismatch or common scale is explanatory, not a waiver.

Raw source passages and audio belong only in appropriately authorized private
review materials after their separate rights review. Repository reports can use
source pointers, positions and summary descriptors. Do not publish an automatic
accusation of copying, or call a screen pass a finding of originality.

A reviewer may record “ordinary pattern,” “potentially meaningful resemblance,”
“uncertain,” or an explanation in their own words. These are suggestions for a
future procedure, not ratings already collected. Preserve the actual wording,
reviewer consent/scope and uncertainty. Algorithm-generated descriptions must not
be relabeled as human judgments. Review can inform a separately prospective
protocol, but cannot override existing frozen experiments or restore blindness.

## Preparing a larger comparison

1. Freeze an inventory before fitting: all admitted work/family IDs, hashes,
   roles and rights evidence; keep related arrangements and contributors grouped
   conservatively. Track rejected and unresolved candidates as well as successes.
2. Reserve new eligible evaluation families before choosing training additions.
   Already scored 640 and 921 remain exploratory diagnostics. Brahms 580 is
   excluded from all 583-augmented independent evaluation because of its shared
   contributor/publisher family. A new source is not automatically a new family.
3. Once enough eligible families exist, preregister exact corpus subsets, model
   parameters, generation seeds, source-weighting and computational limits before
   scoring. Use a fixed model and show per-work outcomes, not only a pooled mean.
4. Compare both natural event budgets and equal event budgets. Preserve sequence
   boundaries; do not concatenate works into invented musical transitions.
   State whether deterministic prefixes, whole phrases or sampling are used and
   their biases. Event count, family count and musical composition remain separate
   explanatory variables, not interchangeable definitions of “more data.”
5. Show the work/event/family count, pitch and duration coverage, homogeneity and
   known contributor/edition confounds for every subset. No inferred genre label
   becomes factual metadata. Weighting changes prior/context strength unless
   explicitly controlled; disclose this rather than treating it as a neutral fix.
6. Report prediction, generation failure, similarity flags and listening results
   separately. Use all prespecified seeds; retain failures. If choosing private
   listening examples, fix the selection and blind the presentation, not the
   provenance record. Lack of listener feedback is missing evidence, not approval.

At present a larger independent evaluation is blocked by insufficient admitted,
unobserved families. Do not pad the corpus with related editions, source fragments,
transpositions, excluded works or uncertain-rights data to achieve a target count.

## Synthetic false-alarm / miss study boundaries

“False alarm” can mean a gate flag on an independently constructed pair and
“miss” can mean no flag on a known mechanical derivative, within the saved fixture
construction only. Publish denominators and strata. A deterministic scale collision
is informative but is not a population false-positive rate, a listener response or
a legal error. Reused examples are development cases, not newly held-out cases.
The current eight-onset / 0.80 gate and all blocked source decisions stay intact.
