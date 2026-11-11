# Mousa specializations

One GitHub repository owns all music-domain specializations. Each specialization is independent at the **task/model** boundary but shares Mousa's dataset provenance, experimental MusicIR conventions and Maidionis general-purpose model infrastructure.

| Directory | Role |
|---|---|
| `melody/` | motive, phrase, interval movement, continuation |
| `harmony/` | chords, tension, progression |
| `bass/` | groove-aligned bass phrase |
| `drums/` | beat patterns, accents, meter and swing |
| `arrangement/` | large-scale form and dynamics |
| `critic/` | validity, structured analysis, preference and similarity as distinct tasks |

No specialized trained models are included in this bootstrap. Before introducing one, define its immutable task ID/version, bounded input/output and failure/abstention rules, dataset split and metrics, provenance, and correspondence to the current Maidionis contract. Do not copy Maidionis Core implementations here.
