# Cycle37: count growth, coverage and probability redistribution

This is posthoc decomposition of the fixed Cycle36 comparison, not another tuned model. The original12 training performances (5,034 events) and deduplicated35 (19,409 events), six formulas and eight already observed diagnostic recordings are unchanged. No other corpus originals were accessed. All96 historical recording-condition NLL sums were exactly reproduced. The duplicate alias remains excluded and1,107 recordings remain not fitted.

## Exact support, not rounded targets

The shared support has30,721 integer IOIs. Training12 observed281 of them; training35 observed86 additional outcomes. The remaining30,354 outcomes are unseen in both. These same three sets are used to sum exact Fraction probabilities under both training conditions, including the quotient/residual models. No timing targets or evaluation events were rounded or dropped.

For every diagnostic previous-instrument context, the report contains the exact mass assigned to each set. Drummer summaries additionally weight these context distributions by their observed diagnostic frequencies. Those are descriptive, teacher-forced mixtures, not autonomous generative distributions. Every mass partition sums exactly to one.

## A measurable prior-strength effect

For the unigram with fixed total uniform prior mass one, an outcome absent from training has probability `1 / (30721*(N+1))`. Increasing training from5,034 to19,409 events therefore raises loss on every still-unseen event by exactly `log(19410/5035) = 1.349374871` nats. Nominal prior strength stayed fixed, but its weight relative to observed counts did not.

This does not mean more data is always harmful. For drummer9,83 newly covered events improved unigram total NLL by−783.501 nats, whereas137 still-unseen events worsened it by+184.864. For drummer10,16 newly covered events improved by−157.277, but the2,608 already-known events worsened by+323.546, plus18 still-unseen events worsened by+24.289. Coverage and redistribution within known outcomes both matter.

## Sharing is not exact-outcome coverage

The quotient/residual model assigned mass as follows to the same fixed outcome sets:

| Set | Training12 | Training35 |
|---|---:|---:|
| Old-seen IOIs | 0.968170 | 0.978543 |
| Newly-seen IOIs | 0.011949 | 0.008051 |
| Still-unseen IOIs | 0.019881 | 0.013406 |

These global factorized probabilities do not depend on previous-instrument context. They share quotient and residual counts, so an exact outcome gaining a direct observation does not guarantee that its product probability increases. Drummer9's83 newly-seen events worsened quotient/residual total NLL by+39.485; its137 still-unseen events worsened by+79.199. Drummer10's main quotient/residual loss was on already-known events (+146.800 total nats).

The factorized model's smoothing is applied to components and legally truncated residual support; it is not the same posterior update as the exact-IOI uniform prior. Context variants also change local/global/prior weight ratios as local counts grow. The report lists those component coefficients rather than equating all models' nominal “prior1” with one shared effective joint prior strength. The final quotient bucket still admits only residual0. Coarse IOI/remainder is not a detected beat position or annotated microtiming effect.

## Denominators and verification

All six conditions, all eight recordings and four drummers are retained. Validation drummer7/8 contribute160/2,598 events; test drummer9/10 contribute1,208/2,642. Each drummer has two recordings. Separate partitions cover global/local exact-IOI novelty, global/local quotient novelty, residual novelty and context exposure/support changes. Each dimension independently partitions all events; never add contributions across overlapping dimensions.

Repeat reports match after excluding CPU time only (approximately4.35/2.00 seconds). Separate verification checked518 mass and aggregation identities, including the closed-form unigram unseen mass. Synthetic tests compare the complement calculation against full30,721-outcome enumeration. These local timings are not a speed comparison. Source hashes and historical roles are unchanged.

Content, performer, style, length, instrument usage, exact-tick variability and effective prior strength are confounded. This bookkeeping explains mathematical contributions, not causal musical or performer differences, population robustness or listener appeal. Any follow-up smoothing ablation requires a separate pre-run plan. Newly reserved recordings being prepared elsewhere are not read or scored here.
