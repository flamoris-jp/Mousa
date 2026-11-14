# Cycle45: Maple addition under fixed count-mass and weighting controls

This actual training comparison adds the complete rights-reviewed Maple Leaf Rag upper staff to17 existing works:18 works /5,512 notes /4,190 onset groups, versus17 /4,319 /3,428. Maple is a polyphonic staff, not an isolated melody, and shares the Joplin/Sawer/Stark series with263. The newly declared11 linked series are used consistently on both sides; they are not11 independent contributors. Historical family and reserve snapshots remain unchanged, with actual use recorded separately.

## Fixed experiment

Seven conditions:17/18 × mass-controlled raw/equal-work/equal-family, plus natural-count raw18. First/later/template-anchor pools separately retain masses17/3411/3428 in the first six conditions; natural18 uses18/4172/4190. Timing prior mass1 stays explicit. Empty-later works contribute zero to that pool. Equal-family weighting retains within-family event-proportional long-work dominance.

Three seeds45000–45002 were absent from tracked seed-field history, not proven unused elsewhere. All conditions use these same seeds, target9216/tail384, max256 notes/max3 voices/64 attempts, one shared60CPU-second budget. No predictive diagnostic score or human rating was added.

Integer scaling preserves exact probability ratios, including prior. However different scales change RNG bit consumption: matching seed labels do not align actual draws. Natural18 and mass-controlled raw18 have identical empirical template/anchor laws but output differences cannot be attributed solely to prior concentration from three samples.

Maple's original2/4 meter and ticks remain intact. The model is not meter-conditioned; output9216 is an8×6/8 convention, not evidence of6/8 phrase understanding.

## Actual outcomes: all21 complete, no copy flags

All7 constructors and21 candidates completed, no CPU skips or generation/copy failures. All three seeds are common-success; each row below is a3-output mean.

| Condition | Notes | Silence ticks | Mean event pitch gap | Above-octave fraction |
|---|---:|---:|---:|---:|
|17 raw fixed mass|32.00|4682.67|7.2523|0.1310|
|18 raw fixed mass|39.67|3428.00|9.1496|0.2241|
|17 equal work|21.33|5297.67|7.7562|0.1784|
|18 equal work|37.67|3552.00|6.9381|0.1549|
|17 equal family|16.33|5856.00|6.1155|0.1222|
|18 equal family|25.00|4698.67|8.1923|0.1699|
|18 natural raw|45.00|3418.67|8.9979|0.2367|

A separate reporting-only paired diagnostic verifies each metric on the same seeds with nonmissing values on both sides. Pitch-gap and above-octave comparisons retain all3 seeds for all four pairings; their means above therefore match paired means. Anchor3gram comparisons retain only2 seeds for raw17/18 and family17/18, and3 for work17/18 and controlled/natural18. Excluded seeds and exact denominators are saved; no missing value is imputed. This conditional subset remains sampling-dependent, not aligned draws.

Adding Maple increases note density and reduces silence under every fixed-mass weighting in this small sample. Gap directions disagree: equal-work decreases while raw and equal-family increase. Event-order intervals include simultaneous staff notes, not inferred voice leading. No weighting is chosen as a winner and no musical-appeal conclusion follows.

All templates are learned. Raw >3-member template occurrences are18 in17 works and47 in18; generation excludes these from sampling under unchanged max3 safety. Weighted excluded mass differs by condition and is retained exactly in results. No original four-note group was removed from learning.

## Structure and repetition diagnostics

Four fixed2bar blocks report note onsets, onset groups, sounding notes and union occupied/silent ticks. Sustained-note intervals are clipped only for measurement, never source/output editing. Empty and singleton blocks are missing for interval-sequence comparison.

Across21 outputs:0 exact equal signed-anchor interval block pairs among90 comparable pairs;0 repeated3-interval windows beyond first among495 overlapping windows. Two sparse outputs lack any such window, so their repeat fraction is missing, not zero. This strict descriptor's failure to detect recurrence is not proof of no meaningful musical repetition, nor evidence that form was learned. Full condition/block denominators remain in structure-summary JSON; raw interval arrays are private.

## Verification, limitations and records

- Final4 plan SHA882a6d62ec19c3400a5d2dabf9a7028f1919182b5872749168e032ab3b42864d bound before fit.
- Initial/repeat reports identical except CPU0.484974/0.517138sec; all21 private files and journals byte-identical.
- Raw17:40 exact timing probabilities and all three generated states equal the frozen old global implementation.
- Natural18/controlledraw18 template and anchor probabilities exactly equal as Fractions.
- All21 outputs pass note/group reconstruction, maxvoice/samepitch/endpoint guards, both-order copy checks against22 originals, and independent structure/timeline recomputation. All original hashes unchanged.
- Ten targeted tests pass; parent profile audit1,794 checks, structure audit1,400 checks; output audit2,301 checks; seed-history audit retained.
- A local verification initially compared JSON lists directly to runtime tuples; canonical JSON normalization resolved this representation mismatch without model/output changes.
- Earlier plans remain unrun. Structure metrics and public-array projection were added before fit after review. Final model and rules were not tuned afterward.
- Additional training is real, but one related work is not independent repertoire diversity; sampling, work content and weighting remain confounded. Weighted ESS is a dependent-event weight descriptor, not independent sample size.
- No actual listening, ratings, phrase labels, public media, deployment or model adoption.

The complete whole-performance input and failed hypotheses remain available for later research. This experiment supports a measured training-size/content effect on symbolic generation descriptors, not a verdict on attractiveness.
