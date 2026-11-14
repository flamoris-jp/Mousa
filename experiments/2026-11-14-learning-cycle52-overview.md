# Cycle52: does learned timing context transfer?

The owner's revised priority is learning, not judging musical appeal. This experiment asks whether previous-note-duration context improves prediction beyond a learned timing marginal and a shuffled-association control.

## Important split discovery before fitting

All 153 pairs among the 18 admitted works were screened with the unchanged exact-eight-interval motif / global interval similarity >= 0.8 rule. Nine pairs had exact motif links; none reached the global threshold. Taking transitive closure together with the existing eleven source/editor/contributor families leaves **four components of sizes 2, 13, 2, 1**. These are not eighteen independent tests. Short common motifs can connect otherwise different music: this is a conservative guard, not a finding that the works are copies. No threshold was relaxed to manufacture more folds.

Each component was held out in turn and models were fitted anew only on the other components. Thus the largest test fold trains on just five works; the other folds train on 16, 16 and 17 works. Every source remains in its historical role. This is **retrospective cross-validation** of previously trained, researcher-exposed data. It is not a newly sealed prospective evaluation, and previous model development saw these works.

## Frozen comparison

Before any real fit, the plan bound sources, all Python dependencies, dataset records, all pair screens, folds, twenty shuffle seeds, supports and metrics. An independent review approved that exact plan. Conditions:

- No-data uniform timing law, a deliberately weak baseline.
- Learned global timing counts with total uniform prior mass one.
- Existing previous-maximum-gate-bin contextual model, local backoff mass four.
- The same contextual model with gate-bin labels randomly permuted over later transitions **within each training work**, twenty fixed seeds. This preserves timing marginals and local context counts, but breaks within-work alignment. Work-level style associations remain.

Only teacher-forced onset-group timing is scored. No pitch, joint template likelihood, generated quality or preference claim. First-event loss is separate; primary comparison is equal-fold mean of each fold's equal-work later-event NLL, in nats (lower is better). The shuffle summary is mean NLL across seeds, not a mixture model likelihood.

| Condition | Primary fold-macro | 18-work macro | 4,172-transition pooled |
|---|---:|---:|---:|
| No-data uniform | 9.416378 | 9.416378 | 9.416378 |
| Learned global | 2.004423 | 2.663905 | 3.069735 |
| Learned duration context | 1.699634 | 2.434030 | 2.998911 |
| Shuffled context, 20-seed mean | 2.048240 | 2.849892 | 3.329109 |

Duration context beats global in all four fold-macro comparisons and 15/18 individual works. It beats mean shuffled context in three of four folds; the one-work Handel fold reverses that contrast (context 1.244580 versus shuffled 1.230472). In the 13-work fold, pooled context loss **worsens** versus global (3.416996 versus 3.387080), although its equal-work average improves. Do not hide those failures behind the overall average.

The results are consistent with transferable timing associations beyond an unconditional frequency table in this retrospective diagnostic. They do not prove broad generalization, absence of memorization, learning of full melodies, or musical appeal. The uniform comparison alone would be weak evidence; the learned-global and shuffled controls matter more. No significance or confidence claim is made from four dependent, unequal folds or twenty randomization seeds.

## Verification and outcomes

- Full local suite: 457 tests, 456 passed, one existing optional AudioAnalyzer integration skip. Five new synthetic tests.
- Initial/replay all 414 rows and aggregates match exactly except recorded CPU, and complete journals match byte-for-byte. CPU about 1.402/1.407 seconds (fit/score stage; screen about 2.4 seconds).
- Per-event probabilities independently checked against the closed-form smoothed conditional law during both runs.
- All input hashes unchanged; no reserved or previously observed external diagnostic work was fitted or scored. The legacy loader reads some existing diagnostic sources for integrity checks only.
- No new MIDI, audio, source admission, GPU, paid operation, live Cantabile change, merge or deployment. No human ratings invented.

## Next hypotheses

1. Freeze a prospective test on new, legally reviewed families to check whether this timing gain survives outside this researcher-exposed corpus. Preserve all existing test-observation roles.
2. Investigate the large-component pooled regression and learning curves at controlled training mass; content and sample size otherwise remain confounded.
3. Extend learning diagnostics to pitch/interval prediction separately rather than turn timing scores into an artistic-quality score.

Plan/results/journal and source-level numbers accompany this document. Private archive receipts and exact-head CI are recorded separately after publication to the draft research branch.
