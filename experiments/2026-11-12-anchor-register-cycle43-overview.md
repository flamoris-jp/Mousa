# Cycle43: octave placement lowers a local proxy, not proof of musical appeal

This follow-up uses the same known17 training works and Cycle37 global seeds0–4, with no new music or human ratings. It compares unchanged output, Cycle42 fixed+2 anchor return, and a new octave-register placement. It is exploratory reuse of known outputs, not fresh validation.

## Fixed rule and preserved information

For each C group in onset order, derive pitch class from original A[j modulo len(A)].anchor+2. Enumerate every MIDI anchor0–127 for which all group members fit MIDI0–127. Choose the candidate minimizing distance to the previous output group's anchor, ties choosing the lower anchor. C decisions are greedy; original A is never modified. The previous anchor is a group's minimum pitch, **not an inferred melody voice**.

No next-best search after same-pitch overlap or copy failure. Empty A/C, no-effect and no legal register have separate statuses. All original times, gates, velocities, release velocities, templates, relative offsets and member order remain unchanged. Sustained notes are never cut. Full-output guards retain max256 notes, max3 active voices, no overlapping equal pitches, target9216 and tail≤384.

All three conditions use the same21 original copy references:17 training plus observed640,921,Dowland21,1691. Generated and canonical event order include joins. No source is added to training or newly evaluated predictively.

## Results

All5 controls complete. Both interventions complete on seeds1,3,4 only; seeds0,2 lack A onsets and remain blocked. There is no success-rate gain. All completed outputs pass the fixed copy screen. All failures are retained.

Matched-success means, denominator3 outputs:

| Descriptor | Unchanged | Fixed+2 | Nearest octave |
|---|---:|---:|---:|
| Mean absolute adjacent-event pitch interval |8.2605|9.0100|7.4572|
| Above-octave interval fraction |0.21848|0.26601|0.19319|
| Distinct pitches |20.0000|21.3333|20.3333|
| Repeated adjacent pitch fraction |0.02530|0.00775|0.00775|
| Notes |42.3333|42.3333|42.3333|
| Silence ticks |2682.6667|2682.6667|2682.6667|

Event intervals include simultaneous group members and are not voice-leading trajectories. Lowering the directly targeted anchor-distance proxy is expected by construction and is not independent evidence of coherence, tonal appropriateness or attractiveness.

Entry/internal/exit group-anchor gaps are separately retained per output, with transition counts. The unoptimized C→D exit exposes a limitation: seed4 remains15 semitones under both interventions versus2 in the unchanged control. Seed3 exit is4 after octave placement versus3 unchanged. Thus local continuity can still worsen an exit even when global descriptive averages decrease. No listening preference is inferred.

The unchanged complete-only summaries use5 outputs and edited summaries3; their differing silence means are entirely selection effects. On the common3 outputs, every timeline metric is exactly invariant.

## Verification and honest failure history

- Original plan1c8306… remains unrun. Parent review found a CPU-skipped-row schema bug before fit: downstream3-arm aggregation would raise KeyError. Corrected helper and regression test were frozen in final plan15893d65656bb6fd8cc3dadf421fd51d985707d26291df5e7091180200a7b22f. The anchor rule did not change.
- Five synthetic tests pass. Independent profile audit:5,000 checks,170 ties and231 no-candidate cases.
- Fixed run/repeat match except CPU0.304244/0.316255 seconds; all5 private files byte-identical.
- All original generation states, control outputs and fixed+2 outputs exactly match Cycle42, including all statuses.
- All non-pitch note fields, non-anchor group fields, full templates and timeline metrics are invariant.
- All28 edited C anchors independently match exhaustive legal-candidate enumeration, original-A pitch class and minimum-distance/low-tie rule.
- All21 reference copy checks recomputed, original hashes unchanged.
- An initial shell-transport failure occurred before a process/clearance/output was created; absence was verified and execution retried. It was not a model failure.
- No rule changes after results, production adoption, new human labels, raw media in Git or uploads by this worker.

A future voice-aware or phrase-exit hypothesis would require separately justified representation and independent listening evidence. Neither is implemented or claimed here.
