# Cycle 10: preserve changing meter; measure candidate-selection tradeoffs

## Exact meter profile

A separate `variable_meter_midi` profile stores each original time-signature
change with tick, numerator, denominator and metronome fields. It supports
2/2,3/2 and changes between supported meters, including declarations beyond the
selected melody's EOT but within the original global timeline. Notes, modeled
performance controls and their same-tick channel order retain exact ticks.

The frozen reader/model are unchanged. Internally, the new reader reuses the
old channel validator with temporary4/4 metadata only; this is not a converted
research corpus. Original bytes and all ticks remain unchanged, and actual
meters are restored in the returned object and exported file. Six synthetic
tests verify full modeled-state roundtrip, constant/new meters, conflicts,
missing initial meter, bounds and old-reader rejection. Identical same-tick
meter duplicates collapse; arbitrary metadata/accompaniment are not retained.
The absolute timeline remains bounded to1024 quarters. This profile is NOT a
new input contract for the fixed-meter statistical models.

## Rights success does not mean technical admission

Brahms580 has newly corroborated rights: a scanned University Society1904
edition's printed page369 matches the title, composer, opus, F-major vocal
opening and actual3/2 transition. Daniel Johnson's exact source dedicates the
typesetting to PD and the work page directly links the reviewed MIDI. This is
a different composer/contributor from fitted sources. Only the incipit and
edition credit were visually collated, not every note; no lyric use or universal
legal guarantee. Evidence URLs/digests are in the rights ledger.

However, the variable-meter reader exposes a second obstacle: all three note
tracks contain overlaps. Vocal track1 starts note64 at19200, note65 at19534,
and note62 at19584; their note-offs occur19655,19630 and19776 respectively.
These are real overlapping source events, not simply same-tick off/on order.
We do not truncate, delete or quantize them to force monophonic admission.
Bach645's newly supported-meter third movement also rejects all three note
tracks for overlap. Both technical probes record source hashes and unchanged
originals. No newly independent work was fitted or model-scored this cycle.

Next investigate bounded overlapping-note preservation separately; this may
retain ornamental performance events without pretending they are a simple
monophonic duration sequence. Source intent still requires notation review.

## Generation-only comparison

Before running, fixed20 groups of4 candidate seeds and the selection rule:
choose the lowest fraction of adjacent onset intervals above an octave; ties
choose the earliest candidate. Compare against the first successful candidate.
Use only the unchanged four-source frozen training configuration, eight6/8bars,
rest cap12, and existing source-copy guard. Silence/single-note candidates are
ineligible, not artificially perfect smoothness winners.

All80 candidates completed, passed exact MIDI roundtrip and had zero guarded
eight-onset source matches. Twenty groups, no missing groups or failures.
Repeated experiment reports and MIDI hashes match.

| Equal-group average | First candidate | Selected of4 |
|---|---:|---:|
| Above-octave interval fraction |0.036151|0.002986|
| Absolute interval, semitones |3.198418|2.511870|
| Distinct pitches |14.20|12.95|
| Onsets |31.10|31.30|
| Rest sixteenths |6.05|4.25|
| Repeated-pitch interval fraction |0.222049|0.247754|

Objective reduction is expected by construction, not independent evidence of
musical improvement. Variety decreases and repeated pitches increase. The
metric crosses rests and does not recognize new phrase beginnings. Candidate
selection consumes up to4x generation budget; no speed advantage is claimed.
This suggests a human-listening hypothesis, not adoption of a universal quality
score. No human ratings, new audio release or perceptual originality clearance.

## Verification

Full suite154 discovered:153 passed, one existing actual AudioAnalyzer integration
skip. Three new feature tests plus six meter-profile tests. Independent review
recomputed all selected seeds and aggregates and checked frozen hashes; it did
not independently regenerate the80 files. Our full repeat run did regenerate
them and matched. Compileall/whitespace checks pass. Main and live Cantabile
projects remain untouched.

Reproduce generation with `tools/compare_candidate_smoothness.py --corpus CORPUS
--output NEW_DIRECTORY`; the fixed existing manifest is hash-checked. Read-only
technical probes use `tools/probe_variable_meter_intake.py --source MIDI --sha256
EXPECTED --output NEW_DIRECTORY`. Raw MIDI and scans remain outside Git; only
code, evidence references, plans and results are committed.
