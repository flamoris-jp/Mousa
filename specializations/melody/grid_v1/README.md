# Mousa Melody: recovered grid-v1 experiment

Music-specific code recovered from `Maidionis_Music_Trial_001.zip`, now composed against an **external, exact, clean Maidionis checkout**. Generic Core code and old weights are not vendored. See [source lineage](../../../experiments/trial001-recovery.json) and [acceptance evidence](../../../experiments/README.md).

## Scope

Input: the previous eight sixteenth-grid tokens and position modulo 16. Vocabulary: REST, HOLD and 25 pitches (MIDI 60..84). Output: the next token. A dense 232 -> 64 -> 27 model has 16,667 trainable parameters. Dataset identity is not a feature. The original task ID, `research.music-next-token` v1, is retained.

The three sources are explicitly selected vocal tracks, not automatically extracted top notes. The frontend rejects polyphony, unsupported meter, off-grid timing, out-of-range melody, ambiguous note pairing, drum channels, pitch bends and active sustain/sostenuto. It preserves initial rests and same-pitch rearticulation. A single recorded transposition normalizes each melody; it does not clamp pitches.

This is a narrow preprocessing profile, not a general lossless MIDI importer. Tempo maps, controllers, accompaniment and dynamics are not learned. The standalone MIDI writer and sine preview are research outputs, not Cantabile integration.

## Setup

Run from the Mousa repository root in a separate research environment. Do not alter a production ROCm installation to match this CPU-only reference profile. Required: Linux x86_64, C++20 compiler, OpenSSL development headers and Python 3.12.

```bash
gh auth status
mkdir -p .deps
gh repo clone flamoris-jp/Maidionis .deps/Maidionis
git -C .deps/Maidionis checkout --detach a987eeeea11e3971d3b9708bfff6b3545cdb601f

python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r .deps/Maidionis/tools/dependencies.txt -r specializations/melody/grid_v1/requirements.txt
python -m pip install --no-deps --no-build-isolation .deps/Maidionis

export MOUSA_MAIDIONIS_ROOT="$PWD/.deps/Maidionis"
export MOUSA_TRIAL_CORPUS="$PWD/.cache/trial001-corpus"
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
```

If GitHub CLI is not authenticated, use `gh auth login`, then repeat the clone as that user, not with sudo. When reusing an existing checkout, verify it is clean and at the exact commit rather than cloning over it.

## Curated source preparation

An explicit command downloads only three exact URLs from the committed [source catalog](../../../datasets/trial001-sources.json), enforcing SHA-256 and size limits and rejecting redirects. No model initiates downloads.

```bash
python tools/prepare_trial_corpus.py --output "$MOUSA_TRIAL_CORPUS"
```

For offline recovery, add `--source-dir /path/to/recovered/specializations/music/corpus`. The same hashes are checked. Paths are illustrative local choices, not deployment defaults. Each output directory must be new; existing evidence is never intentionally replaced.

The generated license evidence files are transparent **review records**, not copies of the original website HTML. Consequently the frozen dataset digest differs from the original archived experiment even though the source MIDI bytes and token sequences are identical. Do not use the old digest with a new run.

## Unit tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python -m unittest discover -s specializations/melody/grid_v1/tests -v
```

The first command runs the 9 MusicIR tests. The second runs 22 recovered music tests, including source byte/evidence hashes, whole-work split isolation, transposed duplicates and forged target/provenance rejection. These are not listening tests.

## Train, reload and generate

```bash
python specializations/melody/grid_v1/experiment.py \
  --corpus "$MOUSA_TRIAL_CORPUS/manifest.json" \
  --output runs/trial001 \
  --build-dir build/melody-grid-v1 \
  --epochs 30

python tools/verify_trial_native.py \
  --driver build/melody-grid-v1/maidionis_music_driver \
  --run runs/trial001
```

The experiment builds the native composition and calls Maidionis's real numerical engine. It freezes source-derived labels, preregisters settings, performs 30 epochs with seed 42 and dev selection, exports a research checkpoint, loads it in fresh processes, reports train/dev/test and baseline metrics, and generates two 8-bar candidates from a supplied four-note primer.

The verification command is for a **30-epoch** run. It checks parameter updates, sample counts, deterministic generation, rejected wrong export pin, rejected modified weights, and exact state/final/best-weight equality between 30 continuous epochs and a fresh-process 2+28 resume. It creates a new `verification/` directory and refuses an already-used destination.

Outputs include `report.json`, `preregistration.json`, `training-summary.json`, `native-verification.json`, `candidate-01.mid`, `candidate-02.mid`, their neutral WAV previews and sampling records. Keep raw corpus, checkpoints and previews out of normal Git commits. The [native CI workflow](../../../.github/workflows/melody-grid-v1.yml) performs the same sequence and retains reports/previews for a limited period.

## Interpretation

The fixed split is one distinct work each: 648 train windows, 248 dev windows, 248 test windows. Those public works were already inspected in the original trial, so this is a mechanics reproduction, not a new sealed evaluation. Most labels are HOLD; report note-onset performance separately. A high continuation accuracy, a finite loss or two valid MIDI files does not establish attractive or original music.

The research export is hash-bound and requires trusted source provenance. It is **not** a production Maidionis serving artifact or a safe loader for arbitrary untrusted native archives. No Runtime host, GPU qualification, Critic, multi-specialist coordination, human preference learning or Cantabile edit path is provided.

## Migration attribution

The recovered music code is Apache-2.0. This migration changes dependency lookup, explicit corpus/build paths and test wiring; the numerical task is preserved. Changes are recorded here and in the source-lineage inventory. Copyright and license notices from upstream must be retained. Individual MIDI sources and future published weights/media require their own recorded terms.
