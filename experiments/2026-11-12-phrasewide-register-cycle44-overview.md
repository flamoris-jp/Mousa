# Cycle44: whole-C octave placement considers both boundaries

This is an exploratory comparison on the same known global seeds0–4 and unchanged17-work training set, not fresh music validation or human preference evaluation. Earlier snapshots and results are unchanged.

## Fixed intervention

Control is unchanged output; comparator is Cycle43 greedy nearest-octave return. The new method preserves the original A ordinal+2 pitch classes and each C group's template, onset, gate, velocity, release velocity, member order and EOT.

Exact dynamic programming minimizes absolute group-anchor movement from entrance through all C groups to exit. Missing endpoints contribute zero. Equal total costs choose the lexicographically lower entire anchor sequence. Every legal MIDI0–127 anchor is considered subject to all template members fitting. Bounds:256 groups,≤11 candidates/group,≤30,855 transition evaluations.

This is post-generation optimization of a minimum-pitch group-anchor proxy, not a learned melody voice, harmony or phrase function. All held notes remain intact. Chosen-path collision, same-pitch overlap or copy failure rejects the output; no alternate path search after rejection.

All conditions retain max256 notes, max3 voices, target9216, tail≤384 and identical full-output copy checks over17 training originals plus observed640/921/Dowland21/1691, in generated and canonical order including joins. Empty A/C and no-effect remain separately reported.

## Results: matched successful seeds1,3,4

Control completes5/5; both edits complete3/5, with seeds0,2 blocked by empty A. No successful edit had a copy or collision flag. This is not evidence of a population safety or success rate.

| Descriptor | Control | Greedy | Whole-C |
|---|---:|---:|---:|
| Adjacent-event mean absolute pitch interval |8.26051|7.45716|7.36414|
| Above-octave event interval fraction |0.21848|0.19319|0.18543|
| Distinct pitches |20.0000|20.3333|19.3333|
| Repeated event-pitch fraction |0.02530|0.00775|0.00775|
| Notes |42.3333|42.3333|42.3333|
| Silence ticks |2682.6667|2682.6667|2682.6667|

The objective is25 and29 for both methods on seeds1 and3. On seed4 it drops58→46; exit movement drops15→3 semitones, still larger than the unchanged exit2. Its entrance remains2 and summed internal movement41. Seed3 exit remains4 versus unchanged3.

The optimized proxy's decrease is built into the method, not independent evidence of musicality. The small event-gap improvement comes with reduced pitch diversity, whose musical meaning is unknown. Event-order intervals include simultaneous notes and must not be called voice-leading. No listening ratings were obtained.

All temporal and occupancy metrics are identical within matched outputs. Complete-only control means over5 versus edited means over3 have selection bias; they do not measure changes in silence. All status rows and the common-success denominator are retained.

## Verification and limitations

- Final plan SHA d0cf72b7a572d619b70a2998bfa8b6d028c8b7fb7e2ab6d288acd2f4a725b931 fixed before real execution.
- Initial/repeat identical except CPU0.591888/0.342670sec; all5 private files byte-identical.
- Old generation state, control and greedy outputs exactly equal Cycle43, including statuses.
- Independent backward scalar-cost DP plus forward lexicographic reconstruction matches every selected path and28 anchor choices.
- All non-pitch note fields, non-anchor group fields, templates and timeline metrics are unchanged; all21 source copy checks recomputed and original bytes unchanged.
- Five targeted tests pass, including100 short exhaustive Cartesian oracle cases and CPU-skip schema. Parent independent profile covers1,000 cases,104 empty candidate sets and480 ties; parent result audit reports3,082 checks.
- A pre-fit automated bound insertion broke loop indentation. Synthetic tests caught3 errors/1 failure; fixed before execution. The unrun earlier plan and correction record remain preserved.
- No new training source, fresh predictive score, human rating, production adoption, media upload or post-result parameter change.

The result supports only feasibility of this exact constrained editing computation on three previously known candidates. Better phrase perception, voice continuity and attractiveness remain untested.
