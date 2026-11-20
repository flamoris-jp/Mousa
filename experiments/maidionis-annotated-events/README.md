# Human-annotated relative chord-event pilot

A separate, freshly initialized Mousa/Maidionis composition learns local
transitions from **McGill Billboard's CC0 chord annotations**. It is not a
continuation of the OpenScore weak-label checkpoint, a melody model, or a
production music generator. See [ChoCo review](CHOCO_REVIEW.md) for why the
original annotations were selected instead of indiscriminately mixing ChoCo.

## Representation and scope

The task `mousa.relative-chord-events.annotated.experimental.v1` predicts one
chord event from two preceding valid chord events. Its 96 classes are
`relative_root_pitch_class * 8 + quality_index`, with qualities
`maj, min, dim, aug, 7, maj7, min7, hdim7`. The root is measured against the
annotated current tonic, modulo 12. This supports chromatic roots; it does not
assert that all roots are diatonic scale degrees or that tonic identifies mode.

Bass inversions remain in source provenance but are not prediction targets.
Extended/altered unsupported qualities are not collapsed to a simpler chord:
they break context. N/X, unknown tonic or meter, uncertain inline-meter phrases,
key/meter changes and gaps also break context. Invalid durations/overlaps reject
the entire representative source slot. Adjacent exact raw duplicates may be
coalesced only under the frozen matching-context and time-contiguity rules.

Timestamps and source-line identities are retained for audit. **The model does
not learn duration, melody, rhythm, voicing or expressive performance.** LAB
internal event times were interpolated within manually aligned phrases by the
source project; this is not a dataset of hand-timed boundaries for every chord.

## Data and evaluation

The original CC0 complete annotations and LAB archives are pinned by SHA-256.
Their grant concerns annotations, not the underlying recordings, lyrics or
compositions. No audio, lyrics or melody transcription was downloaded for this
pilot. Attribution: John Ashley Burgoyne, Jonathan Wild and Ichiro Fujinaga,
*An Expert Ground Truth Set for Audio Chord Recognition and Music Analysis*,
ISMIR 2011. [Official source and terms](https://ddmal.ca/research/The_McGill_Billboard_Project_(Chord_Analysis_Dataset)/).

Exact duplicate files and normalized title aliases from both the index and
headers are unioned before tokenization. Title-only unions conservatively keep
possible covers together, even at the cost of merging unrelated same-title
songs. Alternate titles and translations can still escape this heuristic.
One lowest-ID source represents each union family; rejected representatives
are not replaced. The fixed hash split reserves 20% of families before window
selection, with at most 16 hash-selected windows per family in either split.
Historical use by other models/researchers is not known. Held-out means unseen
by this fresh run, not a newly discovered or globally untouched benchmark.

A single seed-314 fit uses 60 steps × 32 sampled examples, one CPU thread and a
90-second CPU ceiling. It records every sampled index. Evaluation compares
initial/fitted model against Laplace-1 unigram/trigram controls, both full-data
and exposure-matched, with row-weighted and family-macro metrics. These are
teacher-forced next-label metrics, not human preference or musical quality.
The earlier weak-label pilot has different labels, repertoire and prediction
units; its percentages are not a directly comparable baseline.

## Reproduction and boundaries

`prepare.py` consumes explicit local source paths and never fetches data.
`protocol.json` was saved before tokenization; source formats and quantity had
already been inspected, so this is not a source-blind preregistration.
CMake links the pinned external Maidionis Core; Core is not copied or changed.
`annotated_events_model validate DATA` checks a dataset without fitting, and
`train DATA NEW_OUTPUT` writes a new checkpoint directory. `evaluate.py` requires
its manifest and exact data/results digest binding. Native negative tests and
synthetic preparation/evaluation tests accompany the experiment.

No existing checkpoint is overwritten. Raw source data, event tables, weights
and media remain outside Git. No merge, deployment, new service, GPU claim or
commercial clearance for underlying songs is implied.
