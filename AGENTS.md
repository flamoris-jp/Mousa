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
2. No raw external MIDI, weights, large datasets, synthesized WAV, or private assets in commits without explicit licensing review. Use manifests and digests for local material.
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
