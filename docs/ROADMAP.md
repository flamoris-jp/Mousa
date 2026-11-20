# Mousa roadmap

Current stage: **bootstrap / research**. Phases below are intended work, not shipped features.

## M0 — Repository boundaries and testable seed

- [x] README, AGENTS, contribution/security guidance and data policy
- [x] One-repository six-specialization layout with documented ownership
- [x] Experimental bounded note-only MusicIR with fast unit tests
- [ ] Verify CI checks on the PR and merge after review

## M1 — Reproduce the first MIDI learning trial

- [x] Recover original source archive and verify all 429 inventoried members
- [x] Record source hashes, historical metrics and limitations separately from new runs
- [x] Recheck exact three-work source declarations and add a hash-pinned intake catalog
- [x] Migrate music-only source against an external pinned Maidionis checkout
- [x] Add 22 music tests and fresh native CI for training, reload, generation and resume/tamper checks
- [x] Fresh native CI run 43006693911 passed; exact evidence and weak-quality results recorded

See [experiment evidence](../experiments/README.md). The recovered trial uses a narrow next-token task; this does not imply musical quality.

## M2 — MIDI ingestion and musical representation

- [x] Experimental source-referenced scale/key conditions, microtonal numeric targets and original monophonic MIDI rule fixtures; see [SCALE_KEY](SCALE_KEY.md)
- [x] Mandatory scale/key gate in actual saved-checkpoint generation, with exact-zero forbidden probability and history/output verification; legacy microtonal inputs rejected explicitly
- [x] Degree-native input/output composition with a new task identity, original-symbolic fit/reload check and microtonal scale/key MIDI rendering; reviewed music-corpus learning remains follow-on work
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
