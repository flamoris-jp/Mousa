# Cycle47: collision feasibility and singleton fallback are different interventions

This is a frozen2×2 replay of six already-observed Cycle46 candidates. There is no model fit, new generation, new predictive music evaluation or human rating. Historical known/new_random labels identify the old cohorts only; all six are now observed.

## Fixed policies

Both methods use the same original first/third silence segments, threshold192 ticks, original-A ordinal pitchclass+2 and entrance/internal/exit anchor L1 objective with lexicographic low ties. The original post-selection collision rejection remains a control.

The constrained optimizer retains last anchor plus every active selected note pitch/end in its DP state, rejects collisions against all fixed notes, and uses half-open intervals. Only states with identical lastanchor/active state can be dominated by lower cost/lex path. All legal MIDI candidates remain available. State cap4096, transition cap200000 and CPU60 are hard research bounds; exceeding them is failure, not a partial optimum. Copy screening remains after selection with no search for another copy-free path.

The second factor either requires≥2 source groups or permits exactly1 source group as **single-pitch-class repetition fallback**. Empty source and target<2 groups still reject; no other segment is substituted. Fallback completion is counted separately from multi-group return completion.

All original times, gates, velocities, templates, order, note count, rests and EOT remain fixed. Max3 active voices, max256 notes, MIDI0–127 and22 original copy references are unchanged.

## All outcomes, denominator6 per policy

| Policy | Multi-group complete | Singleton fallback complete | Other |
|---|---:|---:|---|
|Old postreject, strict|3|0|2 short source,1 collision|
|Collision-constrained, strict|4|0|2 short source|
|Old postreject, singleton allowed|3|0|1 short target,2 collision|
|Constrained, singleton allowed|4|1|1 short target|

45001 becomes feasible with collision constraints; its optimum rises25→37. The earlier25-cost path overlapped equal pitches and remains invalid. This is improved feasibility under a different optimization problem, not a lower-cost or more attractive result.

46602 completes only as constrained singleton fallback; its unconstrained12-cost path collided, while the feasible optimum is42. It is not reclassified as multi-group phrase return. 45000 still fails: allowing its one-group source exposes a third segment that is also too short. No rescue segment was selected.

The three previously successful candidates retain objectives24,18,16. Maximum search used1210 states and26520 transitions, below fixed bounds; there were no budget failures. No accepted output was copy-flagged.

Historical cohorts remain separated in results. All-four multi-group common seeds are45002 in the old known cohort and46600/46601 in the formerly-new cohort. This common set excludes the newly feasible cases: complete-only aggregate comparisons therefore have selection effects. All per-candidate metrics and status denominators remain available.

## Verification and limits

- Final plan SHA5b82bc058ce3139164e2a376d242202c287578c193594221625417b87b721791 fixed before replay.
- Initial/repeat identical except CPU0.677302/0.653251sec; all6 private files byte-identical.
- Old strict postreject status and every available note/group output exactly match Cycle46 for all6 candidates.
- Fifteen accepted condition-output instances pass full temporal/nonanchor/template invariance, exact timeline equality, whole-output note safety and both-order22-reference copy checks. These are not15 independent samples.
- Independent profile:100 exhaustive Cartesian fixtures plus fixed infeasible/no-register/budget cases. Five worker tests cover nonadjacent sustained-state constraints, future fixed collisions, budget stop, fallback classification and old output parity.
- Independent output audit:1,647 checks on15 accepted condition outputs from6 unique inputs; five unique constrained solutions verified by separate depth-first enumeration with unconstrained suffix lower bounds, at most89 explored nodes.
- Original source bytes and all previous results remain unchanged. No source addition, playback, listener preference or deployment.
- L1 anchor movement is a group-minimum-pitch proxy, not voice leading or harmonic truth. Feasibility gains and imposed recurrence do not establish musical appeal.
- The historical cause diagnosis is included separately; the source constraints and failure meanings were not changed after results.
