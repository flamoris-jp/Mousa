# Prospective complete-coverage diagnostic controls

This preparation fixes the next experiment before fitting: every one of the
4,084 existing training windows is encountered exactly once, rather than 3,200
replacement draws. Six arms pair ordered and per-row context-permuted inputs for
seeds42/43/44. Both models will use the identical observations. Count smoothing
and the native encoder configuration remain fixed by `plan.json`.

**Preparation only:** this directory currently records no new fitting, predictions
or musical-quality result. Its unchanged512-target/16-family evaluation cohort
was already observed in Cycle53 and PR14. It is not a fresh confirmation set.
Reuse is restricted to the hash-pinned PR14 PD/BY derived windows; no raw MIDI,
SA data, newly admitted work or family reassignment is introduced.

## Prepare

After verifying/replaying the original PR14 private evidence:

```sh
python experiments/maidionis-coverage-control/prepare.py \
  --source /private/replayed/data.json --out /private/new-coverage
PYTHONPATH=src python -m unittest discover -s tests -v
```

Outputs contain private family IDs and symbolic windows and must stay outside
Git. Preparation verifies the source digest, row identity, labels/token ranges,
family separation, historical cohort sizes and equal historical training rows.
It refuses existing output directories. It preserves CLS, identities, labels and
context multisets under permutation, checks exact-once coverage, and writes a
receipt with data, code and plan hashes. Paired ordered/permuted schedules are
identical. Two complete preparations were byte-identical. Test suite:44 run,
43 passed, one existing optional integration skip.

The planned downstream runner is the **unchanged** PR14 native diagnostic,
using external Core at the pinned commit, one CPU thread and its300CPU-second
ceiling. Its current100-step history must not be mistaken for this128-step
protocol: this experiment uses127 batches of32 and a final batch of20. This
changes optimizer horizon and last-batch weighting, so a difference from PR14
would not isolate a pure causal coverage effect. Equal exposure is not equal
compute/capacity. No stopping, model selection or smoothing tuning may use this
already-observed evaluation set.
