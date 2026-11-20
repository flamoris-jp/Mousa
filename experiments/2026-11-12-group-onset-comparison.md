# Cycle 34: lossless onset groups, fixed timing comparison

## Outcome

The previous-group-cardinality context did not improve the predeclared timing prediction diagnostic. Equal-work group-delta NLL rose from **4.144505** (global) to **4.799273** (context); lower is better. Both previously observed diagnostic works worsened:

| Observed diagnostic | Groups | Global | Previous-cardinality k4 |
|---|---:|---:|---:|
| Adam 640 | 98 | 4.360577 | 5.091107 |
| Chopin 921 | 83 | 3.928432 | 4.507438 |

These are group-onset-delta outcomes only, not joint note/template/pitch/gate likelihoods. They cannot be compared with earlier event-level NLL. The diagnostics are not fresh tests and were not fitted.

## Frozen design and data

Final plan SHA-256: `a02a87a014edf080d5734ee3e6f2546f9960a36146208d0ee3a815a9e1f85037`.
Existing 16 works, 4,150 selected note events, 3,259 distinct-onset groups. No new source admission; previous edition/contributor and within-training motif links remain. Original bytes and EOT were unchanged.

Both arms have a uniform global prior of total mass 1. The context arm uses `(local count + 4 * smoothed global probability) / (local total + 4)`, conditioned on previous group cardinality, with separate initial/later support. Initial deltas allow zero; later deltas must be positive. Work boundaries reset context. This is not the separate drum model's smoothing formula.

Generation samples delta, empirical template, and empirical anchor in separate stages with whole-proposal feasibility rejection. Templates retain group member order, relative pitches, gates, velocity and release velocity. No gates are clipped. This is not a joint learned template/pitch/gate model or inferred voice/chord labels.

## Generation and repeat

Both conditions completed all five prescribed seeds, so the common completed-seed denominator is 5; no missing or failed outputs. All 10 candidates passed the fixed exact-8-interval guard against the 16 training works and both observed diagnostics. This limited guard is not copyright clearance or a proof of originality.

| Complete-only metric (5 per arm) | Global | Context |
|---|---:|---:|
| Mean notes | 36.0 | 37.2 |
| Mean absolute consecutive-event pitch interval | 7.0234 | 7.0167 |
| Overlap-onset fraction | 0.4457 | 0.4685 |
| Rest fraction | 0.4083 | 0.2943 |

No musical-quality improvement follows from these structural numbers. Same seed and RNG call policy do not align later decisions once timing proposals and rejections differ.

All 127 template types remained in training. Five types larger than three notes, accounting for 18/3,259 occurrences (0.5523%), were unavailable for generation; 122 template types were available. Every generated group reconstructed its note start/end/pitch/velocity/release-velocity fields exactly. All later onsets were strictly increasing; generated bounds, maximum three active notes, and absence of same-pitch overlaps were independently checked. The raw source note-only grouping remains lossless; the capped sampler is a restricted generation policy, not a lossless model of the source distribution.

Run/repeat reports were identical except CPU time (0.2183 / 0.1701 seconds), and all 10 private candidate JSON files were byte-identical. CPU checking occurs before fits/evaluations and each generation proposal, not hard preemption within one operation. No audio or raw generated notes are in Git or training materials.

## Artifacts and limits

- `2026-11-12-group-onset-final2-plan.json`, bound clearance and independent-model-review JSON
- `2026-11-12-group-onset-results.json` (all outputs, rejections and denominators)
- `2026-11-12-group-onset-repeat-verification.json` (candidate hashes and group-size distributions)
- `../datasets/research-group-onset-usage-cycle34-20261112.json`
- `2026-11-12-group-onset-metadata-snapshot.json`

The next question is why previous group size is an unhelpful timing predictor across these observed works, not whether to claim a better melody. No parameters were changed after this result. Source-template reuse is restricted to private research candidates, without public-release clearance.
