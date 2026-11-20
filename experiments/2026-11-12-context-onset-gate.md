# Cycle13: previous sounding gate and pitch-continuity context

## Adaptive experiment, not a new independent benchmark

The preceding overlap failure motivates conditioning the next onset delta on
the previous note's sounding gate. This is adaptive exploration. Training stays
restricted to376/888/889/789; Brahms580 is now a known diagnostic, not fresh or
untouched. Cornelius583 is not fitted, scored or used to select settings.

Use a2x2 factorial comparison: previous-gate timing context off/on and learned
pitch continuity off/on. Common timing support, global gate marginal and prior,
training vocabulary, seeds0..9, target9216ticks, max256notes, max64attempts/note,
max3simultaneous pitches and same-active-pitch rejection are shared. No clipping
or automatic shortfall repair. Failed/copy-blocked candidates remain failures.

Timing context uses a fixed shrinkage strength4, mixing local previous-gate
counts with global delta counts. Context resets per work. Unseen contexts fall
back to the global distribution. This is count shrinkage, not a mixture of
complete probability distributions or learned ornament semantics.

Pitch continuity uses training interval counts restricted to the same absolute
training vocabulary with positive smoothing. The first pitch also changes from
uniform to the training unigram: that is an explicit confound, so do not assign
all effects solely to interval continuity. Both new controls use the same pitch
sampling API; they are distribution-matched but do not reproduce old cycle12
seed bytes because its uniform sampler used a different random-number API.

## Rights and reserved material

Cornelius583's selected vocal part passes exact overlap-reader roundtrip:
80notes, all MIDI71/B4, no overlaps,3/4, first onset1728ticks. Selected EOT36096
and complete source EOT48384 remain distinct, without padding. Earlier
historical-edition and contributor-rights evidence is unchanged. It remains
reserved and grouped with580 by Daniel Johnson/University Society. Its
single-pitch design also warns against treating a distinct-pitch count as a
universal music-quality score.

## Human assessment remains separate

`docs/ONSET_GATE_LISTENING_DESIGN.md` proposes a small private A/B evaluation
with fixed seed IDs, retained technical failures and questions about flow,
overlap, monotony and replay preference. It does not report completed listening
or authorize public media. Overlap-aware rendering is required; the older
monophonic grid renderer must not silently discard simultaneous notes. No new
human ratings are inferred or used as labels.

## Results on the fixed exploratory conditions

Known580 timing NLL/event changes from4.613662 to3.638074 with previous-gate
context. Pitch flags do not change this timing-only likelihood. No parameter
was tuned to this result, and it is not evidence of new-family generalization.

| Timing / pitch context | Complete / attempted | Overlap onset fraction | Mean absolute pitch interval | Distinct pitches | Repeated-pitch fraction |
|---|---:|---:|---:|---:|---:|
| off / off |9/10|0.390455|6.596944|14.888889|0.047290|
| off / on |9/10|0.347019|2.323600|12.777778|0.261228|
| on / off |8/10|0.159433|6.427212|14.000000|0.047738|
| on / on |8/10|0.168377|2.228991|10.625000|0.284152|

These descriptor means use completed outputs only, with unequal successful
sets. Do not hide the six failed attempts: the two timing-off conditions each
fail seed1; the two timing-on conditions each fail seeds0 and3. Total generation
rejections are74,125,151,209 in table order. There are zero copy-guard failures.
The timing intervention reduces overlaps among completed samples but worsens
completion in this small fixed sample. The pitch intervention reduces leaps
while reducing pitch diversity and increasing repeated pitches. It includes a
changed first-pitch prior, not interval continuity alone. Lower overlap is not
a universal goal: real ornaments may overlap legitimately.

All34 completed files independently satisfy target9216ticks, maximum3 active
pitches and no same-pitch overlap, and pass exact modeled MIDI roundtrip. No
live project was touched. The MIDI is still an experimental proposal, not
public-release-cleared or human-rated music.

A reporting-only common-success analysis uses seeds2,4,5,6,7,8,9 across all four
conditions. In table order, overlap fractions are0.362897/0.318588/0.144114/
0.154335; distinct pitches14.5714/12.4286/14.5714/11.1429. Directional tradeoffs
remain, but this is still conditioned on all treatments succeeding and excludes
failures. Do not replace the full attempted denominators with this subset.

## Verification and reporting correction

181 tests discovered,180 passed, one existing actual AudioAnalyzer integration
skip; dependency-free checks and compileall also pass. Seven new context tests
cover work resets, exact normalization and baseline equivalence, support,
constraint safety, deterministic failures, invalid inputs and undefined metrics.
Independent review verified the conditional sampler formula, training scope,
plan-before-score ordering and explicit failure accounting.

Review found an aggregation edge case: if every successful sample has one note,
interval descriptors are undefined and mean(empty) would lose the final report.
The driver now records null and a zero valid-value denominator instead. This
reporting-only fix did not change model/support/settings or initial scores,
statuses and MIDI hashes. Initial and final plans remain as separate artifacts;
the common-success analysis is marked a post-result reporting addition.
Repeated final conditions/common-subset results match exactly, excluding the
new run timestamps and their plan hashes. All original source bytes remain
unchanged. No source or human-label reassignment, main merge, live project edit,
audio release, GPU or paid operation.

Reproduce using `tools/compare_context_onset_gate.py --corpus REVIEWED_CORPUS
--source REVIEWED_580_MIDI --output NEW_DIRECTORY`. The driver verifies frozen
source/model hashes and records its own plan before scoring. The generated MIDI
files remain private outside Git.
