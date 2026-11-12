# Cycle46: silence-defined pitch return, with unchanged rests

Read-only diagnosis separated leading, internal and trailing silence in the old21 candidates and18 training sources. Sparse outputs sometimes stemmed from7,872-tick leading rests; internal long gaps also occurred. Source first onsets include Schubert1558 at7,872, Foster370 at9,216 and Purcell2243 at12,672. These originals were not trimmed. Parent density diagnosis and worker full18-source/21-output diagnosis overlap in scope; both are descriptive, not separate independent experiments.

The intervention uses existing silence as boundary information, **not a method to reduce silence or increase density**. A fixed gap≥192 ticks of complete silence splits groups, using maximum end over every prior note. Leading/trailing silence creates no empty segment. This arbitrary halfquarter threshold is not verified phrase annotation.

## Frozen comparison

The same18-work mass-controlled raw group model generates one pool, with unchanged control and pitch-only return. Original segment1 supplies ordinal-modulo anchor pitch classes+2 to segment3; both must contain≥2 groups. Missing/short segments reject, with no searching for another. Whole-segment DP chooses legal octaves considering entrance/internal/exit, lexicographically low ties. All times, gates, velocities, relative group offsets, order and rests remain intact. Chosen-path overlap/copy failures reject without alternate paths.

All22 original references, MIDI0–127, max256 notes/max3 voices, target9216/tail384 and both-order copy checks are unchanged. No new source enters training, and no original meter is rewritten. The model remains meter-unconditioned.

Known seeds45000–45002 are separate from new-random46600–46602, fixed before their generation. The latter were absent from tracked seed-field history, not proven unused elsewhere, and are not new independent music or human evaluations.

## Actual results, separated cohorts

| Cohort | Controls complete | Edited complete | Failures |
|---|---:|---:|---|
|Known3|3|1|45000 source segment too short;45001 same-pitch overlap|
|New-random3|3|2|46602 source segment too short|

No failed candidate was replaced. All successful outputs passed the22-reference screen. The same-pitch rejection illustrates that preserving group templates does not automatically protect cross-group sustained pitch relationships.

Matched successful known seed45002: event pitch gap7.88235→7.88235; distinct pitches19→20; repeat fraction0.05882 unchanged. Matched new-random seeds46600/46601: gap8.84276→7.85650; above-octave fraction0.22912→0.19503; distinct pitches24→26; adjacent repeated-pitch fraction0.01136→0.04598. These are only1 and2 selected outputs, respectively.

Every successful pair has exactly equal note count, temporal/velocity fields, templates and occupied/silent timeline. New matched pairs retain3,248 silence ticks on average; known pair retains2,752. Differences between unmatched complete-only means are selection effects, not improved rest distribution. Imposed anchor recurrence and lower optimized pitch-gap proxies do not establish attractive phrasing or voice leading.

## Verification

- Frozen final plan SHA e769ff378d452234ca97f79a4dfd775f9ca39029f89cd52a41bf8072ff08cb3e.
- Initial/repeat reports match except CPU0.680510/0.397436sec, all6 private candidates byte-identical.
- Known controls and full generation states exactly match Cycle45 raw18.
- All successful nonpitch note and nonanchor group fields and full timeline metrics match exactly. Full output safety/copy checks recomputed; originals unchanged.
- Seven synthetic tests cover all-prior sustained frontier, simultaneous members, gaps0/191/192/193, leading/trailing silence, fixed first/third short rejection and preserved temporal fields.
- Parent independent segmentation audit:200 synthetic cases/1,284 checks; independent output audit148 assertions verifies all6 partitions, reverse DP choices and the actual rejected collision.
- Source fit conditions, threshold, segment numbers, shift and seeds were not changed after outcomes. No actual listening, ratings, production adoption or media publication.

A future rest-distribution intervention would need a different explicit hypothesis and controls. This experiment deliberately did not perform one.
