# Cycle34: backoff, exact IOI decomposition and polyphonic groups

Two separate tasks were studied with fixed small CPU budgets. Their likelihoods
have different outcomes and must not be compared against each other.

## Drum IOI prediction: same native ticks, previously observed recordings

The same12 training recordings and eight observed diagnostics retain their
performer/session split. No originals, roles or old snapshots changed. All six
conditions were fixed before this run; no winning condition is automatically
adopted from these repeated diagnostic scores.

| Condition | Validation pooled NLL | Test pooled NLL |
| --- | ---: | ---: |
| Exact unigram | 5.165146 | 6.353313 |
| Previous instrument, k4 | 5.462280 | 6.898952 |
| Previous instrument, k32 | 5.261982 | 6.516660 |
| Previous instrument, k256 | 5.134922 | 6.291667 |
| Coarse IOI / remainder | 5.112428 | 5.742597 |
| Contextual coarse IOI / remainder | 5.049289 | 5.773584 |

`dt=120*q+r` preserves every original PPQ480 tick; it is **not** inferred beat
position or proven expressive microtiming. Legal endpoint buckets and exact
normalization are checked. The prior-only shape is uniform over original tick
outcomes, but statistical sharing and data-dependent smoothing also change.
Stronger backoff mitigates sparse-context errors. Additional coarse-IOI context
helps validation pooled loss but worsens test loss and validation recording-macro
loss. k256 also worsens one test drummer. These qualifications prevent a universal
best-model claim. All16 historical control loss sums reproduce exactly; repeat
results match except CPU timing (about0.477/0.505 seconds).

Details: `2026-11-12-groove-multiscale-comparison.md`.

## Pitched group timing and private generation

All16 training works retain4,150 notes represented as3,259 distinct-onset groups.
Both arms predict the same group-onset delta, not historical individual-event
outcomes. Initial support includes zero; later group deltas are strictly positive.
Global timing NLL4.144505 worsens to4.799273 when conditioned on previous group
cardinality. Both already observed diagnostic works worsen. This does not show
that polyphonic grouping is useless, only that this specific extra condition
fails on these diagnostics.

A separate empirical template sampler retains relative pitches, gates, velocities,
release velocities and within-group order. Templates above three notes remain
in training, but18/3,259 occurrences (0.5523%) are generation-ineligible under the
fixed three-voice safety cap. No notes are clipped or deleted inside a sampled
group. Both arms generate5/5 private candidates, zero fixed copy flags, with exact
repeat bytes and independently reconstructed note fields. Generation feasibility
is not the same probability distribution as teacher-forced timing prediction.
Timing NLL excludes template/pitch/gate likelihood and says nothing about appeal.
Counts and reasons for rejected proposals are recorded, and CPU deadlines are checked inside the
proposal loop as well as before other bounded calls.

Details: `2026-11-12-group-onset-comparison.md`.

## Verification, roles and next hypotheses

Independent synthetic audits checked216 drum probabilities and1,200 group
probabilities;120 synthetic grouped outputs were checked for full template
retention, safety, reproducibility and CPU stopping. No original MIDI was changed,
no raw/derived music was committed, and no live Cantabile project was touched.
The copies check remains a limited interval-pattern screen, not public-release
or legal originality clearance. No new audio or subjective labels were created.

Current roles remain16 pitched training works; Groove12 training, eight observed
but untrained diagnostics and1,130 unused recordings. Versioned metadata-only
snapshots are sent to the owner-designated store; prior originals and snapshots
are not overwritten. Read-back completion is tracked separately in the PR.

Future studies can test larger/style-aware training subsets without disguising
these diagnostics as new, or model continuity between intact note groups rather
than sampling anchors independently. Those are hypotheses, not completed work
or inferred harmonic-function labels. No main merge, deployment, GPU or fees.
