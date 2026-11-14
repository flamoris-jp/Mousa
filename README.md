# Mousa 🎼

**Music is learned. Creativity emerges.**

Mousa is FLAMORIS's music-intelligence research project built on [Maidionis](https://github.com/flamoris-jp/Maidionis). It develops several small, separately educated musical specializations in **one repository**, with the long-term goal of proposing, evaluating, revising, and exporting original MIDI compositions.

**Mousa（ムーサ）** は、Maidionis を学習基盤として音楽特化の小さなAIを育て、協力してMIDIを作曲する FLAMORIS の研究プロジェクトです。旋律・和声・ベース・ドラム・編曲・評価を同じリポジトリで管理します。

**Status: early development / research bootstrap.** This repository currently contains project boundaries, specialization plans, an experimental Python MusicIR value representation, reviewed AudioAnalyzer stem-candidate intake, and an offline research-manifest preflight with unit tests. **It does not yet ship** a trained Mousa model, MIDI importer/exporter, dataset crawler, preference-learning system, model-serving API, or Cantabile integration. An earlier local music trial is not included until its source, licensing, and measured evidence are verified for migration.

## 🧭 Repository identity

### What Mousa owns / 主な責任範囲

- Music-specific curricula, feature representation, MIDI analysis/ingestion rules, and provenance of teaching materials.
- Six music-specialized model families: **Melody**, **Harmony**, **Bass**, **Drums**, **Arrangement**, **Critic**.
- Music-specific evaluation: structure, variety, novelty, meaningful phrase development, and preference feedback, each reported separately.
- Reproducible music experiments, measured results, known failures, and model-specific artifacts and contracts.

### What Mousa does not own / 持たない責任

- **Maidionis Core** owns generic training, checkpointing, evaluation infrastructure, artifact and inference-envelope mechanisms. Do not vendor or fork its general-purpose Core into Mousa.
- **FLAMORIS AI Runtime** owns Workflow execution, resource scheduling, retries, shared execution state, and calls to tools. Mousa models return bounded music proposals, not actions.
- **Cantabile** owns editable MIDI projects, note/event editing, rendering, and MIDI/WAV export. Mousa is not a second MIDI editor.
- **Suno/DAWs** own their separate arrangements, instruments, and vocals; Mousa does not claim those abilities.

See [architecture](docs/ARCHITECTURE.md), [roadmap](docs/ROADMAP.md), and [data policy](docs/DATA_POLICY.md).

## Musical specializations

| Model | Intended role |
| --- | --- |
| [Mousa Melody](specializations/melody/README.md) | Motifs, phrases, melody continuation and transformation |
| [Mousa Harmony](specializations/harmony/README.md) | Harmonic suggestions and progression |
| [Mousa Bass](specializations/bass/README.md) | Bass movement, harmony and groove relationships |
| [Mousa Drums](specializations/drums/README.md) | Beats, accents, swing and rhythmic variation |
| [Mousa Arrangement](specializations/arrangement/README.md) | Sections, contrast, transitions and energy |
| [Mousa Critic](specializations/critic/README.md) | Structural analysis, candidate comparisons and learned preferences |

These are **planned specialization boundaries**, not claims of six working trained models. Melody and Critic are natural first experiments; Drums is also a useful bounded creative proof for Maidionis.

## Proposed workflow

```text
MIDI sources with verified rights and provenance
  -> validation / de-duplication / piece-level split
  -> analysis + musical representations
  -> Maidionis-based specialization training
  -> bounded candidate notes/arrangements
  -> Runtime-controlled collaboration and review
  -> Cantabile editable project / MIDI / WAV
  -> human comparison and revisions -> preference examples
```

Musical correctness, musical features, human preference, and music similarity/copying risk must be measured separately. The Critic is **not** an objective judge of artistic value. Dataset licenses, source hashes, rights, rejection reasons and held-out evaluation must be retained.

## Repository layout

```text
src/mousa/            Experimental MusicIR Python representation
specializations/      Melody / Harmony / Bass / Drums / Arrangement / Critic plans
docs/                 Architecture, roadmap and dataset policy
datasets/             Dataset manifests and policies only; no unapproved corpus
training/             Future music-specialization education compositions
evaluation/           Evaluation rubrics and baselines
experiments/          Reproducible music experiments (not generated assets)
tests/                Fast local tests
```

## Development / 開発

For the current fast unit tests, Python 3.11+ is sufficient; no Maidionis native build, MIDI dependency or GPU is required to run these tests.

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

This command validates MusicIR, stem-intake guards and research-manifest preflight; optional real AudioAnalyzer integration requires its separate environment. It does **not** test training, parsing a real MIDI file, or audio quality. Do not reuse Maidionis build commands without checking its current repository and qualification profile.

Next work is tracked in [GitHub Issues](https://github.com/flamoris-jp/Mousa/issues). See [Maidionis](https://github.com/flamoris-jp/Maidionis), [Cantabile](https://github.com/flamoris-jp/flamoris-cantabile), [AI ecosystem](https://github.com/flamoris-jp/flamoris-ai/blob/main/docs/ai-ecosystem.md), and [FLAMORIS organization map](https://github.com/flamoris-jp/.github).

## Licensing and contribution

Code is licensed under [Apache License 2.0](LICENSE) unless otherwise stated. **Code licensing does not grant rights to MIDI compositions, arrangements, soundfonts, recordings, source datasets, or trained weights.** Record their provenance and license separately. Never commit private source material, credentials or unreviewed third-party MIDI. See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [AGENTS.md](AGENTS.md).

FLAMORIS is open-source creative software. Use it, modify it, and make something interesting. Support is community/self-directed and provided as-is. 🌱

## Adaptive research

See [the adaptive protocol](docs/ADAPTIVE_RESEARCH.md) for hypothesis-driven work,
rights and split preflight, resource bounds, evaluation and stop conditions.
The November 2026 window is for repeated research cycles, not one task per day.
The [preparation record](experiments/2026-11-12-preparation.md) separates tests
actually run from historical results and unexecuted work.
