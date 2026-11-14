# Cycle42: pitch-only return preserves timing, but increases large leaps

This is a post-result exploratory follow-up to Cycle41's five blocked whole-fragment replacements. It uses the same known Cycle37 global seed0–4 pool, not independent new outputs. The original17 training works and all previous results remain unchanged.

## Frozen intervention

For C groups with onsets in [4608,6912), replace anchor j with the **original** A[j mod len(A)] anchor +2, where A onsets are in [0,2304). Keep every onset, end, gate, velocity, release velocity, relative group offset, template/member order and EOT9216. Notes spanning boundaries are not cut. Empty A/C blocks the intervention; unchanged anchors are no_effect, not a success. No alternate mapping, shift, seed or boundary after results.

Whole-output checks retain MIDI0–127, max256 notes, max3 active voices, no overlapping equal pitches and tail≤384. The identical eight-note interval screen covers all17 training originals plus already-observed640,921,Dowland21 and1691, in generated/canonical orders including joins. These four observations are not fitted.

## Actual outcomes

- Control:5/5 complete.
- Intervention:3/5 complete, seeds1,3,4; seeds0,2 blocked because A has no onset.
- No pitch-range, overlap or copy rejection in these three completed edits. This small known pool does not establish general safety.
- Changed anchors/notes: seed1 9/13; seed3 8/8; seed4 11/14.
- A/C group counts:9/9,10/8,7/11 respectively. Thus one mapping uses a prefix and another cycles into a second pass.
- No actual human ratings, listening preference or musical-attractiveness conclusion.

Matched successful seeds1,3,4 only:

| Descriptor | Control | Edited |
|---|---:|---:|
| Notes |42.3333|42.3333|
| Mean absolute adjacent-event pitch interval |8.2605|9.0100|
| Above-octave adjacent interval fraction |0.21848|0.26601|
| Distinct pitches |20.0000|21.3333|
| Repeated adjacent pitch fraction |0.02530|0.00775|
| Silence ticks |2682.6667|2682.6667|

The recurrence construction did not reduce large leaps: both interval descriptors increased. These intervals follow event/member order, not inferred melodic voice leading. Lower repeated-pitch fraction and greater pitch variety do not imply more appealing melody. Anchor recurrence is imposed by construction, not learned coherence or tonal cadence.

All non-pitch note fields, non-anchor group fields and every timeline metric match exactly within each completed pair. The report's unmatched complete-only timeline means differ between5 control and3 edited outputs solely because success selects a subset. They are **not a treatment effect on silence or density**. The common-success comparison preserves equal timelines, but still conditions on survival.

## Verification and constraints

Frozen plan SHA256:b7c701198d906b335e3f5524f3c9bf4310592d668b75c0ad7e92ce55fd80599a.

- Run/repeat equal except CPU0.618868/0.353983 seconds; all five private candidate files byte-identical.
- All5 original note/group arrays equal the old Cycle37 outputs, controls unchanged.
- Three edited pairs preserve all ordered nonpitch fields, templates, onsets/deltas and exact occupancy/silence metrics.
- All21 original references reread for independent copy recomputation; original source hashes unchanged.
- Four synthetic tests pass, including incoming/outgoing sustained-note collisions, half-open release legality, empty/no_effect, pitch range, group offsets and joined copy matches.
- Independent parent synthetic audit:100 cases/1788 checks. This separate audit is not claimed to precede the real run.
- No new training sources, fresh evaluations, generation policy adoption, parameter tuning or media publication.

A next hypothesis would need to address cross-group/voice continuity explicitly rather than equating ordinal anchor reuse with melodic return. No such change is implemented or selected here.
