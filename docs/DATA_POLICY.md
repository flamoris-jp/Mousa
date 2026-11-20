# MIDI dataset and model provenance policy

## Why this is needed

Publicly downloadable MIDI is not automatically free of copyright restrictions. Rights may apply to the underlying composition, a specific arrangement, a performance and the delivered MIDI encoding. Dataset-level licensing statements are not substitutes for per-source verification. Keep code licensing separate from weights, MIDI, SoundFonts and audio.

## Intake record (proposed)

For each candidate work, retain at minimum:

- source/project URL, fetch timestamp, exact upstream file identity and SHA-256
- title, composer, arranger/transcriber, known provenance, intended musical role
- license text/version, evidence URL, rights review state: `reviewed`, `pending`, `excluded`
- whether local storage, analysis/training, redistribution and generated work publication are allowed
- normalized composition/arrangement family, near-duplicate grouping and transform lineage
- structural features and human-review notes without overwriting the raw original
- split assignment at **composition/arrangement family** level, not file or transposed-phrase level

Do not ingest unknown/pending material into training or commit its bytes. Approved source manifests may be committed without the files themselves when provenance remains meaningful.

## Evaluation and preference data

- Keep intake validity separate from aesthetic judgement; unusual meter, dissonance, rests or syncopation are not automatic defects.
- Structural Critic metrics describe features, not universal musical beauty.
- Human preferences are context-dependent; distinguish `preferred`, `adopted`, `edited`, `tie`, and `neither`. Record requested genre/use without collecting unnecessary personal data.
- Preserve rejected candidates and reasons as research evidence, but do not train a generative model on unlicensed raw works.
- Report per-split metrics, relevant baselines, new-note-onset performance, diversity and copying/similarity diagnostics.

## Storage

Audio/video files (including stems, demos and synthetic WAV test samples) must never be committed, including through Git LFS or archives, regardless of size or licensing review. Store them outside Git and commit only references, SHA-256 digests and analysis metadata. Generate temporary synthetic audio during tests rather than checking binaries in.

Large raw/processed corpora, checkpoints and model weights are ignored from ordinary commits. Use approved, provenance-bound artifact storage with exact digests and explicit rights; no secrets or machine-specific directories in repository defaults.

## Pre-publication review

For shared datasets, checkpoints, audio demos and generated works: separately review licensing, privacy, reproducibility, similarity risk, and claims supported by held-out testing.
