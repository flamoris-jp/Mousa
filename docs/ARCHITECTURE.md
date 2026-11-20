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

## Melody Trial 001

`specializations/melody/grid_v1` preserves the experimental `research.music-next-token` v1 task while relocating its source. It explicitly registers its schema, input codec, dense model shape, output codec and categorical objective against Maidionis pinned at `a987eeeea11e3971d3b9708bfff6b3545cdb601f`. Core stays an external dependency. The build identity binds both Core and music composition source.

The fixed source catalog is processed only by an explicit CLI. Source byte hashes, selected tracks, declared terms and transformations are recorded. One whole work belongs to each train/dev/test split; exact normalized melody duplicates are rejected. This is not a complete semantic arrangement-family discovery algorithm or a crawler.

Native training uses the real Core numerical engine. Export/reload is limited to an inventoried offline research checkpoint with trusted digests, not an admitted serving artifact or hostile-archive sandbox. Reproduction tests include separate-process resume and tamper detection. See [the experiment guide](../specializations/melody/grid_v1/README.md).

## MusicIR and interchange

The current `src/mousa/music_ir.py` is a small **experimental** note-only Python value object for early unit tests, not a MIDI parser/editor, multitrack arrangement standard, or frozen public wire contract. It stores note start/duration in integer ticks and MIDI pitch/velocity, a part ID, PPQ and tempo. Real MIDI reading/writing will be designed against Cantabile's import/export semantics; controller events, overlapping notes, tempo maps, meter maps, instruments and lyrics need explicit future scope and losslessness decisions.

## Training and evaluation

Candidate pipeline: source verification -> fixed manifest/hashes -> piece-family grouping -> train/selection/held-out split -> features/tokenization -> bounded model training -> offline evaluation -> candidate generation. Preference feedback (A/B/tie/neither, reasons, edited phrase) is a separate learner and is not automatically a 'quality' label for the source piece.

Evaluate discrete note onsets separately from note continuation. Always publish per-split denominator, baselines, uncertainty and similarity diagnostics. The Critic cannot define artistic truth; human selection remains authoritative.

## Current stage

Experimental MusicIR, stem-intake utilities and [scale/key conditions](SCALE_KEY.md)
are implemented alongside bounded research records. Scale/key conditions own
music-specific cents/tonic semantics, a narrow original-exercise exporter and
a [degree-native model composition](DEGREE_GENERATION.md) that selects ordinal
labels before pitch rendering. The separate legacy saved-semitone decoder
retains its scale filter and historical limits;
they do not alter MusicIR's integer pitch field or Maidionis Core. Production qualification remains open for trained specialists, general MIDI
editing, training runners, Runtime adapters, Cantabile bridges, services and MCP.
