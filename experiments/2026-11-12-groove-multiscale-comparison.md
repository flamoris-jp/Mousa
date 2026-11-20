# Groove fixed backoff and reversible IOI decomposition

## Scope and frozen conditions

Cycle34 reused the exact Cycle33 12 training recordings (six drummers, 5,034 events) and eight **already observed** diagnostic recordings. Validation has two drummers/four recordings/2,758 events; test has two further drummers/four recordings/3,850 events. This is not fresh independent validation. All source hashes, split assignments and the 1,130 unused-recording status remain unchanged. No original or prior snapshot was modified. No generation or audio was produced.

Six conditions, including k=4/32/256, were frozen before this run. All outcomes are reported; no condition is selected for adoption from these scores. The control and k4 model reproduce all 16 Cycle33 work-condition NLL sums exactly.

The new representation is **coarse inter-onset interval plus fine remainder**, `dt=120*q+r`, not inferred beat position, meter, phase or expressive microtiming. It preserves each original PPQ480 tick. The support remains all integers 0..30,720. Quotients 0..255 admit 120 remainders; quotient256 admits only remainder0. Quotient prior mass is legal-bucket-width/30,721; residual pseudo-counts are renormalized over each legal remainder set. The prior-only joint shape is uniform over ticks. Data-dependent factorized updates are not the same as the old joint count update: representation, statistical sharing and smoothing allocation change together.

## All fixed results

NLL is in nats/event; lower predicts these observed events better, not necessarily music anyone prefers.

| Condition | Validation pooled | Validation macro recording | Test pooled | Test macro recording |
|---|---:|---:|---:|---:|
| Exact unigram | 5.165146 | 5.627138 | 6.353313 | 6.140283 |
| Exact previous-instrument k4 | 5.462280 | 5.923410 | 6.898952 | 6.736367 |
| Exact previous-instrument k32 | 5.261982 | 5.630762 | 6.516660 | 6.346531 |
| Exact previous-instrument k256 | 5.134922 | 5.509679 | 6.291667 | 6.112066 |
| Quotient / global residual | 5.112428 | 5.505830 | 5.742597 | 5.638734 |
| Contextual quotient k4 / global residual | 5.049289 | 5.508220 | 5.773584 | 5.673442 |

Stronger exact backoff mitigated the large k4 loss, but k32 remained worse than the unigram in both pooled splits. k256 modestly improved both pooled splits but worsened drummer10 (5.731458 to 5.761537). Adding quotient context improved validation pooled NLL relative to quotient/residual but worsened test pooled NLL and validation macro-recording NLL. These mixed results remain visible; they do not justify declaring a universal best model.

All per-recording and per-drummer denominators and scores are in `2026-11-12-groove-multiscale-results.json`. Validation drummer7/8 contribute 160/2,598 events; test drummer10/9 contribute 2,642/1,208 events. Four recordings in a split do not mean four independent drummers.

## Verification and limitations

The two runs completed in approximately 0.477 and 0.505 CPU seconds, well inside the fixed60-second budget. Six conditions completed, zero failed. Reports match exactly after excluding CPU time only; all source hashes remained unchanged. Synthetic tests checked exact rational normalization across all30,721 outcomes for every condition with known and unseen contexts, support endpoints, original control parity, work-boundary resets and fail-closed authorization. CPU measurements are local total-run timing, not a condition-speed ranking.

The prior Cycle33 posthoc decomposition found large losses where an IOI occurred globally in training but never in a particular previous-instrument context. This motivated the fixed alternatives; it is not independent evidence for them. The present cohort was already used to discover that weakness. Style labels, drummer identity, duration, instrument distributions and timing sparsity remain confounded. The training pilot is dominated by rock-labeled recordings while test includes jazz and rock; no style label is established as a cause.

Same-tick source ordering affects previous-instrument context. Velocities, note gates, controller behavior and note-on/off pairing are outside this prediction task. No claims are made about causal groove learning, performance reconstruction, generated quality, musical appeal or broad genre generalization. Rights attribution and use limitations remain in the immutable Google Groove rights snapshot. The Cycle34 usage ledger records continuation of the same roles, not new admissions or fresh test data.
