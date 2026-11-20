# Cycle 9: unknown exact durations and a fair outcome space

## Hypothesis and scope

An unseen duration need not be an unknown token. A fixed, explicitly bounded
MIDI-tick outcome space can give every representable positive duration nonzero
mass without rounding ornaments. Rational quarter-duration and integer-tick
labels should give identical results when they encode the same outcomes.

The comparison plan was written before this synthetic experiment. No music
corpus was accessed by the experiment, no existing frozen model was modified,
and no work was relabeled as unobserved. Schubert1578/1558 and Foster370 remain
observed diagnostics. Schubert1585/1587 are unscored but not independent of the
Schubert contributor/composer family already inspected.

## Implemented contract

`DurationSupport` has a fixed default support of 1..12288 ticks at PPQ384,
i.e. up to32 quarter notes per event. Training counts remain sparse; the prior
has total mass1 uniformly across the fixed support, not across denominators.
Probability arithmetic uses exact fractions. Unseen representable durations
receive positive prior probability. Incompatible denominators and durations
beyond the bound are explicit errors, not rounded notes or a substituted UNK.

Generation samples the exact conditional distribution over durations fitting
the remaining length and an optional duration cap. It never clips a sampled
event. This conditional distribution is not the unconditional likelihood used
for the probe; target-dependent masks must not be sneaked into comparisons.
The helper is a duration-only counting model, not a melody generator or a
learned account of ornaments, meter or phrase structure.

## Synthetic results

Seven artificial training observations; eight probes. Six probes are inside
the declared support, including unseen1-tick and22-tick durations. A1/7-quarter
probe is incompatible;33 quarters exceeds the bound. Only three probes fit
both a sixteenth grid and the same duration bound. We do not silently discard
the remaining probes and compare conditional coarse NLL against full NLL.

- Sum of all12288 exact probabilities is1.
- Rational-label and independent integer-label probability calculations match.
- Twenty seeds generate exactly9216 ticks (eight6/8 bars), with each duration
  at most768 ticks. Event counts39..54; all samples terminate within4096 events.
- Independent integer-label sampling gives identical seeded sequences.
- Two full experiment runs produce byte-identical reports.

This proves representation equivalence and the implementation contract on
these fixtures, not musical quality or practical superiority. The uniform tick
prior can produce unnatural timings. No new music or audition recording is
being delivered as a result of this duration-only test.

## Validation and reproducibility

Run `PYTHONPATH=src python tools/compare_duration_support.py --output NEW/report.json`.
The result records code/plan hashes and a sample-sequence digest. Six new unit
tests cover full-support normalization, unseen/OOV distinction, empty-training
prior, deterministic constrained generation, exhaustive tiny-support draw
weights and invalid inputs. Full suite145 discovered,144 passed, one existing
actual AudioAnalyzer integration skip. Compileall and whitespace checks pass.

Before a future musical comparison: freeze the same outcome space, prior,
source-family splits, target task and constraints; count unsupported outcomes
separately; fit on training data only. Any PPQ change changes the discrete
outcome space and its prior, so likelihood is not directly comparable merely
because both representations use fractions. Human preference remains separate.

## Independent source search: no newly admitted work

Five candidates were checked without fitting or model scoring. Bach1534 remains
pending: typesetter attribution does not resolve the new adaptation's author.
Bach645 source archive retrieval succeeded and its autograph/PD dedication was
verified, but available melodic tracks fail the current overlap/meter profile.
Mozart252 (Deborah Lowrey) has a technically usable225-note6/8 Pamina part, but
its source header warns about a consulted Dover/Peters edition's Germany/West
Berlin restrictions. Do not infer unrestricted training permission from the PD
label; keep pending. Mozart260 has the same concern and unsupported meter.
Brahms580 (Daniel Johnson, historical1904 edition) has alternating2/2 and3/2,
which the current profile rejects. No meter rewrite or note deletion was used
to force admission. Evidence URLs and selected hashes are in the cycle9 ledger.

This is a negative intake result, not a completed independent benchmark.
Extending exact variable-meter handling may be more useful than repeatedly
searching only for files compatible with a narrow reader, but should be a
separate, tested change preserving the original meter map and event timing.
