# Cycle35: where the fixed Groove predictions differ

This is posthoc accounting of the already reported Cycle34 six-condition results. The same12 training recordings (5,034 events) and eight already observed recordings were used. No new condition, timing bin, source, split, parameter or selection was fitted. All48 recording-condition NLL sums exactly reproduce the historical values. Source bytes remain unchanged. The1,130 unused recordings remain unused by this model experiment.

## Denominators and instability

Validation drummer7/8 contribute160/2,598 events; test drummer9/10 contribute1,208/2,642. Each drummer contributes two complete recordings. Short fills, styles, lengths, instrument frequencies and performer identities are confounded. Pooled results can conceal materially different contributions.

- Drummer10 remains worse under exact k256: +79.468 total nats relative to unigram. Global-known/local-unseen IOIs contribute +475.916 nats across643 events; global/local-known events offset this by −339.088 across1,964 events. This is not just a problem in tiny contexts: contexts with at least100 training transitions account for +61.108 of the net loss over2,292 events.
- Drummer9 benefits strongly from quotient/residual factorization: −2,226.296 total nats. Its219 globally unseen IOIs with known previous-instrument contexts account for −2,236.928 nats, partly offset by worse performance on other events. Across all1,208 events, the residual values themselves were already seen in training. Recombining previously seen components is a plausible mathematical explanation for improved probability coverage; it is not proof that this learned expressive microtiming or generalizes to jazz.
- Drummer7 and8 show smaller quotient/residual gains (−31.528 and−113.868 total nats). Drummer10's quotient/residual gain is−124.960. The larger pooled test gain is therefore not uniform across performers.
- The largest k4 loss contributions arise from different previous-instrument keys across drummers:44/51/43 for drummer7,26/22/51 for drummer8,36/38/26 for drummer9, and38/26/53 for drummer10. These are conditioning instrument labels, not melodic pitches or causal blame assigned to the instruments.

All six conditions, all four drummers, all eight recordings and all category denominators are retained in `2026-11-12-groove-cycle35-results.json`. Every dimension partitions a drummer's events separately. Dimensions overlap each other; **do not sum contributions across dimensions**. NLL sums describe accounting, not independent statistical tests.

## Verification

The fixed diagnostic was repeated: reports are identical apart from CPU time (approximately0.586/0.582 seconds). A separate report-arithmetic check verified24 historical per-drummer condition means and168 dimension/condition sums. Synthetic tests check exposure-bin edges and additive numerator/denominator accounting. No new model comparison or generated sample was produced.

## What this warrants, and what it does not

Simply treating low training context counts as the whole problem is inadequate: errors also occur in high-exposure contexts. Context support coverage may matter as well as count mass. A separate, prospective **proposal only** records a small parameter-free coverage-adaptive interpolation and matched formula controls. It has not been implemented or scored and is now deferred in favor of planning more training coverage rather than repeatedly adapting models to the same eight recordings. If approved, it must still be described as exploratory testing on these same observed recordings, not a newly independent validation. No adoption decision follows from this report.
