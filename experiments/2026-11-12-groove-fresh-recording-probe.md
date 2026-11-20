# Cycle37 prospective probe on eight previously unscored recordings

## What was genuinely new

Before any predictive score, the plan fixed two whole non-evaluation recordings per heldout drummer7–10 by source SHA then ID, excluding previously trained/observed/duplicate-alias identities and bytes. The original4096-event-per-recording cap was retained; no score-guided replacement or truncation occurred. Independent review recomputed the selection and checked usage, hashes and gates. All six existing models and both12/35 training corpora were frozen.

The selected eight recordings have4779 events: validation3180 (drummer7:48, drummer8:3132), test1599 (drummer10:1245, drummer9:354). They were technically inventoried before, but not predictively scored or fitted. **These are new recordings, not new performers**: models had already been compared on different recordings from the same heldout people. They provide a prospective recording-level check, not independently sampled new-person generalization or representative genre coverage.

The unchanged exact-byte/onset-key/tempo-normalized/coarse-pattern rule compared them with every other non-evaluation recording:8872 pairs,0strong flags,92weak matches retained. Screening does not prove every musical pattern independent. All40 shared evaluation recordings remain reserved for prediction and training.

## All frozen results

Mean exact-IOI NLL in nats/event, lower better for prediction. Every condition is retained; none selected for adoption.

| Model | Validation12 | Validation35 | Test12 | Test35 |
|---|---:|---:|---:|---:|
| Unigram |5.474446|5.396305|8.009007|7.444297|
| Exact k4 |5.808886|5.466359|8.161518|7.774450|
| Exact k32 |5.544615|5.340939|7.829016|7.500590|
| Exact k256 |5.383564|5.244945|7.694288|7.292510|
| Quotient/residual |5.350156|5.303469|6.352690|6.337867|
| Contextual quotient/residual |5.367980|5.262921|6.560660|6.372767|

All pooled splits and recording-macro means improve under35 recordings in this probe. That contrasts with quotient/residual worsening on Cycle36's older test recordings. It does **not** erase that earlier negative result or establish universal benefit from more material. On the new drummer9 recordings, unigram, k256 and both quotient models worsen; only k4/k32 improve. Large drummer8/10 event counts dominate pooled averages. The validation recordings contain only12,36,1016 and2116 events, so recording-macro and event-weighted estimates answer different questions.

The12→35 training change also changes style, instrument and duration mixture, not only sample count. This probe cannot isolate quantity causally, assess musical appeal, or validate generated grooves. No new generation was performed.

## Verification and irreversible observation status

The two executions match exactly except CPU time (0.9723/0.9467 seconds). All12 model-construction journal entries and96 prediction entries completed; before-fit and cumulative prediction journals are byte-identical on repeat. Independent arithmetic checks verified24 split aggregates. Original hashes remain unchanged. A bound approval references the plan, screen and independent review; no model choice changed after these scores.

All eight are now recorded as **observed, untrained**, never fresh again. Current recording roles:35training/16observed-untrained/1099remaining-unscored-untrained. The latter include40reserved evaluation recordings,one excluded exact duplicate alias and1058other. These are recording-role counts, not counts of independent compositions. Source originals remain in the previously archived ZIP; this cycle adds metadata only.

Artifacts: fixed plan/screen/review/clearance/results/verification and journals under `2026-11-12-groove-fresh-recording-*`, plus `../datasets/research-groove-fresh-observations-cycle37.json`. The old Cycle36 usage ledger remains immutable.
