# Cycle30: full-length source screening and twelve-work training

## Full-length comparison without changing similarity criteria

The previous512-interval resource guard prevented comparison of Joplin's full
1394-note staff. A new, separate2048-interval profile now computes the same exact
normalized Levenshtein score over pitch intervals. The exact-eight-onset local
rule and whole-line0.80threshold are unchanged. No notes are removed, segmented,
quantized or approximated to obtain eligibility.

The profile, formula, limits and tests were registered before real Joplin
comparisons. It uses two rolling rows over the shorter interval sequence, plus
interval arrays. Working-row memory is O(min(n,m)); total array memory O(n+m)
and time remains O(n*m). This is a bounded extension, not an unbounded or
linear-time corpus search. More than2048intervals still fails explicitly.

Forty seeded short synthetic pairs and the old512boundary agree exactly with
the original helper. Long identity, length imbalance and exact0.80boundary cases
pass. The short-side memory test peaks below300KB for2048versus32intervals;
this is a fixture-level allocation check, not a production resource guarantee.
Original helper, models and earlier frozen drivers remain unchanged. A new
prepare wrapper binds the new comparison profile, then reuses the existing
rights, assignment, support and run-review checks. A transitional legacy-shaped
prepare plan is retained privately; final plan hashes identify the reviewed run.

## Actual corpus growth

First, Joplin263was added intact to the nine-work exploratory corpus:10works,
2536selected-track events. Then two newly acquired and rights-reviewed source
cohorts were added: Beethoven904/Samelis628events and Tchaikovsky2080/McNamara
99events, giving12works/3263events. All are original MIDI bytes; these keyboard
staffs can contain chords and must not be advertised as isolated melodies.

Each addition has exact source URL, acquisition time, hash, paired-source license,
historical edition evidence and limitations in its ledger. Beethoven's1862
BreitkopfNo193and Tchaikovsky's1904Schirmer/Ruthardt incipits were checked.
Ruthardt's1849–1934dates are separately recorded; the scan is a branded
reproduction without its original title leaf, not proof of exact physical-copy
identity. Source PDdedications concern the contributed encoding, not ownership
of reproduction branding. Composer, historical edition and MIDI evidence remain
separate. Publisher overlap with earlier sources is retained as a confound.

The historical reserved/unfitted rights snapshots remain immutable. Separate
Joplin and two-new-cohort actual-use records now point to fitted results.
Schubert/Foster previously reassigned material remains openly exploratory.
Adam640/Chopin921remain untrained, already observed diagnostics. No fresh test
set or real human preference labels were acquired. Existing blocked1692/804/
1741remain excluded. Carcassi and other uncertain-rights candidates remain pending.

## Frozen screening and comparison conditions

For10works,20cross-split and45within-training pairs were fully compared;54old-
supported pairs agree with the original helper and11long pairs receive complete
exact scores. For12works,24cross-split and66within-training pairs were checked;
65old-supported pairs agree and25long pairs receive complete scores. No gate
flags occur in either experiment. Within-training grouping still follows source
families, not absence of matching intervals. These are not counts of independent
composers, contributors, genres or styles.

Separate assignments/plans and bound review decisions precede each fit. The
factorized and contextk4models, fixed support, raw event weighting, seeds0–4,
9216-tick horizon, trailing-rest384limit and constrained generator are unchanged.
All source events are in support. Source polyphony can reach4while the generator
caps3; no full piano performance reproduction is claimed. Meter/pickup timing
is preserved in input, but the timing model still has no meter condition.

## Results

Equal-work timing NLL on the two observed diagnostics, lower being better:

| Training works / events | Factorized | Contextk4 |
| --- | ---: | ---: |
| 5 /444 | 8.769905 | 7.859410 |
| 9 /1142, cycle29 | 9.491853 | 8.429055 |
| 10 /2536 | 9.188327 | 8.116754 |
| 12 /3263 | 9.055696 | 7.990111 |

More material after9works improves the mean here, but neither new corpus beats
the5work mean. The per-work result matters: relative to5works, Adam640improves
and Chopin921worsens under both models at10and12works. Going10→12slightly
worsens Adam and improves Chopin. Do not call this universal generalization.

Five generated candidates per condition give these complete-only means:

| Works | Notes | Distinct pitches | Same-pitch repetition | Overlap-onset fraction | Mean absolute interval | Rest fraction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 23.2 | 10.0 | 0.309123 | 0.131989 | 3.066789 | 0.333333 |
| 10 | 52.8 | 25.6 | 0.064155 | 0.371321 | 6.053559 | 0.072917 |
| 12 | 46.2 | 23.8 | 0.084149 | 0.358148 | 6.470203 | 0.109722 |

Every candidate completes; no fixed exact8copy flag occurs against all assigned
training sources plus both diagnostics. Lower repetition is accompanied by more
notes, overlap and leaps. This could be undesirable for a singable melody and
is not evidence of greater appeal. Joplin alone supplies1394/2536events at10works
and1394/3263at12works. Raw-count weighting, texture and source mix are confounded
with quantity. Long files and repeated sections are not independent examples.

Base5predictions/notes reproduce previous results. Repeat outputs and all metrics
match, excluding measured CPU time. Independent audit recalculated all90pairs
for12works and all14reference output-copy sets; max3voices, no active same-pitch
overlap, timing bounds and tail limit hold. There are15unique condition-seed
outputs here, not20independent samples because base5is repeated. No new MIDI
export, real Cantabile audition or human judgment is claimed; notes remain private
JSON. Copy-screen zeros are not originality clearance.

## Storage handoff and next research

The owner designated a material store and a separate authorized transfer process
received a fixed snapshot of12originals totaling91,230bytes plus16metadata JSON
files. All original hashes were verified before handoff. No training audio is
included. Transfer completion, destination readback and durability are separate
checks owned by that process; this experiment does not claim they succeeded.
Research did not modify original files or the handed-off snapshot.

The next useful control is source/event balancing or explicit texture/voice
handling, not blindly maximizing note count. Broad metadata-driven discovery
continues, but12mostly Western historical works are not a large or culturally
diverse corpus. The2048comparison profile still has a stated scale limit.

## Verification

Fullsuite270discovered,269passed,1existing actualAudioAnalyzer integration skip.
Dependency-free270discovered,232passed,38expected optional skips. Compileall and
diff checks pass. The independent audit ran its checks before the final two
record-binding tests were added; the final270suite includes both. No main merge,
public source/media release, deployment, paid compute or GPU use.
