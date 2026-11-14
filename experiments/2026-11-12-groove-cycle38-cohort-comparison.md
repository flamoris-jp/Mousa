# Cycle38: recording-cohort effects are not stable drummer traits

This analysis reads saved result/plan JSON only. No original MIDI, unscored recording or model constructor was accessed. It compares the same fixed12/35 training sets and six conditions across the earlier eight diagnostic recordings and the eight recordings scored in Cycle37. **Both cohorts are now observed.** The historical `fresh-recording` filenames do not make the later cohort fresh again.

The cohorts contain16 distinct recordings from the **same four drummers**, not16 independent people. Each drummer contributes two recordings per cohort. Training remains35 recordings, observed diagnostics16, and unscored recordings1,099. The duplicate training alias, rights and performer-group split are unchanged.

## Opposite directions within the same drummer

Among24 drummer×condition comparisons, the pooled effect of increasing training12→35 changes sign between cohorts in9 cases. Macro-recording effects change sign in8. These are descriptive counts over overlapping comparisons, not population error rates or independent hypothesis tests.

- Unigram, drummer10: earlier cohort **+0.072126** nats/event (worse), later cohort **−0.751619** (better).
- Unigram, drummer9: earlier **−0.510882** (better), later **+0.092639** (worse).
- Exact k256 has the same direction reversals for those two drummers.
- Drummer7's four exact-IOI conditions reverse pooled direction from worse to better. For k4, however, its later pooled and macro directions disagree, showing that even two recordings from one person can lead to different aggregate interpretations.

These observations argue against labeling a drummer intrinsically “helped” or “harmed” by additional training. Recording content, duration, IOI distribution, instrument use, style/session and count weights differ alongside cohort membership. This report does not isolate any cause.

## Test-split pooled effects, all six conditions

Values are expanded35 minus baseline12 NLL, in nats/event. Negative means improved prediction of these events, not better-sounding music.

| Condition | Earlier test cohort | Later, now-observed test cohort |
|---|---:|---:|
| Unigram | −0.110802 | −0.564710 |
| Exact context k4 | −0.302366 | −0.387068 |
| Exact context k32 | −0.135220 | −0.328427 |
| Exact context k256 | −0.067367 | −0.401777 |
| Quotient/residual | +0.077252 | −0.014823 |
| Contextual quotient/residual | +0.020568 | −0.187893 |

Both quotient/residual conditions reverse pooled test direction. This does not erase the earlier deterioration or select a winner. Every condition, split, drummer and individual recording remains in the results JSON.

## Pooled and macro answer different weighted questions

Earlier validation has2,758 events, including160 from drummer7 and2,598 from drummer8. Later validation has3,180 events, including48 from drummer7 and3,132 from drummer8. Earlier test has3,850 events; later test1,599. Overall the earlier cohort has6,608 events and the later4,779.

All four earlier validation exact-IOI conditions improve pooled NLL but worsen macro-recording NLL. For example, exact k4 changes by−0.244279 pooled but+0.069096 macro. In the later cohort that condition improves under both weightings (−0.342527 pooled,−0.192682 macro). Long recordings dominate pooled results, while each short fill receives the same weight as a long performance in macro means. Neither weighting silently replaces the other.

Combined16-recording summaries are included for bookkeeping only, not as a fresh confirmation sample. Cross-cohort comparisons match drummer identity but **not recording identity**; difference-of-differences is descriptive, not a randomized paired intervention.

## Verification and next question

Initial and repeat reports match after excluding CPU time only. A separate calculation verified120 pooled/macro paired-delta aggregations, and synthetic tests cover direction disagreement, ID-order-independent matching and mismatched denominators. The two historical plans were checked to have identical baseline IDs and expanded training ID/hash sets. No new predictive probability was calculated.

A useful next hypothesis is that event-support composition within a recording mediates these differences more directly than drummer identity. Testing that would require a separately fixed plan to reconstruct the same counts and partition both already observed cohorts by exact-IOI and quotient/residual novelty. It is **not implemented here** and would still not be new independent validation. No new model, training-material selection, parameter tuning or aesthetic claim is proposed for immediate adoption.
