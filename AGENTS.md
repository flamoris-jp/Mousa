# AGENTS.md — Mousa

Mousa is the FLAMORIS music-specialization repository. Inspect current code, README and related Issues before modifying it. The [FLAMORIS repository policy](https://github.com/flamoris-jp/flamoris-commons/blob/main/docs/repository-policy.md) applies.

## Ownership boundary

- **Mousa:** music-specific tasks, symbolic MusicIR proposals, training curricula, rights/provenance, model compositions, music evaluation, research failures, and held-out measurements.
- **Maidionis:** specialization-neutral numerical models, education, checkpoint/restart, artifact and bounded inference contracts. Reuse it rather than copying its Core into Mousa.
- **AI Runtime:** job scheduling, execution, retry/fallback, tool authority, shared workflow state, resource/host lifecycle.
- **Cantabile:** source-of-truth for editable MIDI project/event state, import/export and rendering. Mousa must not silently mutate Cantabile projects.
- No model obtains authority to download files, operate services, trigger actions, or write music projects merely from its output.

## Non-negotiable research rules

1. Do not infer that public availability means a MIDI file is permitted for training or redistribution; record each source's terms and underlying arrangement/composition provenance.
2. No raw external MIDI, weights, large datasets, or private assets in commits without explicit licensing review. Audio/video files, including synthesized WAVs, are prohibited regardless of licensing review; use external storage with manifests and digests.
3. Split by composition/arrangement family before tokenization or transposition. No transformed sibling may cross train/selection/test boundaries.
4. Never call fit-to-train, note-continuation accuracy, or a model's Critic score proof of musical quality or held-out generalization.
5. Keep negative preferences, failed experiments, sample counts, metric denominators, seeds, environment, dataset/source hashes, and duplicate checks.
6. Separate deterministic invalid MIDI checks, structural/music features, human preferences, and similarity/reproduction risk; no universal 'good music' score.
7. MusicIR here is experimental, not a replacement for Cantabile's format or a frozen Maidionis v1 specialization contract.
8. Protect privacy and credentials. Do not put machine-specific topology, hostnames, personal identifiers, or secrets in public source.
9. Avoid speculative service/runtime deployments, GPU claims and build commands. Only describe tested behavior as implemented.

## Before substantial changes

Read README, architecture, data policy, roadmap, existing code and tests; check Maidionis current specialization contract and Cantabile import/export boundaries. Use a branch and PR, and update tests and docs together. Each specialization owns its music semantics; keep generic Maidionis logic outside Mousa.

## Verification

Current bootstrap command: `PYTHONPATH=src python -m unittest discover -s tests -v`. No training or GPU acceptance is claimed.

Code: Apache-2.0 unless stated otherwise. Dataset/weight/media rights are separate. AI assistance is welcome, with human review responsible for licenses, quality and security.

## Audio/video storage policy

Do not commit audio or video files (including MP3, MP4, WAV, FLAC, M4A, OGG, MOV, WebM and equivalents), regardless of size, ownership, license, or whether they are generated demos or test samples. This also prohibits Git LFS pointers, renamed/encoded media and media hidden inside archives. Do not bypass the rule with `git add -f` or ignore exceptions.

Store media outside Git in approved artifact/media storage. Commit references, SHA-256 digests, provenance, analysis results, scripts and small text/symbolic fixtures instead. Generate temporary synthetic media during tests when needed. Licensing review does not waive this storage policy. MIDI/project data and images retain their existing repository-specific rules.

The `.gitignore` covers common audio/video extensions case-insensitively. Where installed, the `Media policy / No tracked audio or video` PR check also detects force-added files and LFS pointers by filename; it is not a content/archives scanner or a server-side push restriction. Do not rewrite history or remove external assets as part of this rule. See the [shared policy](https://github.com/flamoris-jp/flamoris-commons/blob/main/docs/repository-policy.md#121-audio-and-video-storage).
