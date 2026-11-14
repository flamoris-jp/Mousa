# Group roles and phrase-boundary measurement audit (Cycle35)

This is a **posthoc audit of the ten already generated Cycle34 candidates**, not new training or a fresh generation comparison. All candidate hashes are bound to the frozen Cycle34 results; original and repeated candidate directories produce byte-identical diagnostic JSON. No notes, simultaneous groups, durations or performance fields are changed. No new recording is admitted.

## Why separate the measurements?

A flattened event pitch interval can mix vertical chord spans with horizontal changes. The new descriptive view reports within-group spans separately from consecutive minimum-pitch-anchor intervals. A minimum selected pitch is **not** an inferred bass voice, harmonic root or melodic role. It is observable, unlike those interpretations.

Mean absolute anchor change across five candidates per arm is 6.8352 semitones for global timing and 6.8340 for previous-cardinality timing. Earlier flattened-event means were 7.0234 and 7.0167. These distinct measures cannot establish either voice leading or listener preference.

## Silence is not phrase truth

Internal silence is measured from the running latest end of **all earlier notes**, not only the preceding group. A sustained old note must not create a false pause when a newer short note ends. Initial and trailing silence are reported separately.

Using one quarter-note (384 ticks) silence as a provisional boundary gives counts `[2,2,2,3,3]` for global seeds0–4 and `[0,5,2,3,2]` for cardinality seeds0–4. Two quarter-notes gives `[1,1,0,2,0]` and `[0,0,0,1,0]`. This threshold sensitivity cautions against turning a convenient feature into a claimed semantic label. Phrases can cross rests or end without one; human segmentation is absent. The cut profiles are analytic conventions, not training targets or automatic judgments of structure.

Synthetic checks cover sustained-note overlap, exact threshold inclusion, unsorted input, transposition invariance, proportional time/PPQ scaling, singleton/empty cases, invalid parameters and candidate-hash rejection. No source data is used to tune the one/two-beat thresholds. Both arbitrary thresholds and every seed are reported, with no winner selected.

## Next hypotheses, not results

A whole-group generator could combine a slowly changing anchor with varied relative templates, but constraining the minimum pitch is not learned voice-leading and may merely induce repetition. A phrase experiment needs separate controls for local continuity, template repetition, long rests and planned motif returns. Test those controls on synthetic examples first; do not manufacture human preference/role labels or reuse these ten samples as independent proof. Whole-group feasibility, fixed copying checks and failure denominators must remain intact.
