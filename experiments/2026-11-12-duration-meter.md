# Third cycle: duration priors, relative pitch and exact 6/8 transfer

## Controlled ablations on the known diagnostic
Compare six variants: absolute/relative pitch contexts × uniform/empirical/typed
duration priors. Order 1, total prior mass 1, seeds 7/17/29, the same fixed
3,328-event support. Empirical priors come only from the training work, with a
small uniform floor; typed conditions durations on note versus rest. Relative
encoding tracks intervals across rests, starting at the fixed register center.
No source or outcome selects a different vocabulary. Marginal pitch and duration
accuracy are explicitly distinguished from joint-event accuracy.

For absolute pitch, replacing uniform with empirical duration prior changes
candidate onset counts from **10/9/14 to 37/31/32** at the same seeds. The earlier
uniform prior allocated mass to extremely long durations absent from the melody.
This addresses sparse generations, but more notes do not imply better music.
Typed priors are not automatically better: one seed creates 66–70 rest steps.
Retain those failed variants rather than presenting only their best seeds.

Known test (52 events): absolute-empirical pitch 4, duration 29, joint 3 correct;
relative-empirical pitch 6, duration 9, joint 3. Relative-empirical NLL is lower
(6.451611 versus 7.376935) but trades off exact duration prediction. Selection of
relative-empirical for the next probe is based on prior dev NLL (6.434973, lowest
of the six), not on new test results. The first two cycles used a padded grid
reader; this ablation keeps that reader unchanged for controlled comparison.

## Explicit 4/4 and 6/8 I/O
New `meter_midi.py` retains selected-track note start/end, absolute pitch,
velocity/release velocity, explicit constant meter, tempo, PPQ, channel/program
and exact end-of-track time. Sixteenth-grid events must already be exact; no
quantization or meter conversion. 6/8 has 12 grid steps/bar, 4/4 has 16. Partial
bars are not silently padded. This reveals a second old preprocessing issue:
the historical reader padded source 376 from 652 to 656 steps and source 2245
from 248 to 256. Metrics across those projections are not interchangeable.

This is a strict research melody extraction profile, not lossless general MIDI
or a Cantabile substitute. It rejects polyphony, changing/missing meter,
changing tempo, unsupported controllers/pitch bend/pressure, SysEx, ambiguous
note pairing and other-track interference on the selected MIDI channel. Lyrics,
key signatures and descriptive metadata are not preserved by export. Tempo is
microseconds per quarter even in 6/8, not automatically dotted-quarter BPM.

The three new files round-trip exactly as MeterMelody without changing meter:
- Mutopia 888: 38 onsets, 120 steps, 6/8, 10 bars.
- Mutopia 889: 47 onsets, 120 steps, 6/8, 10 bars.
- Mutopia 789: 120 onsets, 394 steps, 6/8, 197/6 bars; partial bar preserved.

## New-work transfer probe, no training on the new works
Per-work historical composition/arrangement, typesetter dedication and linked
MIDI evidence are recorded in `research-transfer-probe-20261112.json`. All exact
hashes were checked. No full normalized melody or eight-note interval/rhythm
phrase matched across the six source works. This is limited duplicate screening,
not proof of no perceptual similarity. The two English County Songs sources are
correlated and remain together in test. New sources were never fitted or used to
choose the compared models; after this observation they are no longer untouched.

Compare the frozen selected relative-empirical model with absolute-uniform and
absolute-empirical controls, all trained on the same original work. Exact meter
reader normalization is explicit and identical across models. New-work results:

| Work | Absolute-empirical pitch | Relative-empirical pitch | Absolute NLL | Relative NLL |
|---|---:|---:|---:|---:|
| Oats and Beans (38 events) | 2/38 | 8/38 | 7.287775 | 5.917338 |
| The Water of Tyne (48 events) | 3/48 | 9/48 | 7.537501 | 5.697682 |
| Sing Ivy (130 events) | 37/130 | 33/130 | 5.681484 | 5.851173 |

Relative pitch helps two new works and hurts one. Do not describe it as a
universal improvement or infer artistic preference. The event model has no
bar-position/meter features: meter-correct I/O is not learned 6/8 phrasing.

Nine 6/8, eight-bar MIDI candidates were generated (96 steps) and all exactly
round-tripped. All metrics and candidate hashes reproduced in a fresh run.
Absolute-empirical produces 27/23/27 onsets versus uniform 10/9/4. Relative-
empirical produces 31/10/29; variance and the sparse middle seed remain issues.
No candidate has been human-rated or declared original. The prior eight-note
copy safeguard remains narrow and does not replace a musical similarity review.

## Private listening preparation
Two neutral sine previews were generated from the same 6/8 seed 7 comparison,
with identical renderer and tempo (quarter=120), approximately 12 seconds each:
A absolute-empirical, B relative-empirical. These are research previews, not
Cantabile rendering or a listening assessment. No live Cantabile project changed.
WAV SHA-256:
- A: 6218f45f2c5287f10d3175a4a4db71308c642ed081b07d1ddc255e1035672b05
- B: 14e3932315d7d7ddbd223f3cd4bbc3bdb50f33886072c459c33203b1a1b4a533
Media stays outside Git. Ask A/B/tie/neither and a reason if listening feedback
is useful; lack of feedback is not a label and does not halt other research.

## Verification and next hypotheses
- 90 tests discovered with mido: 89 passed, existing actual AudioAnalyzer
  integration skipped because its external environment is not configured.
- New meter module has 21 focused tests, including empty-track boundaries.
- Exact source MIDI extraction/export/reimport passed on all three new files.
- Both ablation and transfer experiments repeated identically for metrics/MIDI.
- No GPU, paid operation, merge, deployment or public media/weights release.

Next: test phrase/metrical position features without conflating meter-aware
rendering with learning; use several distinct training families to reduce
single-work bias; calibrate a duration prior that limits pathological long rests
without removing intentional phrasing. Keep a genuinely new work-family set for
later testing instead of repeatedly calling these now-observed examples sealed.

Reproduce `tools/compare_melodic_ablations.py` with the same four arguments as the
second cycle. For exact-meter transfer use `tools/probe_meter_transfer.py` with
`--corpus`, `--manifest datasets/research-transfer-probe-20261112.json`, and a new
`--output` directory. All source bytes must be acquired and hash-checked separately.
