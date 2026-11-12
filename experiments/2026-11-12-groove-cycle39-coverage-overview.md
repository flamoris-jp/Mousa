# Cycle39: 58 unique Groove training performances

The fixed rhythm-only study actually expanded training from35 to58 unique recordings,19,409 to32,141 positive note-on events. Twenty-three previously unused recordings entered the model. The same six training drummers and sixteen **already observed** diagnostic recordings were retained; no new test recording or melodic-pitch model was introduced. The12-recording reference below uses saved scores only, not another fit.

## Selection, rights and limits

Up to ten complete recordings per training drummer were selected by SHA/ID order, with prior35 retained and all evaluation-session material excluded. Drummer4 had only nine eligible recordings. The59 candidates included the known exact-byte alias `drummer2/session2/8`; it stayed excluded in favor of the already trained `/7`, with no replacement. The final58 recordings contain no duplicate byte hashes. All MIDI bytes, PPQ480 and expressive tick timing were preserved.

The reviewed Google Groove CC BY4.0 rights snapshot and credits remain unchanged. All1,150 archive originals were read-only integrity-checked for screening. There were40,302 cross-split comparisons,235 weak pattern-window candidates and no strong unresolved cross-split match. Within1,711 candidate pairs, the known duplicate alias was the only strong match. These bounded checks do not certify independent musical patterns or public-release originality.

A separate60-work/60,000-event profile was tested; the old35-work/30,000-event profile was not edited or bypassed. Actual expanded training required32,141 events. Both runs remained below the60-second CPU budget. No GPU, audio generation, raw MIDI transfer or public media release occurred.

## Quantity and composition both changed

| Training drummer | Old35 recordings/events | New58 recordings/events |
|---|---:|---:|
| drummer1 | 6 /3,641 | 10 /3,693 |
| drummer2 | 5 /2,877 | 9 /4,465 |
| drummer3 | 6 /507 | 10 /1,162 |
| drummer4 | 6 /1,141 | 9 /2,227 |
| drummer5 | 6 /7,333 | 10 /14,401 |
| drummer6 | 6 /3,910 | 10 /6,193 |

Drummer1 added four recordings but only52 events; drummer5 now contributes44.81% of all training events, versus37.78% before. Provided style labels increased from12 to19, including very short new labeled fills. These are dataset labels, not independently verified genres or composition families. Exact drummer/session/style record and event fractions are in the frozen fit plan. This is a coverage-and-content change, not an isolated causal experiment on recording count.

## All fixed pooled results

Same observed16: validation5,938 events from eight recordings/two drummers; test5,449 events from eight recordings/two other drummers. Lower NLL predicts these events better, not necessarily music listeners prefer.

| Condition | Validation35 →58 | Test12 →35 →58 |
|---|---:|---:|
| Exact unigram | 5.275011 →5.269562 | 6.839174 →6.595173 →6.138004 |
| Exact context k4 | 5.351006 →5.280415 | 7.269450 →6.942229 →6.684282 |
| Exact context k32 | 5.246271 →5.212657 | 6.901769 →6.709852 →6.441938 |
| Exact context k256 | 5.163132 →5.156140 | 6.703263 →6.537764 →6.231970 |
| Quotient/residual | 5.211060 →5.216848 | 5.921628 →5.971861 →5.920744 |
| Contextual quotient/residual | 5.151916 →5.156153 | 6.004550 →5.963946 →5.895489 |

Test pooled NLL improved under all six fixed models. Validation worsened under both quotient/residual variants. Those two models also worsened for drummer8 (+0.007488 and+0.007228 nats/event), despite improving for the other three drummers. All per-recording, per-drummer, pooled and macro means are retained, with no winner selected.

Distinct observed exact IOIs increased367→437. Globally unseen diagnostic events decreased45→32 in validation and335→108 in test. Every event still received positive probability within the same exact support; none was rounded or dropped. Added coverage is one descriptive change, not proof that it alone caused the likelihood gains. Quotient/residual is a reversible IOI representation, not learned beat phase or expressive microtiming labels.

## Verification and actual use

Both runs completed all twelve journaled constructors (six baseline35 and six expanded58). The baseline35 exactly reproduced96 historical recording-condition NLL sums across both diagnostic cohorts. Initial/repeat reports match after excluding CPU time only; before-fit records and journals are byte-identical. CPU totals were approximately2.032/2.047 seconds, not a comparative speed benchmark. Originals remained unchanged.

Independent coordinator reviews separately checked selection, synthetic exact probability/count parity and276 result aggregation/coverage identities. Local verification checked24 split aggregations and known/unknown denominators. A pre-fit synthetic import test initially caught a missing historical-report constant; it was corrected before final plan freeze and any real fitting, and the failure was recorded. Six targeted tests then passed.

The current usage ledger records58 train-used recordings,16 observed untrained recordings and1,076 unscored/untrained recordings (40 reserved evaluation recordings, one duplicate alias and1,035 others). Historical rights/usage/plan snapshots remain unchanged. This repeated observed-cohort research does not establish robustness to new performers or recordings, aesthetic quality, or a general law that more data always helps.
