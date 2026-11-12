# Cycle14: why generation stops; acceptance-aware sampling and pitch mixture

## Failure mechanism before changing the sampler

Exact replay of three cycle13 failures recovers the same notes and rejection
counts. Each final64-proposal stage violates the three-active-note limit.

| Condition / seed | Last onset | Ticks left | Earliest capacity-release delta | Zero-delta proposals in final64 |
|---|---:|---:|---:|---:|
| timing+pitch /0 |9113|103|77|62|
| timing+pitch /3 |9186|30|8|64|
| neither /1 |9057|159|96|63|

Legal continuations exist before target9216: these are not logically impossible
states. Near the endpoint, the remaining-length condition excludes many common
training timing pairs. The sampler repeatedly proposes near-zero deltas while
three notes remain active. Same-pitch collisions sometimes coincide, but a
pitch-only filter cannot solve a fully occupied three-note state. This evidence
motivates masking timing and pitch jointly, not clipping existing gates or
silently advancing the clock.

The replay's reason flags are nonexclusive. The new experiment's diagnostic
counters may prioritize polyphony over same-pitch; compare rejected attempts,
not the sum of overlapping reason flags.

## Proposed fixed comparison and interpretation

Use the previous-gate/pitch-continuity model, old four training works only,
shrinkage4 and existing budgets. Compare rejection sampling versus direct
sampling of the accepted joint timing/pitch distribution. For each onset delta,
weight its timing mass by the summed allowable pitch weight; a fully occupied
three-note state contributes zero until a voice releases. Sample delta, then
remaining-length-compatible gate, then legal pitch. Existing notes never change.

For pure continuity, this targets the original proposal's accepted-next-event
law. It does not preserve RNG sequences or the old finite64-attempt failure
probability. Avoid claiming the entire generation process is unchanged. A
finite note budget and explicit failure state still apply.

The monotony hypothesis mixes25% uniform pitch probability with75% continuity
probability over the same training vocabulary, before acceptance conditioning.
That may increase variety and reduce repeated pitches, but may also restore
large leaps. Compare rather than select a winner from these few seeds. No
unobserved source or human label is used for choosing the mixture weight.

Brahms580 is already observed and used only as the stated output similarity
reference when applicable. Cornelius583 remains reserved, not training or
parameter selection. No new independent-generalization claim is available.

## Initial fixed-run outcomes

| Direct acceptance conditioning | Uniform pitch mixture | Complete/10 | Rejected proposals | Timing proposals |
|---|---:|---:|---:|---:|
| off |0%|8|209|499|
| off |25%|8|160|455|
| on |0%|10|0|314|
| on |25%|10|0|332|

The original baseline reproduces every seed's old notes/status/rejection count.
Direct conditioning removes the observed retry failures without increasing
retry limits or changing existing notes. That is a proposal-efficiency result,
not automatically a wall-clock speedup: computing legal delta masses adds work.
A bounded sampler can still stop at its note budget or lack a feasible event;
this fixed20/20 result is not a proof of universal completion.

Within the direct-sampling conditions,25% uniform pitch mixture changes
completed-output means: distinct pitches10.9→13.7, repeated-pitch fraction
0.318369→0.219997. Mean absolute interval increases2.098134→3.378890semitones and
above-octave jumps0→0.027568. This is the expected variety/continuity tradeoff,
not evidence of better music. Whole-system acceptance conditioning means a
pitch-mixture change can also affect timing probabilities via legal pitch mass;
it is not a pitch-only edit of an otherwise identical generated tune.

Common accepted seeds1,2,4,5,6,7,8,9 are also reported for matched-set descriptors.
That analysis remains conditioned on success and cannot replace all40 attempt
statuses. Copy-guard failures and partial results are retained separately.

## Cost and endpoint artifacts: important negative findings

Measured generation time for ten seeds, excluding export, is approximately
0.388s for pure rejection versus2.682s for direct conditioning; repeat runs are
0.434s versus3.202s. With25% mixture, direct conditioning takes3.116s (repeat
3.431s). This implementation is slower despite fewer rejected proposals. Timing
is local and small-scale, not a universal benchmark. Sparse/event-boundary
optimization is future work, not an already achieved speedup.

Post-initial diagnostics use an explicitly arbitrary short-gate threshold
24ticks and final-window384ticks. Across all attempted outputs, including
partial failures, short-gate counts in table order are4/3/10/0; all occur in the
last384ticks. The pure direct sampler can fill the endpoint with tiny prior-
supported notes. This is a new quality concern rather than grounds to celebrate
completion alone. Thresholds were not tuned to select a winner, and the initial
plan/results are preserved. Missing blocked-output listening remains missing,
not a preference judgment.

## Verification

187 tests discovered,186 passed, one existing actual AudioAnalyzer integration
skip. Six new tests cover exact whole-vocabulary mixture, baseline parity,
exhaustive tiny-state joint-feasibility masses, no implicit advancement,
determinism/safety and invalid inputs. Dependency-free checks, compileall and
whitespace checks pass. Independent review verified the final joint-conditioning
formula and data boundaries; an obsolete pitch-only draft was rejected before
any experiment, not used as the implemented fix.

All36 complete MIDI files preserve exact target/EOT, maximum3 voices and no
same-pitch overlap; exact roundtrip and repeat byte hashes pass. Results and
common-seed analyses repeat excluding measured times and new-run timestamps/
plan hashes. Original source files are unchanged. No fresh predictive scores,
new training data, public audio, main merge, live-project changes, GPU or fees.

Reproduce `tools/compare_feasible_context_generation.py --corpus REVIEWED_CORPUS
--source REVIEWED_580_MIDI --output NEW_DIRECTORY`. Plans are written before the
run; final reporting additions are distinguished from the initial plan.
