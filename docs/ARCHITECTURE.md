# Mousa architecture (proposed / early development)

## Responsibility map

```text
Verified MIDI source + provenance
          |
          v
  Mousa dataset processing / MusicIR / features
          |
          v
  Maidionis Core <-- Mousa task-specific compositions, curricula, evaluation
          |
    bounded proposals from specialist models
          |
          v
  FLAMORIS AI Runtime: Workflow/Jobs/Shared Music State/permission
          |
          v
  Cantabile: editable events / projects / MIDI / WAV
          |
          v
  Human listens, chooses, revises -> Mousa comparison dataset
```

Maidionis owns specialization-neutral training and model/archive mechanisms, not music semantics. Mousa owns the music-specific descriptors and model composition. Runtime owns orchestration; Cantabile owns editable project state. Do not duplicate these systems by copying Maidionis Core source into Mousa. A future explicit versioned dependency is preferred.

## Six independent model families within one repository

- **Melody:** phrase continuation/variation, intervals, rests, motif development.
- **Harmony:** harmonic alternatives, chord rhythm, tension/release.
- **Bass:** line generation and groove/harmony relationships.
- **Drums:** accents, meter, swing, kick/snare/hat and variations.
- **Arrangement:** section plans, contrast, transitions, energy arcs.
- **Critic:** first strict validity checks; then separate structural feature reports, preference comparisons, and similarity/red-flag reports.

The model outputs are bounded proposals. A specialist never executes an action or writes directly to a Cantabile project. Cross-specialization dependencies are mediated through a versioned, bounded musical state projected by Runtime, not private mutable global memory.

## MusicIR and interchange

The current `src/mousa/music_ir.py` is a small **experimental** note-only Python value object for early unit tests, not a MIDI parser/editor, multitrack arrangement standard, or frozen public wire contract. It stores note start/duration in integer ticks and MIDI pitch/velocity, a part ID, PPQ and tempo. Real MIDI reading/writing will be designed against Cantabile's import/export semantics; controller events, overlapping notes, tempo maps, meter maps, instruments and lyrics need explicit future scope and losslessness decisions.

## Training and evaluation

Candidate pipeline: source verification -> fixed manifest/hashes -> piece-family grouping -> train/selection/held-out split -> features/tokenization -> bounded model training -> offline evaluation -> candidate generation. Preference feedback (A/B/tie/neither, reasons, edited phrase) is a separate learner and is not automatically a 'quality' label for the source piece.

Evaluate discrete note onsets separately from note continuation. Always publish per-split denominator, baselines, uncertainty and similarity diagnostics. The Critic cannot define artistic truth; human selection remains authoritative.

## Current stage

Documentation and experimental MusicIR implementation only. No fitted specialist model, training runner, actual MIDI ingest, provenance-approved dataset, Runtime adapter, Cantabile bridge, service, MCP or deployment has been accepted in this repository.
