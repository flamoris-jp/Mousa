# Actual Maidionis MIDI interval diagnostic

This bounded CPU experiment fits the actual, unmodified Maidionis encoder at commit `c288e92979d5005742a1bc3f86b389eadbc873d3`. No Core code is copied into Mousa. It uses a small native diagnostic optimizer calling Core Model/loss APIs, **not the full production education pipeline**.

## Fixed protocol and data

Reuse the rights-checked Cycle53 split, with no role changes. All 16 test work-families were **already observed in Cycle53**: this is a regression/architecture diagnostic, not a fresh held-out confirmation. No validation/test tuning or epoch selection.

SHA-ranked nested training subsets:18 families /567 windows versus128 families /4,084 windows. Test16 families /512 windows. Each family contributes at most32 evenly spaced target windows among its first2,048 projected onsets. Three fixed seeds42/43/44,100 optimizer steps,batch32,AdamW0.0003,no weight decay/dropout,clip1. Same initialization and sampled batch indices in128 ordered/permuted arms. Equal3,200 sampled training targets per run, but fewer repetitions per available window in128. Dataset amount is confounded with repertoire; this does not identify a pure causal song-count effect.

Input:CLS+8 preceding pitch-interval tokens. Output:next pitch interval49 clipped classes. Highest non-drum pitch at each exact onset is a **projection, not an annotated melody**; duration, dynamics, lower simultaneous voices, tempo and instrumentation are discarded. Intervals clipped±24 semitones. Sources PD/CC BY only; SA excluded. Per-source MIDI hashes, attribution, licensing and modification notice in `midi-attribution.json`. The family-ID prefix `ccbysa-combined` is inherited graph nomenclature, **not a statement that the selected sources are SA**.

Controls: untrained initialization; uniform, additive unigram, hierarchical trigram based on identical selected training windows;128-training context permutation preserves labels/token multisets and destroys precise history ordering. For fairness, count baselines see all available unique windows, while neural fitting samples3,200 targets with replacement: exposure is not identical between model classes. Train-size neural arms have equal optimizer steps, not equal exposure per piece.

## Reproduction and provenance

`plan.json` was frozen before native fitting. Original split/evidence hashes and exact selected family IDs are recorded. Preparation verifies raw MIDI SHA, exact-file allowlist and rights eligibility. Private token data is not committed. Full evidence is stored in approved LIME Files metadata storage; no raw MIDI, audio or weights in Git. Original raw materials remain untouched.

### Verify historical evidence without fitting

Obtain the private evidence ZIP identified below through approved storage. It is
not included in Git. Run from the Mousa repository root with Python 3.12:

```sh
python experiments/maidionis-midi-learning/replay_evidence.py \
  --evidence-zip /path/to/maidionis-midi-learning-20261115-evidence.zip \
  --out /path/outside-the-repository/new-midi-replay
```

The output directory must not exist. The verifier checks the ZIP digest and
historical code/plan pins, recreates the exact native `data.json` and all six
count-baseline results, and reaggregates the recorded nine native runs. It
requires exact agreement with the committed summaries. It makes no network
calls and does **not** rerun neural training. Output includes private derived
windows and recorded predictions: keep the entire output outside Git.

Historical scripts and measurements are preserved unchanged. In particular,
`freeze_native_frozen.py` is the hash-pinned generator; its original location
assumption is handled by staging verified inputs in the new output directory.
Do not run it directly in this checkout, where exclusive writes collide with
the recorded `plan.json`. The regenerated plan has a new timestamp and the old
metrics-description wording; it is not a replacement for the archived final
plan. The numeric dataset must match SHA-256
`49ff7ee03687d77d1707d82985266f9b51fa836154a924ef7529873ea9f6171f`.

### Historical native build and fit

The measured build used external pinned Core, CPU Torch2.5.1, GCC14.2,
CMake3.31.6,nlohmann_json3.12.0; C++20,Release `-O0 -g0`,one thread,FP32.
Use a clean external Maidionis checkout at
`c288e92979d5005742a1bc3f86b389eadbc873d3`; verify its revision before building.
For a private checkout, use an authenticated `gh repo clone flamoris-jp/Maidionis`
and select that commit. Core remains an external dependency.

With CPU Torch2.5.1, CMake3.31.6 and nlohmann_json3.12.0 installed in a Python
environment, the native target is configured directly from this PR:

```sh
TORCH_PREFIX=$(python -c 'import torch; print(torch.utils.cmake_prefix_path)')
JSON_INCLUDE=$(python -c 'import nlohmann_json; print(nlohmann_json.get_include())')
cmake -S experiments/maidionis-midi-learning -B build/midi-diagnostic \
  -DMAIDIONIS_SOURCE=/path/to/pinned/Maidionis \
  -DCMAKE_PREFIX_PATH="$TORCH_PREFIX" -DNLOHMANN_JSON_INCLUDE_DIR="$JSON_INCLUDE" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE='-O0 -g0'
cmake --build build/midi-diagnostic --target midi_diagnostic maidionis_model_tests -j1
build/midi-diagnostic/core/maidionis_model_tests
build/midi-diagnostic/midi_diagnostic /path/to/new-midi-replay/data.json \
  /path/to/new-midi-replay/new-results.json
python experiments/maidionis-midi-learning/summarize.py \
  /path/to/new-midi-replay/new-results.json /path/to/new-midi-replay/new-summary.json
```

This is the historical build configuration, not a claim of a fresh native fit
during review or cross-toolchain bitwise compatibility. The related synthetic
diagnostic [PR #13](https://github.com/flamoris-jp/Mousa/pull/13) is background,
not a source-file or merge prerequisite.

`prepare_midi.py` documents the original raw-source preparation. It also
requires external Cycle53 split, evidence, extractor and source files. The
extractor digest is **recorded, not enforced** by that historical script;
compare it with `plan.json` before executing trusted code. Editing paths in
the split changes its pinned hash and is rejected. Raw-source relocation is
not implemented as a portable command here; use the verified derived-window
replay above to recover this experiment's native inputs. A portable raw-source
adapter remains follow-on work under [Issue #3](https://github.com/flamoris-jp/Mousa/issues/3).

Some configuration constants are explicitly fixed in the native harness; editing plan.json alone is not an implemented configurable trainer. CPU guard300seconds over nine runs; each completed run writes partial evidence, so failures do not erase earlier results. The harness checks finite gradients and actual embedding parameter changes. No deployment, main merge, corpus mutation, MIDI generation or Cantabile operation.

## Measured results

Family-macro natural-log NLL (lower better), same512 test windows:

| Condition | Seed42 | Seed43 | Seed44 |
|---|---:|---:|---:|
| Untrained encoder |3.8071|4.2066|3.8828|
|18 ordered encoder|3.4939|3.4212|3.4014|
|128 ordered encoder|3.1799|3.0801|3.1528|
|128 context-permuted encoder|3.3026|3.2130|3.3136|

Uniform NLL3.8918. Same-window18 unigram3.3529,trigram3.5405;128 unigram3.2753,trigram3.0276.

**Actual learning is observed:** all encoder arms improve over their same-seed initialization, all128ordered runs improve over18ordered and128permuted. This is evidence that the encoder can learn predictive features from this MIDI projection, and precise context order helps in this diagnostic. It does not prove more works always help.

**Negative:**128 trigram still outperforms every encoder (NLL3.0276,accuracy24.02% versus encoder15.82–19.73%).18 encoder is worse than18 unigram. Do not claim neural superiority or music-generation success. More varied training reduces the train/test gap here:18 finaltrainNLL1.63–1.92 versus test3.40–3.49;128 finaltrain2.80–2.94 versus test3.08–3.18. This is not an unbiased fresh generalization estimate.

All nine fits/evaluations took115.793CPU seconds excluding build/setup. Finite gradients,100steps/run and positive embedding updates verified. Independent review rechecked row targets/splits, numeric aggregates and shared initial outputs. A separate replay of **first arm only**,18ordered/seed42, is exactly identical excluding runtime; a full nine-arm replay was not performed. No musical attractiveness judgement or generated MIDI.

Full private evidence archive verified in LIME Files `assets/mousa/materials/metadata/maidionis-midi-learning-20261115-evidence.zip` (785,313bytes,SHA256 `7a67cd00707c6bb0d72bc2722572ace8940404fc5e5d7f6e0d201b991e7851b3`). Includes private extracted windows, exact predictions/losses, attribution and scripts, but no raw MIDI/audio/weights or machine-specific paths. Derived windows plus the frozen generator reproduce the native dataset; native data hash is recorded rather than repeating all9arms in archive.

`freeze_native_frozen.py` preserves the exact frozen script SHA. `freeze_native.py` differs only by correcting the metrics-description text to initial/final test plus finaltrain; it did not change any numeric dataset or outcomes. Frozen finalplan was corrected before fitting. The earlier4condition plan was superseded before outcomes and is retained in private evidence.

## Review verification (2026-11-15 JST)

The private ZIP digest, regenerated native data, six regenerated count baselines
and exact reaggregation of all nine recorded runs were verified during review.
Recorded prediction row identities/targets, finite losses, update evidence and
selected-source split separation were also checked. The bootstrap suite ran
33 tests: 32 passed and the existing external AudioAnalyzer integration was
skipped. No fresh neural fit, native build, raw-source rights re-audit or
musical-quality test was performed in this review. See
`review-verification.json`. This research record contributes to
[Issue #4](https://github.com/flamoris-jp/Mousa/issues/4); it does not complete
specialist lifecycle or music-generation acceptance.
