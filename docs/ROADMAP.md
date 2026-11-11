# Mousa roadmap

Current stage: **offline Melody research implementation**, not production music AI. Source completion, measured acceptance and deployment are distinct.

## M0: Repository boundaries

- [x] README, AGENTS, contribution/security guidance and data policy
- [x] One repository with six specialist boundaries
- [x] Experimental note-only MusicIR and 9 unit tests
- [x] Bootstrap CI passed and PR #1 merged

## M1: Recover and reproduce Trial 001 (Issue #2)

- [x] Recover original source archive and verify all 429 inventoried members
- [x] Record source hashes, historical metrics and limitations separately from new runs
- [x] Recheck exact three-work source declarations and add a hash-pinned intake catalog
- [x] Migrate music-only source against an external pinned Maidionis checkout
- [x] Add 22 music tests and fresh native CI for training, reload, generation and resume/tamper checks
- [x] Fresh native CI run 43006693911 passed; exact evidence and weak-quality results recorded
- [ ] Review and merge PR #6

See [experiment evidence](../experiments/README.md). The recovered trial uses a narrow next-token task; this does not imply musical quality.

## M2: Broader MIDI ingestion and musical representation (Issue #3)

- [x] Initial three-source allowlist, hash checks and explicit mono-track preprocessing
- [ ] Broader source admission and composition/arrangement-family provenance
- [ ] Event/phrase representation with rests, durations and note onsets, rather than mainly HOLD targets
- [ ] Near-duplicate/family detection beyond exact normalized melodies
- [ ] Versioned interchange with Cantabile, explicit supported events and losslessness tests

## M3: Useful music specialists (Issue #4)

- [ ] Melody: improved representation, broader whole-work-held-out evaluation and stronger baselines
- [ ] Critic: separate validity, structural features, human A/B/tie/neither preference and similarity tasks
- [ ] Drums, Harmony, Bass and Arrangement, added with independent bounded contracts
- [ ] Specialization artifact acceptance and qualified model-serving interfaces

## M4: Music workflow (Issue #5)

- [ ] Runtime-owned musical state, section plans and selective regeneration
- [ ] Cantabile handoff with explicit permissions and editable project history
- [ ] Consented human preference/revision records
- [ ] Blinded listening comparisons on independent work families

## M5: Release qualification

- [ ] Model cards, third-party notices, dataset/weight/media rights and honest quality thresholds
- [ ] Measured GPU/ROCm/resource qualification in a separate deployment environment
- [ ] Auditable artifacts and reliable versioned interfaces
- [ ] Distribution/Updater/Hub only after appropriate acceptance
