# Maidionis order-sensitive learning diagnostic

Executed 2026-11-14 UTC (2026-11-15 JST). This is a tiny synthetic architecture diagnostic, **not MIDI training, musical-quality evaluation, a full Core education lifecycle acceptance, or a replacement for corpus training**.

## Question and frozen design

Does actual Maidionis learn a target that requires preserving token order? The unmodified [Core](https://github.com/flamoris-jp/Maidionis/tree/c288e92979d5005742a1bc3f86b389eadbc873d3) is linked externally, not copied into Mousa. The native harness calls its `Model`, `categorical_loss`, constraints and archive API, with a small diagnostic AdamW loop.

Inputs are `[CLS, a, b]`, IDs 2–9; target is whether a < b. Eight IDs produce 28 unordered pairs; a deterministic SHA-256 ranking assigns 20 pairs (40 orientations) to train and 8 pairs (16 orientations) to held-out test. Reverse siblings never cross splits. All token IDs occur in training. No external copyrighted material is used. These original symbolic fixtures are under the repository Apache-2.0 license.

Plan/dataset were frozen before execution: seeds 42/43/44, 100 full-batch steps, learning rate 0.0003, zero dropout/weight decay, clipping 1.0, final step only. No test-driven tuning. `plan.json` and `dataset.json` hashes are in `verification.json`.

## Results

| Model | Seed | Train accuracy | Held-out accuracy | Held-out NLL, initial → final |
|---|---:|---:|---:|---:|
| pooled |42|50%|50%|see full results → 0.69385|
| pooled |43|50%|50%|see full results → 0.69328|
| pooled |44|50%|50%|see full results → 0.69335|
| encoder |42|100%|81.25% (13/16)|0.823 → 1.592|
| encoder |43|100%|81.25% (13/16)|0.686 → 1.972|
| encoder |44|100%|75% (12/16)|0.715 → 2.539|

**Negative result: encoder held-out NLL worsened for every seed**, even though accuracy rose. It is confidently wrong on some unseen pairs. This establishes ability to fit order-sensitive training targets, not reliable generalization/calibration. The 16 test orientations comprise only 8 independent pair families; seeds are not additional independent data.

Pooled gives exactly identical logits to each reversed pair. Its content-embedding mean discards order, hence balanced reverse labels force exactly 50% deterministic accuracy regardless of more training. Parameters still changed and loss reduced to approximately ln(2): it did train, but cannot represent this target with these raw inputs. This does **not** apply to every possible position-encoded upstream representation or every Maidionis model.

Encoder retains positional information. It has 3,228,674 parameters versus pooled's 68,866, so this is not a parameter-matched causal architecture ranking. Token-ID comparison is an artificial relation with seen vocabulary, not musical order, melody generation or semantic understanding.

## Verification and cost

- Actual native Core model contract tests passed.
- Mousa baseline unit tests: 28 run, 1 skipped, no failures.
- All gradients finite, positive parameter changes; full losses/predictions included.
- In-memory archive save/reload gave bit-identical test logits for all six runs.
- Repeated entire six-run experiment: all JSON values identical excluding CPU time.
- First six-run fit/evaluation: 17.175 CPU seconds, one thread, FP32, no GPU. Compilation/setup time excluded. No paid operations.
- Environment and package versions are recorded; C++ build uses GCC14.2, LibTorch2.5.1 CPU, Release with `-O0 -g0`.

## Reproduce

Requires an external clean Maidionis checkout at the pinned SHA, Python3.12, a C++20 compiler, CMake3.31.6, nlohmann_json3.12.0 headers and CPU PyTorch2.5.1. No changes to upstream Core are required.

```sh
python -m venv .venv
.venv/bin/pip install torch==2.5.1+cpu --index-url https://download.pytorch.org/whl/cpu
.venv/bin/pip install cmake==3.31.6 nlohmann_json==3.12.0
TORCH_PREFIX=$(.venv/bin/python -c 'import torch;print(torch.utils.cmake_prefix_path)')
JSON_INCLUDE=$(.venv/bin/python -c 'import nlohmann_json;print(nlohmann_json.get_include())')
.venv/bin/cmake -S experiments/maidionis-order-toy -B build/order-toy \
  -DMAIDIONIS_SOURCE=/path/to/pinned/Maidionis \
  -DCMAKE_PREFIX_PATH="$TORCH_PREFIX" -DNLOHMANN_JSON_INCLUDE_DIR="$JSON_INCLUDE" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE='-O0 -g0'
.venv/bin/cmake --build build/order-toy --target order_diagnostic maidionis_model_tests -j1
build/order-toy/core/maidionis_model_tests
build/order-toy/order_diagnostic experiments/maidionis-order-toy/dataset.json \
  experiments/maidionis-order-toy/plan.json /tmp/order-results.json
```

`prepare.py` regenerates frozen plan/data in an empty directory (uses exclusive creation to prevent accidental overwrite). Commands express the tested configuration with portable paths, not an automated dependency installer integrated into Mousa.

## Next useful experiment

Train a small actual music-token task against fixed unigram/ngram controls, preserving order and held-out work families. Use train/dev for any learning-rate/step selection; never choose an epoch from this observed test. Measure calibration/NLL as well as accuracy and retain negatives. Corpus size alone cannot repair order erased by the representation. No architecture switch, main merge, deployment, MIDI generation or Cantabile update was performed here.
