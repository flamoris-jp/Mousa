# Results — original Billboard annotation pilot

## Intake and frozen data preparation

The original source explicitly releases its annotations under CC0. This is not
an assertion that the original recordings or compositions are public-domain.
The selected complete-annotation and LAB archives are 219,100 and 1,037,052
compressed bytes respectively. They contain 890 slots; no audio was downloaded.

Exact source-content grouping gives 740 groups. Combining index/header title and
artist aliases gives 739; conservative title-only unions give 729. The family
split was fixed before tokenization: 583 train and 146 test groups. Each group
uses its lowest numeric slot ID and no fallback representative. Current-run
cross-split leakage is checked by this grouping; unknown alternate-title covers
remain a limitation. Normalized title comparison against 29 earlier OpenScore
test records found no exact match, not proof of historical or semantic novelty.

After rejection/barrier rules and a maximum of 16 hash-selected windows per
family, the dataset has **8,616 train windows / 559 active families** and
**2,213 test windows / 143 active families**. Slot 974 is rejected in full for
invalid timing. Other nonpositive-event occurrences are in slots not selected
as family representatives. Unknown/unsupported/uncertain spans remain barriers,
not silently deleted to join unrelated passages.

One pre-fit parser hardening rejected mixed accidental spellings and enforced
protocol/implementation consistency. No mixed accidental occurred in the source.
The old and revised preparation outputs retained identical dataset, split,
counts, exclusions and all 728 per-slot event files (732 files in total).
A full replay checked all 10,829 windows and 75,381 coalesced events against the
original LAB lines. No prediction scores were observed during preparation.

## Single fit and controls

One fresh seed-314 fit ran 60 × 32 draws in 5.101712 CPU seconds, one thread.
Actual exposure: 1,920 draws, 1,737 unique windows and 539 source families, including 747 distinct
three-chord patterns and 50 distinct target classes.
This is less than the available training population; it must not be described as
training on every one of the 8,616 windows. No second fit or seed search occurred.
Parameters changed, and the native process verified saved/reloaded logits exactly.

| Model | Accuracy, 2,213 rows | NLL (lower is better) | Family-macro accuracy | Family-macro NLL |
| --- | ---: | ---: | ---: | ---: |
| exposure_matched_trigram | 35.47% | 3.4130 | 34.84% | 3.4373 |
| exposure_matched_unigram | 22.64% | 2.9530 | 22.30% | 2.9647 |
| full_train_trigram | 38.05% | 2.9314 | 37.63% | 2.9643 |
| full_train_unigram | 22.64% | 2.9383 | 22.30% | 2.9508 |
| initial_ai | 0.00% | 4.9450 | 0.00% | 4.9335 |
| trained_ai | 30.68% | 2.5651 | 30.33% | 2.5815 |

**The result is mixed, not an across-the-board AI win.** The model assigns better
average likelihood to held-out target chords than these fixed count baselines,
but its top-1 accuracy is below both trigram controls. The count baselines use
fixed Laplace-1 smoothing; they are not a tuned state-of-the-art competitor.
Overlapping windows are correlated, and one seed/budget is not a broad model
comparison. Human-annotation prediction is still not musical quality or proof
that the original analyst's interpretation is uniquely correct.

The earlier OpenScore pilot used weak labels, major-oriented 14 classes and
bar-based contexts. The current 96-class event-based task has different
repertoire, targets and sample selection. Percentages cannot be compared as
though they were the same benchmark. No melody, rhythm, voicing or human
preference was evaluated. No new listening samples were generated for this
source/learning investigation.

## Outstanding limits

- Unknown alternate titles, translations and composition identities can defeat
  simple title-based grouping; same-title unions may also over-group works.
- Interpolated LAB timing is preserved for auditing, not learned or presented as
  hand-aligned timing of every event.
- Inversion bass is preserved in provenance but omitted from the 96-class target;
  unsupported extensions are barriers, narrowing the repertoire represented.
- The original annotation ecosystem includes subjective and simplified analyses.
- Future optimization should use a separate selection set, rather than choosing
  additional training runs against this already observed test result.

No existing checkpoint or earlier experiment was changed. No GPU, Files,
merge, deployment, raw-dataset publication or underlying-song license clearance
is claimed.

## Verification

The Python suite ran 144 tests with one optional external stem-exporter
integration skipped. Native no-fit contract tests passed all 25 cases.
Independent audit reproduced all 1,920 sampling indices, checked all prepared
source windows and 728 source pairs, verified checkpoint/data digests and
53 parameter tensors / 106 Adam moments at step 60, and independently
reconstructed the embedding update. It recomputed 82,278 evaluation checks.
Saved/reloaded-logit equality is the native process assertion, not a new
independent forward pass. No audit retrained or generated music.
