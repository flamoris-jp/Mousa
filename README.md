# Mousa 🎼

**Music is learned. Creativity emerges.**

Mousa is FLAMORIS's music-intelligence research project built on [Maidionis](https://github.com/flamoris-jp/Maidionis). Several small musical specializations share **one repository**, with the long-term goal of proposing, evaluating and revising editable MIDI compositions.

**Mousa（ムーサ）** は、Maidionisを学習基盤として音楽特化の小さなAIを育てるFLAMORISの研究プロジェクトです。旋律・和声・ベース・ドラム・編曲・評価を同じリポジトリで管理します。

**Status: early development / offline research.** The first [Mousa Melody experiment](specializations/melody/grid_v1/README.md) now has a curated three-work MIDI intake, a native Maidionis training composition, checkpoint reload, next-token evaluation, and MIDI/neutral WAV generation code. [Recovery evidence](experiments/trial001-recovery.json) distinguishes the earlier verified archive from new execution; the [native CI workflow](.github/workflows/melody-grid-v1.yml) performs fresh training and resume/tamper checks. This is not a production-trained music model or evidence of musical appeal.

**現在：Mousa Melodyのオフライン学習実験。** 前回の実験ソースを復元し、出典とハッシュを確認した3曲を教材として、学習・保存・再読込・MIDI生成を再実行する経路を実装しています。魅力の自動判定、好みの学習、他の専門モデル、Runtime常駐、Cantabile連携は未実装です。

## 🧭 Repository identity

### What Mousa owns / 主な責任範囲

- Music-specific tasks, curricula, symbolic representations, source provenance and model compositions.
- **Melody, Harmony, Bass, Drums, Arrangement and Critic** within one repository.
- Music-specific evaluation, preference examples and reproducible experiments, including failures.

### What Mousa does not own / 持たない責任

- **Maidionis Core** owns generic numerical training, checkpointing, evaluation infrastructure and artifact/inference contracts. Core remains an external pinned dependency; it is not copied into Mousa.
- **FLAMORIS AI Runtime** owns execution, scheduling, retries, shared workflow state and tool authority. Models return proposals, not actions.
- **Cantabile** owns editable MIDI projects, event editing, instrument rendering and production export. A standalone research MIDI writer does not replace its project authority.
- External DAWs and vocal/arrangement services own their respective instruments and vocals.

See [architecture](docs/ARCHITECTURE.md), [roadmap](docs/ROADMAP.md), [data policy](docs/DATA_POLICY.md), and [research evidence](experiments/README.md).

## Musical specializations

| Specialization | Intended role | Current scope |
| --- | --- | --- |
| [Mousa Melody](specializations/melody/README.md) | Motifs, phrases and melody development | Recovered bounded next-token experiment |
| [Mousa Harmony](specializations/harmony/README.md) | Chords and harmonic relationships | Planned |
| [Mousa Bass](specializations/bass/README.md) | Bass movement and groove | Planned |
| [Mousa Drums](specializations/drums/README.md) | Beats, accents and rhythmic variation | Planned |
| [Mousa Arrangement](specializations/arrangement/README.md) | Sections, contrast and transitions | Planned |
| [Mousa Critic](specializations/critic/README.md) | Features, comparisons and preferences | Planned |

A next-token predictor is not the Critic. No aesthetic labels or human preference learning are included in Trial 001.

## Implemented research path

```text
Three reviewed source identities + exact MIDI hashes
  -> chosen monophonic track / exact sixteenth grid / explicit transposition
  -> separate works for train, development selection and test diagnostics
  -> external pinned Maidionis native model and training engine
  -> checksum-bound offline research export / fresh-process load
  -> next-token metrics + simple baselines + note-onset metrics
  -> two 8-bar MIDI candidates and neutral synthesized previews
```

This deliberately small task uses the previous eight grid steps and a position within the bar. It does not learn whole-song form. Source selection is based on recorded terms and representation compatibility, **not musical attractiveness**. The three already-public works are reproduction diagnostics, not a sealed benchmark. Similarity checks are diagnostic, not a legal or originality guarantee.

Future Runtime-controlled collaboration and Cantabile handoff remain distinct work.

## Development / 開発

The original MusicIR value-object tests need only Python 3.11+:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

These tests do not test native training. For the tested-profile setup, curated MIDI preparation, 22 music regression tests, 30-epoch experiment and fresh-process verification, use the [Melody experiment guide](specializations/melody/grid_v1/README.md). The native profile requires Linux x86_64, Python 3.12 and LibTorch 2.5.1+cpu. GPU and deployment acceptance are not implied.

## Repository layout

```text
src/mousa/                       Experimental note-only MusicIR values
specializations/melody/grid_v1/  Recovered melody research composition
specializations/                 All six specialist task boundaries
datasets/                        Reviewed source catalog and policies, no raw MIDI
tools/                           Explicit corpus preparation and native verification
evaluation/                      Evaluation boundaries and future specialist rubrics
experiments/                     Source lineage and evidence, not model checkpoints
docs/                            Architecture, roadmap and dataset policy
tests/                           Fast MusicIR tests
```

Next work is tracked in [Issues](https://github.com/flamoris-jp/Mousa/issues). Related projects: [Maidionis](https://github.com/flamoris-jp/Maidionis), [Cantabile](https://github.com/flamoris-jp/flamoris-cantabile), [AI ecosystem](https://github.com/flamoris-jp/flamoris-ai/blob/main/docs/ai-ecosystem.md), [FLAMORIS organization map](https://github.com/flamoris-jp/.github).

## Licensing and contribution

Code is [Apache-2.0](LICENSE) unless stated otherwise. Code licensing does not grant rights to compositions, arrangements, MIDI encodings, SoundFonts, recordings, datasets or model weights. Review and record those independently. Trial 001 records publisher Public Domain declarations for three exact works; this is not blanket authorization for other MIDI.

Read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) and [AGENTS.md](AGENTS.md). FLAMORIS is open-source creative software, provided as-is without guaranteed individual support. 🌱
