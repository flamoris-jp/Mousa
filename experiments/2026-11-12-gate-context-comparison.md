# Cycle37: timing context from observed note durations

## Fixed comparison

Same17training works (4319notes,3428groups), observed untrained diagnostics640/921, initial support0..65536, later1..12288, and the same all17+2 copy references. Four arms were fixed before fitting: global, previous cardinality, previous-group maximum gate binned, and active horizon binned. Both duration contexts use the same thresholds192/384/768/1536 ticks and k4 backoff. The earlier exact-gate three-arm proposal was never run.

Active horizon after a group is `max(previous_horizon - delta, current_max_gate)`. The next prediction uses only past groups, with state reset per work. It does not infer voice, harmonic function, or melody labels. Timing is conditioned on this history; templates and anchors are sampled separately. This is not a joint learned group probability model.

## Prediction results

| Arm | Adam640 | Chopin921 | Equal-work timing NLL |
|---|---:|---:|---:|
| Global | 4.426875 | 3.944144 | 4.185509 |
| Cardinality | 5.172988 | 4.531769 | 4.852378 |
| Previous max gate, fixed bins | 4.025480 | 3.403290 | 3.714385 |
| Active horizon, same bins | 4.059505 | 3.436023 | 3.747764 |

Lower is better. Both duration contexts improve this repeatedly observed diagnostic relative to global and size context. Previous max gate has slightly lower NLL than horizon here. These are teacher-forced group-delta NLLs, not raw-event likelihood, fresh-test evidence, or musical-quality scores. Initial probabilities are identical across all four arms, so differences arise in later timing. No settings were retuned after these outcomes.

## Generated timeline measurements

All20prescribed candidates completed and passed the fixed exact8interval guard, with5complete seeds per arm and all5common across arms. Candidate completion or zero copy flags is not proof of musical appeal, originality, or publication permission.

| Complete-only mean (5 per arm) | Global | Cardinality | Previous max gate | Active horizon |
|---|---:|---:|---:|---:|
| Internal actual silence, ticks | 2314.4 | 2643.2 | 2681.6 | 1216.0 |
| Longest contiguous actual silence, ticks | 1267.2 | 1152.0 | 2880.0 | 1267.2 |
| Total silence, ticks | 3476.0 | 3766.4 | 3882.4 | 2362.4 |
| Polyphonic time fraction | .24314 | .24375 | .15599 | .17925 |
| Active voice-tick integral | 8716.8 | 8531.2 | 7424.0 | 9273.6 |

Leading silence was921.6ticks on average in every arm. Leading/internal/trailing silence is separately recorded; it is calculated from the union of sounding note intervals, never inferred from gaps between onsets. An earlier long-held note therefore prevents a false silence label. A separate per-tick occupancy oracle reproduced the union, maximum gap, and voice-integral measurements for all20files.

The horizon arm had less internal silence than the previous-max-gate arm in these five seeds, while slightly worse timing NLL. That is a structural tradeoff, not an established musical improvement. Identical seeds do not align later random decisions after different timing draws and rejected proposals. Templates retain all note fields and are rejected whole if infeasible, never clipped. All original source bytes and EOT values remain unchanged.

## Reproducibility and controls

Run/repeat reports agree except CPU time (0.1405/0.1421seconds). All20private candidate files are byte-identical. Reconstruction checked start/end/pitch/velocity/release velocity, strict later-onset order, bounds, maximum3active notes, and no overlapping equal pitches.

Cycle36's17work global/cardinality controls reproduce the same10private candidate bytes. Global prediction JSON is identical; cardinality per-group NLL differs by at most about1e-15 (later sums at most6e-14), within a1e-12 floating comparison tolerance. Their equal-work means match exactly. The new standalone model rejects legacy generators that would silently substitute cardinality state for gate state; this prototype issue was fixed and regression-tested before real fitting.

## Artifacts and unchanged roles

Plan SHA: `d2ea15dce6facbcba71f7cd3327ac74899eb0e48e90cfca5137575bc4a4bc836`.

Results, repeat verification, independent review, clearance, and metadata snapshot use the `2026-11-12-gate-context-` prefix. `datasets/research-gate-context-usage-cycle37.json` records continued use of the same17works. No new sources were admitted, no model selection was made from the separate Groove results, and640/921 remain observed diagnostics. Prior within-training motif and source-family links persist.

Only metadata is prepared for storage. Private generated notes/audio are absent from Git and training-material storage. The next useful question is whether this structural difference persists under predeclared independent listening or additional unobserved material, not whether to label a numerical winner universally better.
