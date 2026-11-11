# Mousa architecture

## Responsibility map

```text
Reviewed MIDI source and provenance
  -> Mousa preprocessing / music task composition
  -> external Maidionis Core: numerical training / checkpoints / contracts
  -> bounded specialist proposals
  -> AI Runtime: Workflow / Jobs / shared state / execution authority
  -> Cantabile: editable project / MIDI / WAV
  -> human choice and revisions -> future preference examples
```

Only the first offline Melody research path is implemented. Runtime collaboration, product edits and preference feedback in this diagram remain planned. A research CLI can write standalone diagnostic MIDI files; it does not own Cantabile projects.

## One repository, six specialist families

Melody owns motif and phrase proposals; Harmony owns harmonic suggestions; Bass owns bass/groove relationships; Drums owns beat/accent patterns; Arrangement owns section/contrast proposals; Critic separates validity, features, preference and similarity diagnostics. These domains share general mechanisms in Maidionis without adding music semantics to Core.

Model outputs are proposals, never execution authorization. Future cross-specialist inputs must be bounded snapshots mediated by Runtime rather than private shared mutable state or model-owned tool calls.

## Current Melody composition

`specializations/melody/grid_v1` preserves the experimental `research.music-next-token` v1 task while relocating its source. It explicitly registers its schema, input codec, dense model shape, output codec and categorical objective against Maidionis pinned at `a987eeeea11e3971d3b9708bfff6b3545cdb601f`. Core stays an external dependency. The build identity binds both Core and music composition source.

The fixed source catalog is processed only by an explicit CLI. Source byte hashes, selected tracks, declared terms and transformations are recorded. One whole work belongs to each train/dev/test split; exact normalized melody duplicates are rejected. This is not a complete semantic arrangement-family discovery algorithm or a crawler.

Native training uses the real Core numerical engine. Export/reload is limited to an inventoried offline research checkpoint with trusted digests, not an admitted serving artifact or hostile-archive sandbox. Reproduction tests include separate-process resume and tamper detection. See [the experiment guide](../specializations/melody/grid_v1/README.md).

## MusicIR and interchange

`src/mousa/music_ir.py` remains a small experimental note-only Python value object, not a frozen wire protocol. The recovered grid task has its own intentionally narrower representation. Neither is a lossless replacement for Cantabile's MIDI/event contracts. Controller events, tempo/meter maps, overlapping notes, instruments and lyrics require explicit future integration and losslessness decisions.

## Evaluation

Keep source validity, structural features, prediction accuracy, human preference and similarity risk separate. Report denominators and note-onset performance as well as sustain-heavy overall accuracy. Three already-inspected public works support reproducibility diagnostics only, not a sealed quality benchmark. A Critic cannot define artistic truth.

## Still outside this implementation

Other trained specialist families, learned preferences, live model serving, Runtime orchestration, Cantabile handoff, host lifecycle, GPU qualification, MCP and deployment.
