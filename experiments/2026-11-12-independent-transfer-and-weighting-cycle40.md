# Cycle40: prospective Dowland timing transfer and mass-controlled drum weighting

## Previously unscored melodic family

Before the first predictive call, plan `06803ea492e4849e7dba70af9aa648b399bc7af03dd802ea09f725b11e167c15` bound the unchanged Cycle37 four-arm models, the same seventeen training works, all source and implementation hashes, support and comparison rules. The two Dowland works were never fitted. Rights/representation had already been inspected; they were not unseen in every sense. They form one 1597 book/Peter Chubb contributor family, not two independent cohorts.

All 89 + 43 Cantus groups were evaluated without clipping, filtering or quantization. Original full SATB, 2/1 meter, first onsets 0/768 and EOT 49152/39936 remain intact. Forty-five fixed similarity comparisons passed; these limited checks do not establish legal originality or universal independence.

| Frozen arm | Equal-work group-delta NLL |
|---|---:|
| Global | 3.710699963 |
| Previous cardinality | 4.086068948 |
| Previous maximum gate | 2.462154106 |
| Active sounding horizon | 2.518445454 |

Both gate-history conditions improved timing prediction on both works relative to global; cardinality worsened both. This is teacher-forced timing likelihood, not joint pitch/harmony/gate accuracy, generated melody quality or human enjoyment. All four conditions and each work's first/later and pooled losses are retained. No model was selected or retuned after seeing these results.

Each run journaled all eight prediction attempts before calling the model, and all eight completed. Repeat reports match except CPU. An independent review checked 54 aggregate/journal identities, including absence of evaluation IDs from fit journals. The new observation ledger marks both works **observed evaluation, never trained**. Historical reserve rights metadata remains immutable; consult this latest ledger before later studies. Historical preparation scripts are replay tools, not authority to claim the same works fresh again.

## Equal performer mass does not improve every summary

Plan `16e6216e4a5094c43d9e9aea8abe06a049fd345aa89b9bdb338731b685651b02` fixed four rhythm conditions: raw versus equal-drummer event weighting, each with exact unigram and quotient/residual marginal models. The same 58 training recordings and sixteen already observed diagnostics were used. Each event weight is 32141/(6 × training events for its drummer), with exact rational arithmetic. Total count mass stays 32141 and each original prior remains total mass one. There is no local previous-instrument context, avoiding a separate local shrinkage-strength change.

| Model | Validation pooled raw → equal | Test pooled raw → equal |
|---|---:|---:|
| Unigram | 5.269562 → 5.250861 | 6.138004 → 6.106502 |
| Quotient/residual | 5.216848 → 5.200769 | 5.920744 → 5.887721 |

Although pooled losses improved, validation recording-macro losses worsened by 0.027299 and 0.031472 nats/event, respectively. Short recordings have equal weight in the macro summary but little pooled influence. Per-drummer results are retained. This is not a universal improvement or proof of reduced overfitting.

Weights range approximately 0.372 to 4.610. The small drummer3 training set is amplified; its distinctive patterns could be amplified too. Algebraic Kish event ESS falls from 32141 to about 17688. Strongly dependent musical events mean this is not a count of independent observations. No weight was tuned on evaluation scores, and no new diagnostic recordings were consumed.

All 32 raw historical work-condition NLL sums reproduce exactly. Repeat results match except CPU; four constructors completed. Independent checks cover 216 synthetic exact mass/probability identities and 60 result identities. Groove roles remain 58 trained / 16 observed-untrained / 1076 unscored-untrained, with all forty evaluation-session recordings and the duplicate alias excluded.

## Reproducibility, history and limits

Full suite: 378 tests, 377 passed and one existing integration skip. Dependency-free suite: 378 tests, 337 passed and 41 expected optional skips. Compile and diff checks pass. No new audio, generation or live Cantabile change occurred; A–D human evaluation remains unanswered. No GPU, paid action, merge, deployment or media publication occurred.

The previous 56,059-character PR body is preserved exactly in `docs/RESEARCH_PR_HISTORY_THROUGH_CYCLE39.md`, including failures, qualifications and historical roles. Its digest and exact preservation check are recorded separately. A shorter PR entry links this history and current reports instead of discarding earlier results. Owner-designated LIME archival completion is tracked by separate readback receipts; local snapshots alone are not proof of remote storage.
