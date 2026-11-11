# Mousa roadmap

Current stage: **bootstrap / research**. Phases below are intended work, not shipped features.

## M0 — Repository boundaries and testable seed

- [x] README, AGENTS, contribution/security guidance and data policy
- [x] One-repository six-specialization layout with documented ownership
- [x] Experimental bounded note-only MusicIR with fast unit tests
- [ ] Verify CI checks on the PR and merge after review

## M1 — Reproduce the first MIDI learning trial

- [ ] Locate and verify the original experiment source, licenses, model weights, exact dataset IDs, commands and hashes before migration
- [ ] Reproduce its train/selection/held-out split and next-note baseline
- [ ] Preserve observed failures and distinguish continuation from new-onset accuracy
- [ ] Link experiment output/metrics rather than committing unreviewed MIDI or weights

## M2 — MIDI ingestion and musical representation

- [ ] Source crawler/ingester limited to approved sources, with per-work and arrangement provenance
- [ ] MIDI event extraction preserving beat-time, tempo/meter and meaningful durations
- [ ] Derive melodic intervals, rests, phrase/motif repetitions, rhythmic accents
- [ ] Duplicate/family detection before train/validation/test split
- [ ] Design a versioned interchange with Cantabile without claiming losslessness prematurely

## M3 — First specialists

- [ ] Mousa Melody: reproducible bounded candidate training and generation versus statistical baseline
- [ ] Mousa Critic: validity + structural features + A/B preference as separate outputs
- [ ] Later: Drums, Harmony, Bass, Arrangement in bounded tests
- [ ] Exact Maidionis specialization descriptor/codec/objective components and checkpoint load acceptance

## M4 — Music workflow

- [ ] Runtime-controlled composition sections and selective regeneration
- [ ] Cantabile handoff for editable projects and human review
- [ ] Store preference and revisions with consent, provenance and separate rights
- [ ] Test song quality with blinded pairwise human comparisons and held-out work families

## M5 — Release qualification

- [ ] Evaluation thresholds, model cards, clear licensing and third-party notices
- [ ] GPU/ROCm compatibility and resource admission measured explicitly
- [ ] Auditable model artifacts, similarity safeguards and reliable versioned interfaces
- [ ] Distribution/Updater/Hub integration only after passing acceptance

See [DATA_POLICY](DATA_POLICY.md) and [ARCHITECTURE](ARCHITECTURE.md).
