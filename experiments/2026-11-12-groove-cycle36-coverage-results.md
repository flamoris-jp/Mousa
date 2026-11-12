# Cycle36: more whole Groove performances, mixed predictive effects

## What actually ran

The authorized comparison retained the original12 training recordings and added23 previously unused performances from the same six training drummers. The expanded set contains35 unique MIDI byte hashes and19,409 positive note-on events, versus12 recordings/5,034 events at baseline. All six Cycle34 prediction formulas stayed fixed. Both conditions were evaluated on the same eight **already observed** recordings, not a new independent test. No music was generated and no raw originals were retransmitted.

The metadata rule originally selected36 candidates. Known duplicate `drummer2/session2/8` was explicitly excluded from fitting in favor of `drummer2/session2/7`, following baseline-priority then ID-order deduplication. There was no replacement. The36-candidate preparation plan/screen and the first unrun fit plan remain historical records. A separate standalone35-work profile was reviewed and tested; it retains the old30,000-event ceiling rather than silently bypassing the original20-work constructor.

All40 known shared-pattern evaluation-session recordings remain reserved. Cross-split screening covered23,024 comparisons and found no strong matches under the predeclared exact/normalized/coarse-window rules. The138 weak window candidates are not evidence of independent compositions or proof of copying. Screening remains limited.

## All fixed pooled results

NLL is nats per exact IOI event. These are predictions of observed events, not music-preference scores.

| Condition | Validation12 →35 | Test12 →35 |
|---|---:|---:|
| Unigram | 5.165146 →5.135159 | 6.353313 →6.242511 |
| Exact context k4 | 5.462280 →5.218001 | 6.898952 →6.596587 |
| Exact context k32 | 5.261982 →5.137117 | 6.516660 →6.381439 |
| Exact context k256 | 5.134922 →5.068800 | 6.291667 →6.224300 |
| Quotient/residual | 5.112428 →5.104513 | 5.742597 →5.819849 |
| Contextual quotient/residual | 5.049289 →5.023926 | 5.773584 →5.794152 |

More training recordings did **not** uniformly improve predictions. Both quotient/residual variants worsened on pooled test data, despite small validation improvements. Drummer7 worsened under every exact-IOI condition, while drummer9 improved under those four conditions but worsened under both quotient/residual conditions. Unigram also worsened for drummer10. Per-drummer, per-recording, pooled and macro recording means and denominators are preserved in the full results.

Validation comprises four recordings from two drummers,2,758 events; test comprises four recordings from two further drummers,3,850 events. Equal source counts do not balance event mass, style, duration or instrument exposure. This comparison changes training content and weights as well as volume; it does not isolate the causal effect of dataset size. Quotient/remainder is a reversible coarse-IOI representation, not learned beat phase or expressive microtiming.

## Verification and honest failure history

Initial attempts stopped before source access and model construction because the coordinator's clearance used a status string while the frozen driver required `approved:true`. The original clearance and rejection record were retained. A compatible clearance references the same authorization and unchanged plan; no model or threshold was modified.

The successful initial and repeated runs each completed12 journaled constructors: six baseline and six expanded. Before-fit records and attempted/completed train-ID journals are retained. Each baseline model exactly reproduced its eight historical recording-level NLL sums (48 checks). Repeated reports matched after excluding CPU time only; journals and before-fit records were byte-identical. All source hashes remained unchanged. Total CPU was approximately1.175/1.034 seconds, under the fixed60-second cap. These local timings are not a model speed ranking.

The usage ledger now records35 train-used recordings (23 newly used), eight already observed diagnostic recordings and1,107 not fitted:40 reserved evaluation recordings, one duplicate alias and1,066 others. Historical role/rights snapshots remain unchanged. No new independent validation, public music release, generated audio or claimed aesthetic improvement follows from this experiment.
