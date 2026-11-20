# Cycle40: fixed total-mass drummer weighting

This is a reused-diagnostic comparison, not fresh validation or a musical-appeal test. All four predeclared conditions completed without changing weights after results. Training remains 58 complete performances / 32,141 events from drummers 1–6. The same 16 already-observed performances / 11,387 events from drummers 7–10 are evaluated; 1,076 performances remain unscored and untrained.

## Fixed comparison and result

Raw event weights are 1. Equal-drummer weights are 32141/(6 × that drummer's training events). Both models retain exactly 32,141 weighted event mass and their original prior mass 1. The exact-IOI marginal and reversible quotient/residual marginal are separate fixed formulas; no previous-key model, generation, beat-phase learning or hyperparameter selection is involved.

Mean NLL in nats/event, lower is better for this symbolic prediction task:

| Model | Split | Raw pooled | Equal pooled | Raw recording macro | Equal recording macro |
|---|---|---:|---:|---:|---:|
| Exact marginal | validation | 5.269562 | 5.250861 | 5.636229 | 5.663528 |
| Exact marginal | test | 6.138004 | 6.106502 | 6.218876 | 6.146440 |
| Quotient/residual | validation | 5.216848 | 5.200769 | 5.522330 | 5.553802 |
| Quotient/residual | test | 5.920744 | 5.887721 | 5.903326 | 5.826950 |

Validation has 8 recordings / 5,938 events / 2 drummers; test has 8 / 5,449 / 2. Each diagnostic drummer contributes 4 recordings. All per-recording and per-drummer results remain in the results JSON.

Pooled NLL improves in all four model/split comparisons, but validation recording-macro NLL worsens for both models. Drummer7's macro exact NLL worsens 6.068068→6.156477, and quotient/residual 5.891243→5.982102; that drummer's pooled values improve. Thus even individual-drummer aggregate direction depends on event versus recording weighting. This is not universal improvement and does not justify selecting a winning weighting.

## Exposure, scale and limitations

The raw corpus has 44.81% of events from drummer5. Equal weighting reduces that exposure but amplifies drummer3, whose 1,162 training events receive weight 4.610011; the smallest weight is 0.371976. Kish event ESS decreases from 32,141 to 17,687.994795. This is an algebraic weight-dispersion descriptor, not a count of independent observations: IOIs within performances and sessions are dependent. Equal drummer mass does not equalize styles, sessions, independent performances or local rhythm support.

Total event mass and marginal prior strength remain fixed; component support and q/r endpoint normalization remain unchanged. Relative counts still change, and this can amplify performer-specific patterns. No causal reduction of overfitting, unseen-performer generalization or musical attractiveness follows from this reused set.

## Verification and retained evidence

- Plan fixed before fit: SHA256 16e6216e4a5094c43d9e9aea8abe06a049fd345aa89b9bdb338731b685651b02.
- Four constructor journals completed, original bytes unchanged, raw 32 recording/model NLL sums exactly match Cycle39.
- Run/repeat identical except CPU time: 1.242221154 / 1.282386606 seconds, below 60 seconds.
- Local aggregation audit: 88 checks; independent parent result audit: 60 checks. Parent synthetic profile audit: 216 checks.
- Six Cycle40 tests pass, including full-support normalization, raw parity, endpoint support and pre-fit failure journaling.
- An initial local verification assertion omitted the serialized mass's extra decimal field and failed before artifact saving; the assertion was corrected. Neither experiment nor frozen code/results changed.
- No new sources, labels, human ratings, media, model adoption or post-result weight tuning. Historical ledgers remain unchanged; a separate continuation ledger records unchanged roles.
