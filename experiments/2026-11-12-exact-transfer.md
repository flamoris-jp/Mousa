# Cycle 7: preserve the performance, score only the declared projection

## Outcome and frozen boundary

Admitted two previously unscored Schubert works for **test-only** prediction:
Trost in Thränen D120 (Mutopia1578) and Der Musensohn D764 (1558). They are one
correlated composer/edition/typesetter family, not two independent domains.
Neither enters fitting. The cycle6 selected model, controls and training IDs
were frozen before these scores; the evaluation driver verifies all frozen
model/config hashes. No parameter changes or new model selection after scoring.
The works are now observed and must not be described as fresh again.

Separate composition, arrangement and MIDI-encoding evidence, original hashes,
acquisition dates, contributor/edition and restrictions are in
`datasets/research-frozen-schubert-transfer-20261112.json`. Schubert died1828;
exact sources identify the historical Breitkopf&Härtel1884–1897 edition, no
separate modern arranger, and Ph.Raynaud's explicit PD contribution dedication.
This is legacy PD, not CC0, and contributor edition provenance is not a
note-for-note independent collation. Local selected-melody research only; no
external corpus distribution or generated-work clearance. Lyrics are unused.

## Separate exact-tick intake, not a weakened old reader

`meter_midi.py` and the frozen model remain unchanged. New `tick_midi.py`
preserves integer-tick selected notes, velocities, tempo map, CC7 volume map,
program changes, same-tick modeled channel-event ordering, selected-track EOT,
and full-source end separately. No quantization, cropping, tempo flattening or
automatic transposition. Original file hashes verified unchanged.

The new path is deliberately separate and narrower than an editable MIDI
project: arbitrary metadata/lyrics/accompaniment and cross-track metadata order
are not exported by it; equivalent note-on-zero becomes note-off; redundant
same-tick equal tempo declarations may be normalized. Cantabile remains full
project authority. Other controls, sustain/pitch-bend, conflicting same-tick
state values, overlapping notes and inconsistent stored event/model state reject.

Two initial attempts stopped **before any model scores**: first because the
candidate used non-initial program changes, then because volume changed after a
note-on at the same tick. Rather than delete or reorder these source events,
the new profile was extended and tested with a retained channel-event stream.
Its validator replays that stream against notes/maps. The final run independently
compares original and export channel-event signatures, including ordering.
No aborted attempt is claimed as a successful benchmark.

Program defaults are explicit bookkeeping: an absent initial program is GM0,
recorded as implicit and not newly written to the export. A source tempo change
after the selected melody ends also must not extend that melody's EOT.
For1558, selected EOT127104 versus source EOT134016 ticks are both retained.
All eight original/current reference files round-trip modeled fields and pass
independent channel-order comparison; all old training tokens match the old
reader exactly, preventing an unnoticed change to the fixed comparison.

### Declared projection and phrase alignment

Only after exact intake, project to sixteenth pitch/rest/HOLD tokens **if every
note boundary and selected EOT is exactly representable**. Tempo, volume,
program and velocity are deliberately excluded from this existing pitch/rhythm
model, but remain in the original and tick representation. Thus token prediction
is not performance/timbre modeling and not lossless MIDI conversion.

Record transposition explicitly:1578 -5 semitones,1558 -6, no clipping. Score
source alignment also includes MIDI-only initial silence:1578 has10 silent steps
then a2-step pickup (first downbeat12);1558 has12 initial silent steps, then a
delayed entry at82 before downbeat84. Both source timeline origins are0 modulo12.
No leading rests are removed. Exact note counts170/289, token lengths552/1324,
scored event counts180/304. No off-grid boundary in either selected melody.

## Independent source screens before scoring

Keep existing normalized full-grid equality and exact transposed eight-onset
interval/duration/gap checks. Added a bounded approximate screen: normalized
Levenshtein similarity of the whole onset pitch-interval sequence, ignoring
rhythm to flag rhythmic rewrites. Fixed rejection/review threshold0.90 with
at least16 intervals; reject >512 onsets rather than silently skipping. Threshold
and code hash are recorded before scoring. Four synthetic tests cover transposed
rhythmic rewrites, a changed note, insertion/deletion symmetry and bounds.

All28 pairs across the eight sources: no exact eight-onset overlap; maximum
whole-interval edit similarity0.377778. This narrow whole-sequence screen can
miss local borrowing and perceptual resemblance; passing is not legal or musical
originality clearance. Related Schubert works stay in the same heldout family.

## Frozen transfer results (not attraction ratings)

| Model | D120 NLL/event (180) | D764 NLL/event (304) | Equal-work family mean |
|---|---:|---:|---:|
| selected: bar context, count shrinkage k1 | 4.612684 | 4.662211 | 4.637447 |
| same bar context, k0 | 4.705615 | 4.819722 | 4.762668 |
| melodic control, no position | 5.248168 | 5.498934 | 5.373551 |

The selected model has lower NLL on both works, but **lower exact joint top-one
counts than k0**:31/180 vs33/180,36/304 vs43/304. Duration top-one is also lower:
selected102/180 vs k0 114/180, and149/304 vs180/304. Do not suppress this tradeoff or
claim every predictive metric improved. No confidence interval, population
claim or musical appeal conclusion from one family. No human listening labels.
Repeat run yields the entire same report. Full results retain all denominators.

## Measure hypothetical quantization damage; do not apply it

The tick reader can preserve three off-grid melodies exactly. They remain
excluded from the frozen grid model. Diagnostic nearest-sixteenth rounding
(ties upward), onset/end/EOT occurrences counted separately, PPQ384:

| Work | Off-grid boundaries / all | Max tick error | Mean tick error | Notes collapsed to zero |
|---|---:|---:|---:|---:|
|1040|5/99|44|134/99|2|
|1585|6/201|22|30/67|2|
|1587|18/217|22|270/217|6|

All require384 steps per quarter to represent all those note boundaries exactly,
versus4 for the existing sixteenth model. This is representability, not a
recommended model vocabulary. Mean error alone hides complete loss of short
notes. No rounded corpus was emitted, fitted or scored. Only diagnostic numbers
and exact original-preserving selected exports were produced; musical semantics
of ornaments still need separate design. See grid-loss diagnostics JSON.

## Native Cantabile and tests

Pinned Cantabile CLI from cycle5 imported and exported both complete original
new MIDIs **byte-identically**, and the new tick reader independently agrees
before/after. No audio rendering or live-project mutation for these sources.
Originals, extracted MIDI and projects remain outside Git.

Full suite130 discovered:129 passed, one existing actual AudioAnalyzer integration
skip. New tick tests13, approximate screen tests4; compileall/diff checks pass.
Frozen old-reader/model hashes match, repeated reports match, no source file
changes. No GPU, paid operation, deployment, main merge or media publication.

## Next

Preserve this frozen result rather than retuning on it. Grow another independent
contributor/composer cohort, or compare an exact rational-duration model on a
new plan instead of rounding away ornaments. Human form preference remains a
separate pending outcome; lower transfer NLL does not settle whether the
handcrafted A–A′–B–A″ comparator sounds better.

Reproduce `tools/evaluate_frozen_transfer.py` with reviewed local `--corpus`,
`--manifest datasets/research-frozen-schubert-transfer-20261112.json`,
`--origins datasets/research-metrical-origins-20261112.json`,
`--freeze experiments/2026-11-12-frozen-transfer-plan.json`, fresh `--output`.
