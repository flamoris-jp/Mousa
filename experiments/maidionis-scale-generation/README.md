# Mandatory scale rules in actual saved-model generation

This is the native inference path for the saved pitch/rhythm encoder from
[PR #17](https://github.com/flamoris-jp/Mousa/pull/17), adapted from
[PR #18 at ce10fd62](https://github.com/flamoris-jp/Mousa/tree/ce10fd62acb0e002787c6f808df8bb145878dfff/experiments/maidionis-checkpoint-generation).
Historical PR #14/#17/#18 evidence remains unchanged. No training is required
to enforce a scale, and no scale MIDI is admitted as a learned rule.

The scale/key request is mandatory. Every next-pitch support is the intersection
of the scale's exact integer-semitone degrees, the 48..84 pitch range and the
maximum +/-12-semitone step. The decoder normalizes logits over that support
before sampling. Forbidden classes have exactly zero probability even if their
raw logits dominate. Empty support/nonfinite input fails; there is no snapping,
unconstrained retry or fallback. Every chosen interval is appended to model
history before the next actual Core forward call.

The Python wrapper independently verifies condition identity/digest, model
pins, every event's scale membership, exact allowed labels, zero forbidden
probability, normalization, full history recurrence, timing and all three seeds.
It retains private traces and a verification report; it does not mutate an open
Cantabile project or promote a model. These raw proposals still need the
separate similarity/copy and MIDI-export gates from the generation workflow
before delivery or audition. A scale constraint is not a musical-quality or
originality guarantee.

## Supported checkpoint and limits

- External unmodified Maidionis Core `c288e92979d5005742a1bc3f86b389eadbc873d3`.
- Manifest SHA-256 `123c378362a73c4e2ff54da539fa47b4ebabbd29afc2767d540b751cc36bd4db`.
- Weights SHA-256 `34dd1e168367a12390d2b10c1bf534459c24413a8460e74555da63b625d5d7f7`.
- Actual CPU encoder: 256 hidden, 4 layers/heads, FFN 1024, vocabulary 77,
  49 outputs, task control 1=pitch interval, 2=rhythm, past eight event pairs.
- Fixed seeds 101/102/103, synthetic non-emitted primer, 8 bars, 100 BPM,
  4/4, PPQ480, 15,360 ticks, <=128 events, fixed velocity80 and 90%-gap gates.
- This historical semitone-only model rejects microtonal definitions, tonic
  micro-offsets and alternate concert tuning. The generic scale definitions
  retain these values, but are not silently reinterpreted by the old model.
- No optimization, dataset reads/expansion, new evaluation cohort, GPU,
  model-weight update or production service is involved.

## Build and invoke

Use the CPU Torch2.5.1, CMake3.31.6, nlohmann_json3.12.0, GCC14.2 C++20
toolchain and a clean external Core checkout at the exact commit above.
No Core source is copied into Mousa.

```sh
TORCH_PREFIX=$(python -c 'import torch; print(torch.utils.cmake_prefix_path)')
JSON_INCLUDE=$(python -c 'import nlohmann_json; print(nlohmann_json.get_include())')
cmake -S experiments/maidionis-scale-generation -B build/scale-generation \
  -DMAIDIONIS_SOURCE=/path/to/pinned/Maidionis \
  -DCMAKE_PREFIX_PATH="$TORCH_PREFIX" -DNLOHMANN_JSON_INCLUDE_DIR="$JSON_INCLUDE" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE='-O0 -g0'
cmake --build build/scale-generation --target generate_scale_checkpoint scale_rule_tests -j1
build/scale-generation/scale_rule_tests
PYTHONPATH=src python -m mousa.scale_generation \
  --binary build/scale-generation/generate_scale_checkpoint \
  --checkpoint /private/verified-v2-checkpoint \
  --scale ryukyu_12tet --key D4 --out /private/new-scale-generation
```

Checkpoint files must have trusted provenance and the exact pins; hashes do
not make untrusted native archives safe. The output directory must be new.
Native loading is CPU-only; the wrapper enforces a 90-second wall timeout and
the native loop a 60-CPU-second limit. The first emitted pitch is the requested
tonic. The scale is a strict rule outside model learning, while the model still
chooses pitch/rhythm within allowed support.

The lightweight native `scale_rule_tests.cpp` does not need Torch and is run
in CI. It tests all twelve tonic classes, two scales and every valid current
note in range (444 supports), with deliberately dominant off-scale logits,
plus six rejection cases. Python tests include required-condition enforcement,
microtone refusal before model startup, changed-condition rejection, forbidden
probability leakage and stale-history rejection. Full saved-weight inference
acceptance is recorded in `verification.json`.

## Measured integration acceptance

The actual pinned v2 model generated all five integer-semitone catalogue scales
at C4 and D4, three fixed seeds per condition: 10 conditions, 30 candidates,
1,622 emitted notes. Every note was in the requested scale; every forbidden
class had exactly zero probability. Independent Python checks recomputed the
masked softmax from raw model logits, the sampling choice from each recorded
RNG word, and complete history/event recurrence. One complete three-seed
condition replay matched exactly except CPU time. Model weights stayed
byte-identical. No retraining or source-corpus read was needed.

58 Python tests ran: 57 passed, one existing external producer integration was
skipped. Native adversarial tests covered 444 supports and six failures; five
additional invalid native requests were rejected before checkpoint loading.
Microtonal scales were among the explicit rejections. These are constraint and
integration results, not music-quality, originality or generalization evidence.
