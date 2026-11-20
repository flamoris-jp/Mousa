# Mousa specializations

One repository owns all six music domains. Each specialist has its own bounded task and learned parameters; generic education/model/checkpoint infrastructure stays in Maidionis.

| Directory | Role | Current stage |
| --- | --- | --- |
| `melody/` | Motifs, phrases, intervals and continuation | Recovered grid-v1 offline experiment |
| `harmony/` | Chords and tension/release | Planned |
| `bass/` | Groove-aligned bass phrases | Planned |
| `drums/` | Beats, accents, meter and swing | Planned |
| `arrangement/` | Form, transitions and dynamics | Planned |
| `critic/` | Distinct validity, feature, preference and similarity tasks | Planned |

The current Melody composition is not six deployed trained models. Before extending a task, define immutable identity/version, bounded inputs/outputs, dataset lineage and splits, metrics, known failures, and exact correspondence with Maidionis contracts. Preserve semantic identity on a code relocation; intentionally change it when the task meaning changes.
