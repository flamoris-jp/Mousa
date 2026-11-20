# Cycle 5: score-linked pickup phase, shrinkage and native Cantabile

## Hypotheses and evaluation scope

A within-bar model may be learning the wrong phase if MIDI tick zero is a
pickup. Sparse position counts may also overfit; cautiously shrink them toward
the existing melodic count model. This is an exploratory diagnostic on the
same six previously observed pieces, not a fresh test or musical quality score.

### Correctness before optimization

Reviewed the linked LilyPond sources for all six pieces, recording URLs, source
hashes and opening durations in `datasets/research-metrical-origins-20261112.json`.
Water of Tyne (889) explicitly declares `\partial 8`, beginning with an eighth
rest. Its 6/8 MIDI starts at phase **10 of 12 sixteenth steps**; the first full
bar begins at MIDI step 2. The first audible melody note is at MIDI step 24,
which is again phase 10, not the downbeat. Initial pickup2 + full rest12 +
rests4+2+4 exactly explain that step24 onset. Treating the first sounding note
as bar zero would be wrong. The other five source openings have no partial and
full opening durations; their reviewed origin is zero, including delayed entries.

Added explicit per-song `origin_steps` and matching evaluation/generation input.
No automatic pickup inference, inserted silence, MIDI shifting or quantization.
The reader/writer still preserves exact input timing. Four-bar phrase origin
remains unannotated, so this experiment uses bar position only.

### Count shrinkage, explicitly not a probability mixture

`position_strength=k` uses `w=n/(n+k)` and mixes positional and control **event
counts** as `w*positional + (1-w)*control`, then applies existing factorization
and smoothing. This retains the interface and exact k=0 behavior. Count totals
change, so it is not equivalent to mixing output joint probabilities; it is one
specific heuristic, not a universal Bayesian estimator. Tests check its formula,
normalization and convergence to the smoothed control for very large k.

## Experiment and negative findings

Naive/score origins crossed with k=0,1,4,16,64. All four training pieces remain
in their three conservative source families. Leave one whole family out,
including both English County Songs pieces together, train on the remaining
families, and record the unfitted family NLL. Average works inside each family,
then give the three families equal weight. These observed families are not a
sealed holdout. Folds share fitted data and do not support confidence claims.

| Origin | k | Family-macro NLL/event |
|---|---:|---:|
| naive | 0 | 5.370599 |
| score | 0 | 5.311026 |
| naive | 1 | 5.163409 |
| score | 1 | 5.133228 |
| score | 4 | 5.163514 |
| score | 16 | 5.210067 |
| score | 64 | 5.261438 |

The best **exploratory** setting here is score/k1. Fit-to-training NLL worsens
from score/k0 1.3294 to score/k1 1.6711 while family-fold NLL improves, consistent
with reduced overfitting in this small diagnostic, not proof of generalization.
The known 2247 dev score worsens 4.7598→5.0527 while known2245 improves
5.5617→5.4618. Score alignment also worsens the Sing Ivy held-family fold at
k0 (4.7951→4.8678); physical correctness is not selected based on favorable NLL.
The held376 4/4 fold remains6.5265 for every setting because all its training
sources are6/8, so the absent meter contexts correctly fall back to control.

Thirty 6/8 eight-bar candidates, three seeds for each condition, explicit rest
cap12 and the existing eight-onset transposed phrase guard against all six known
references. 30/30 complete and round-trip exactly. A repeat run reproduces all
metrics and MIDI hashes (timing excluded). Approximate runtime12 CPU seconds;
no GPU/neural training. No human judgments or originality clearance.

## Cantabile: isolated real engine, not the live project

Read-only connector inspection found an available Cantabile0.1.0 instance and
configured FluidSynth backend, but it contained another existing project. No
import, save, edit, render or project switch was sent to that live workspace.
A later context check confirmed the same document and revision unchanged.
Private project names/content/runtime identifiers are not included in this repo.

Instead built pinned Cantabile source
`420f395f187d46072e86912c51bae5a2527a00f1` in a separate local build directory:
CMake4.0.3, nlohmann_json3.12.0, C++20, Release, single compile worker. Initial
inspection found no CMake or JSON headers, so these two build dependencies were
installed in the existing isolated Python environment. No Cantabile source edit
or installation/deployment to the live service. Native `midi-codec` CTest1/1
passes. The build used the repository's documented CMake path with an explicit
JSON include directory.

Used its actual `cantabile-cli import-midi` and `export-midi` on the previous
private B sample, then `cantabile-render` with the locally installed TimGM6mb
SoundFont,48000Hz,2s tail,max30s. Import/export MIDI SHA-256 is identical to input,
and the independent strict reader confirms all note timing/pitches/velocity,
6/8 meter and trailing length. WAV header independently checked stereoPCM16,
672000frames,14s =12s music+2s tail; render reports zero clipped samples.
Additionally all thirty cycle5 candidate MIDIs passed isolated native import/export,
with byte-identical outputs and independently equal note/event models. Those
thirty were not audio-rendered. Full hashes and render metadata: `2026-11-12-cantabile-verification.json`.

This is real native-engine execution and technical audio rendering, **not**
live-service audition, human listening or Windows GUI verification. TimGM6mb's
installed package identifies GPL-2 and sampled-content provenance; it is used
only for private technical testing here, with no claim of media redistribution
clearance. WAV, project and MIDI remain outside Git. No soundfont is copied.

## Unused sources remain pending

New library evidence supports an early history for Finnish candidate1019/1020:
early1902–1914 recording metadata, a1910s arrangement catalog, and a librarian's
discussion separating the folk tune from later arrangements. Actual old-score
melody comparison is still missing; neither candidate is fitted or model-scored.
The source-linked corroboration ledger distinguishes successful web reads from
raw403 downloads and does not invent downloaded-file hashes. Do not infer
training permission for historical recordings or for other arrangements.

## Verification / next

- Full suite106 discovered:105 passed, one pre-existing actual AudioAnalyzer
  integration skipped because its external environment is absent.
- Position tests16/16, including explicit phase rollover/reset, invalid origins,
  shrinkage formula/control limit, normalization and prior safety checks.
- Repeat experiment, compileall and diff whitespace checks pass.
- No main merge, public media, live project replacement, GPU, paid operation or
  deployment. All findings remain draft research.

Next: obtain a genuinely unobserved and rights-cleared contributor-family set,
freeze a chosen model before scoring it, compare old and contributed melody
incipits, and seek human preference evidence. More tuning on these six sources
must remain exploratory; lower NLL alone is not enough.

Reproduce `tools/compare_origin_shrinkage.py` with `--corpus`,
`--manifest datasets/research-exploratory-multifamily-20261112.json`,
`--origins datasets/research-metrical-origins-20261112.json` and a fresh `--output`.
