# Post-merge exposure-matched baseline audit

## Question

PR #14 is merged at `a5a924854c2b1c2f5156e74fffc2f804166112b8`.
Its encoder was worse than the trigram using every available training window.
However, that count baseline saw 4,084 distinct windows while the encoder sampled
3,200 observations **with replacement**. Is the ranking robust to this exposure difference?

This is a frozen-protocol **retrospective diagnostic** of existing measurements,
not a new neural fit or a fresh generalization test. The protocol was committed
before the new exposure-matched count fits. Every originally recorded condition
and seed is included; no validation/test selection or hyperparameter tuning.

## Procedure

1. Download the exact private evidence archive recorded in PR #14 and verify its SHA-256.
2. Run main's digest-checked `replay_evidence.py`, reproducing all original native
   inputs, six count baselines and recorded summaries exactly.
3. For each of three conditions and seeds 42/43/44, fit unigram and hierarchical
   trigram using (a) every unique window, (b) precisely the 3,200 recorded sampled
   observations, including repeated occurrences, and (c) unique windows among
   those sampled observations. Keep historical smoothing unchanged.
4. Score the same 16 previously observed families / 512 targets. Report
   family-macro natural-log NLL, accuracy and all family differences. Family
   identities and per-window predictions stay in private storage.

No source admission, role reassignment, new labels, SA use, neural fitting,
MIDI generation or Cantabile changes. This reuses prior rights-cleared derived
PD/BY windows, not a new independent legal audit of raw MIDI.

## Results: 128-family ordered arm

NLL is lower-is-better; each column uses the same test cohort.

| Seed | All 4,084 windows trigram | Actual 3,200 observations trigram | Sampled unique-only trigram | Recorded encoder |
|---|---:|---:|---:|---:|
| 42 | 3.02757 | 3.43281 | 3.28216 | 3.17993 |
| 43 | 3.02757 | 3.28708 | 3.18935 | 3.08012 |
| 44 | 3.02757 | 3.25652 | 3.15285 | 3.15279 |

The encoder actually encountered **2,231 / 2,213 / 2,221 distinct windows**,
roughly 54% of those available. Under actual sampled-observation exposure,
the trigram's average NLL is worse than the encoder for all three seeds.
Under sampled-unique-only exposure, the third seed is effectively tied
(difference about 0.000054), not a robust margin.

**Negative and qualification:** accuracy does not reverse consistently. With
actual sampled observations, the trigram is correct on 20.51%, 19.73%, 23.83%;
the encoder on 15.82%, 19.73%, 18.95%. The trigram therefore still equals or
beats encoder top-1 accuracy in all three ordered 128-family runs. It also
has lower NLL on 6, 5 and 6 of the 16 individual families respectively.

The earlier all-data trigram result remains correct and is not removed.
These results show that the model ranking depends on **exposure protocol and
metric**. They do not establish that either model is universally superior,
that the encoder can compose attractive music, or that the smaller/more
repetitive corpus is equivalent to a larger repertoire.

Repeated counts sharpen count-model probabilities under the same fixed smoothing;
unique-only controls separate this weighting effect from omitted windows. Equal
observations do not mean equal compute, capacity, optimization, or learning dynamics.
The full 54-condition results are in `summary.json`, including 18-family and
context-permuted counterchecks. Previously observed test data must not be called
fresh again. No confidence interval across 512 allegedly independent notes is claimed.

## Reproduce

From repository root, first run the existing PR #14 evidence replay into a new
private directory. Then:

```sh
python experiments/maidionis-exposure-audit/audit.py \
  --replay /path/to/private/replayed \
  --out /path/to/new-private-audit
PYTHONPATH=src python -m unittest discover -s tests -v
```

The output contains derived private predictions and family IDs; keep it outside
Git. Input and prediction digests are enforced. Output directory must not exist.
All-data ordered counts reproduce the historical baseline. The two new complete
runs of this audit produced byte-identical summaries and per-window predictions.
Bootstrap suite: 39 tests, 38 passed, one existing optional AudioAnalyzer skip.

An independent implementation recomputed all 27,648 prediction rows and 54
summaries with zero numeric discrepancy, and checked exposure identities,
labels, source-evidence digests and family separation. Private results are saved
in LIME Files `assets/mousa/materials/metadata/maidionis-exposure-audit-20261115-evidence.zip`.
The initial evidence archive SHA-256 is
`0b6226c68ee1ac8344605d9a1141eaf31f36161678d07922e14d7d11ed9d9fe9`
(320,312 bytes). It contains the executed script/plan, full per-family and
per-window results and input replay receipt; its README predates this storage
receipt paragraph. No raw MIDI or weights included.
