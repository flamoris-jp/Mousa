# Degree-relative progression corpus pilot

This is a **fresh, small weak-label experiment**, not a production harmony model
and not evidence that the model understands human harmonic function or musical
quality. It does not modify Maidionis Core, existing checkpoints, or the harmony
foundation in main.

## What is learned

A separately initialized Maidionis encoder predicts the next bar's chord label
from preceding accepted bar labels. The original eight-bar task was retained as
a blocked pilot; a separately identified two-bar local-transition task is used
only if its frozen sample-size gate passes. The fourteen classes are
`root_degree + 7 * seventh_flag`; roots are zero-based within the major orientation
of a score's key signature. This is not reliable major/minor mode recognition,
local-key analysis, modulation analysis, or functional Roman-numeral annotation.
The original task identity is `mousa.major-progression.weak-label.experimental.v1`;
the local task is `mousa.major-progression-local2.weak-label.experimental.v1`.

The score-derived labels are newly calculated deterministic **weak labels**.
Existing automatic RomanText annotations are not read or reused. Neither melody
nor rhythm is learned in this pilot. Audition melodies are the same original
fixed arpeggio rule in each condition; only the chord sequence is model-generated.

## Rights and provenance

OpenScore/Lieder's score encodings are CC0. The pilot additionally requires a
reviewed historical underlying score edition and the exact `OpenScore (CC0)`
marker in each encoded file. Unknown editions, missing files, unsupported scores,
and uncertain annotation licenses remain excluded. Lyrics are not used or
exported. Source bytes, weights and media remain outside Git.

- [OpenScore Lieder](https://github.com/OpenScore/Lieder)
- [Encoding license](https://github.com/OpenScore/Lieder/blob/main/LICENSE.txt)
- [Attribution and source documentation](https://github.com/OpenScore/Lieder/blob/main/README.md)

CC0 on one representation is not a substitute for checking the underlying
composition/edition. Human annotation datasets with NC, SA, GPL or uncertain
rights chains were not silently absorbed into this experiment.

## Frozen limits

A protocol is saved before extraction; `prepare.py` saves the family split before
extracting labels. Family assignment is
fixed before learning: related compositions/arrangements and exact duplicates
cannot cross the fresh run's train/test boundary. The test set is not claimed to
have been historically unseen by all earlier researchers or models.

`extract_weak.py` accepts a conservative MuseScore 3 subset with explicit,
constant key and meter. Uncertain timing, repeat boundaries, low-coverage or
ambiguous chords produce a null bar that breaks context. Rejected bars are not
silently removed to join distant passages. The narrow scope biases this pilot
toward simpler diatonic passages, and excludes much of the collected material.

Training uses a new seed-314 model, 60 steps × 32 examples, CPU only with a fixed
90-second CPU ceiling. There is no model selection, seed search, or test-directed
threshold tuning. `evaluate.py` compares the initial/fitted model with Laplace-1
unigram and trigram models, including count baselines using the exact 1,920 sampled
training indices as well as explicitly labeled full-training-data baselines.
Weak-label prediction accuracy is not an expert chord-annotation accuracy score.
Family-macro metrics accompany row-weighted metrics; the small held-out family
count limits conclusions.

## Reproduction

The CMake target links an external pinned Maidionis checkout; it does not vendor
Core. Read `CMakeLists.txt` for required dependency selectors. The scripts use
explicit input/output paths; they do not download datasets or run external
services on model authority. `validate` checks training data without fitting.
Run the standard repository test command, plus `native_negative.py` against the
built executable. Generated MIDI is passed through Cantabile for import,
validation, export and rendering before private audition delivery. Exact MIDI
message equivalence is distinct from byte-identical MIDI serialization.

No merge, deployment, GPU execution, commercial-license clearance, human
preference study, or release readiness is claimed.
