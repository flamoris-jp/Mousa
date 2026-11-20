# Event-centered statistical baseline diagnostic — 2026-11-12

## Hypothesis and scope
Removing HOLD from the prediction target exposes event-level weaknesses hidden
by grid continuation accuracy. Compare unigram (order 0), Markov (order 1), and
2-gram (order 2), alpha=0.5, seeds 7/17/29, 128 grid steps (8 bars). The full
pitch-token/duration pair, including rest events, is predicted. This is NOT the
same denominator/task as PR #6's grid-token metric.

The three sources and split roles are the already-inspected Trial 001 diagnostic,
not a new sealed test. Training uses only the training work. The code is a small
music-specific statistical baseline; no Maidionis numerical Core is copied.
No trained neural model, human quality improvement or original-work clearance
is claimed.

## Rights review completed before fitting
After the initial quarantine audit, the publisher's individual Public Domain
statements were checked together with https://www.mutopiaproject.org/legal.html
which explicitly says contributors dedicate their contribution into the public
domain. The exact pages link the MIDI as the LilyPond-generated contribution.
Composition/source edition, contributor encoding and arrangement grounds are
recorded separately in the source audit, with source/page/legal-page hashes.
This admits only these exact files for local diagnostic analysis/training;
it is not a new corpus, redistribution approval or legal warranty. Fetched files
match the previously reviewed PR #6 SHA-256 values. Source bytes remain outside Git.

## Actual measurements

| Order | Train correct / events | Dev correct / events | Test correct / events | Test NLL / event |
|---|---:|---:|---:|---:|
| 0 | 20 / 174 | 0 / 36 | 0 / 52 | 4.763808 |
| 1 | 123 / 174 | 0 / 36 | 1 / 52 | 4.500262 |
| 2 | 157 / 174 | 0 / 36 | 1 / 52 | 4.493403 |

26/36 dev and 31/52 test pitch-duration combinations are absent from the train
vocabulary. NLL reserves one explicit unknown category; the vocabulary is not
expanded with test answers. Generation excludes this undecodable category.
The diagnostic shows overfitting and a sparse event vocabulary, not a winner in
musical appeal. Higher order nearly memorizes the training sequence without
improving exact dev accuracy.

Nine 8-bar MIDI candidates were actually generated and individually re-read
with the pinned PR #6 frontend; the reread exposed a loss documented below. Two same-configuration
runs yielded identical candidate hashes and predictive metrics. Per-model time
was below 0.1 seconds in these small CPU runs, peak process RSS below 20 MiB.
The machine-readable report preserves exact values and source digests.

## Failure: reproduction risk
Order 1/seed 7 and order 2/seed 7 each share a contiguous 70/128 grid-step run with
the training melody. This raises a copying warning. A grid substring includes
HOLD/rest and is not a full perceptual or legal originality test. All nine
candidates remain quarantined from original-work presentation until fuller
similarity and human review. Do not cherry-pick the unflagged candidates as
proven original. No listening test or Cantabile mutation was performed.

## Failure: end-of-track silence lost on re-import

Order 0/seed 17 writes an eight-bar file including end-of-track silence, but the
pinned reader returns only 112 grid steps (seven bars) because it rounds the last
note end rather than preserving the MIDI end-of-track time. Four other re-imports
shift pitches by -5 semitones because the reader normalizes the lowest pitch.
The report records every returned length and transposition. No exact lossless
roundtrip is claimed, and this is not a Cantabile bug. Preserve trailing silence
and make normalization an explicit semantic decision before transfer comparisons.

## Next hypotheses
1. Predict relative pitch and duration separately to reduce unseen combinations;
   compare with the same event task and retain the existing diagnostic as a
   known set. A new untouched work-family test set is still needed.
2. Block long exact/transposed source phrases while decoding, then measure how
   the safeguard changes validity, diversity and structure rather than merely
   deleting inconvenient outputs afterward.
3. Test whether large HOLD/rest blocks inflate similarity warnings, using
   onset/interval and rhythm-aware diagnostics alongside raw-grid matching.

## Reproduce

From the research branch, with PR #6 and its requirements installed in a separate
checkout, after confirming source rights and preparing its exact corpus:

```sh
PYTHONPATH=src python tools/compare_event_baselines.py \
  --trial-root /chosen/trial-checkout \
  --corpus /chosen/trial-corpus \
  --manifest datasets/research-source-audit-20261112.json \
  --output /chosen/new-output-directory
```

Output includes preregistration, all measurements and nine local MIDI files.
No MIDI, weights or audio files are committed. Output paths above are illustrative,
not server locations or service defaults. Tests for new event conversion,
context boundaries, determinism and exact matching accompany the implementation.

## Subsequent correction
The [second research cycle](2026-11-12-factorization.md) established that the
70-step warning consisted of 68 REST and 2 HOLD tokens, with zero note onsets.
It is not evidence of a copied melody. Keep the raw measurement, but use the
corrected interpretation and new onset-aware diagnostic rather than presenting
this warning as proven plagiarism.
