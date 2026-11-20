# Cycle15: computation parity versus a changed ending policy

These are separate questions. A faster implementation should preserve the
original feasible sampler's integer probability masses and, where the RNG path
is preserved, exact seeded events. Allowing a trailing rest changes the ending
policy and therefore the output distribution; it cannot inherit a claim of
probability equivalence from the computation optimization.

The fixed small-corpus setting remains adaptive research: four historical
training works only; already-observed580 is a source/copying reference, not a
fresh evaluation;583 stays reserved in the same contributor/publisher family.
No parameters are selected using an unobserved source, and no human preference
or musical appeal is inferred from completion rates or timing descriptors.

## Optimization target

Legal pitch mass is constant between active-note release times. Calculate the
whole-vocabulary weight once, subtract active pitch weights, and reuse that
legal sum within release intervals rather than scanning the vocabulary for
every possible delta. Keep ascending integer delta masses and random draw order.
Measure runtime separately from proposal counts, and retain the old sampler as
a reference rather than replacing its historical results.

## Ending-policy hypothesis

Instead of forcing a sounding gate to end exactly at9216ticks, allow the final
MIDI EOT to remain9216 while the last sounding note ends at most384ticks earlier.
That is at most one quarter-note duration at PPQ384, not an entire6/8bar. Do not
trim, extend, rewrite or insert notes. Stop only after a nonempty generated
prefix already meets the declared tail condition. This may avoid tiny endpoint
fillers, but it is a hand-specified stopping rule, not a learned cadence.

The repeatedly reused seed IDs are diagnostic cases, not an untouched random
test set. Exact parity is a software-correctness requirement, whereas musical
comparisons on these cases remain exploratory. Fresh source families and human
listening are still needed before claiming broader musical improvement.

## Fixed-run results

Optimization-only exact-end generation reproduces every old seeded returned
field (apart from new endpoint metadata), including notes, rejection counters
and final state. Integer mass tests and independent randomized-state checks
also match. This is stronger than merely similar aggregate distributions.

Measured ten-seed generation time, excluding export:

| Pitch mixture | Old feasible implementation | Optimized | CPU seconds old → optimized |
|---|---:|---:|---:|
|0%|2.754s|0.487s|2.751→0.486|
|25%|2.997s|0.538s|2.995→0.538|

The old/new execution order alternates by seed. These small local measurements
show a computation improvement for this implementation, not a universal speed
claim; cache state, interpreter and hardware affect timings. Output draws and
probabilities are unchanged for this optimization-only comparison.

All four endpoint/mixture conditions complete10/10. With0% mixture, allowing up
to384ticks of trailing silence changes average note count31.4→27.9, short-gate
count (under24ticks) totals10→0, and mean actual silent tail0→287.2ticks. With25%
mixture, short-gate count stays0, notes33.2→31.0, and tail0→240ticks. Original
note prefixes are unchanged; generated MIDI EOT remains9216 in all conditions.

This removes endpoint filler events in these cases by stopping sooner, not by
learning a better cadence. It also reduces distinct-pitch means10.9→9.8 in the
pure-continuity condition and13.7→13.3 with mixture. Rest, phrase completion and
replay preference still need human assessment. No score establishes whether the
result sounds pleasantly finished or prematurely cut off.

Repeat timing is2.597→0.449s (0% mixture) and2.859→0.525s (25% mixture), about
5.4–5.8x for the paired local implementation benchmark across both runs. Do not
apply that ratio to training, rendering, complete workflow latency or other
hardware. Non-timing results and all40 MIDI hashes match across runs. The20
exact-end MIDI outputs also match the existing cycle14 files byte-for-byte.

## Verification and boundaries

193 tests discovered,192 passed, one existing actual AudioAnalyzer integration
skip. Six new optimization/termination tests pass; dependency-free checks,
compileall and whitespace checks also pass. Independent review additionally
compared100 legal-state mass arrays,200 seeded exact-end outputs and200
bounded-rest prefixes, and audited final source hashes and driver data flow.
All40 outputs preserve EOT9216, the declared silence bound, maximum3 voices and
no active same-pitch retrigger. No copying-guard failures were replaced by a new
seed. Baseline, plan and original files are unchanged.

No musical attractiveness, fresh predictive generalization, human preference,
public-media clearance or learned cadence is claimed. No live Cantabile edit,
main merge, deployment, raw corpus/model publication, GPU or paid operation.

Reproduce `tools/compare_optimized_endpoint.py --corpus REVIEWED_CORPUS --source
REVIEWED_580_MIDI --output NEW_DIRECTORY`. Plans precede the experiment. MIDI and
repeat-run artifacts remain private outside Git; committed results contain
hashes, metrics, hypotheses and limits.
