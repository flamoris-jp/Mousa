# Cycle32: upper-onset selection is not melody extraction

## Prospective design

Frozen plan: `2026-11-12-onset-projection-plan.json`. The existing 12 originals,
3,263 staff-note events, and observed diagnostic works 640/921 remain unchanged.
Four conditions cross full staff versus one highest pitch per exact onset with
event-proportional versus equal-work weighting. All weighted note masses are
3,263; transition mass and local context support are not held constant. Five
seeds per condition, identical generator, settings, original-source copy guard
and bounded CPU budget. No condition-specific retries or listening selection.

Selected note objects retain their original onset, end and velocity. This is a
lossy selection, not a voice separator, annotated melody or monophonic repair.
Earlier notes can continue sounding beneath later selected notes.

## Measured loss

The selection retains 2,421 events, removing 842 events and 208,320 summed gate
ticks. Sounding-union coverage falls by only 384 ticks, all in Beethoven904.
Most removed notes share onset with a retained note, so near-preserved sounding
time does **not** mean near-preserved musical information. Harmony and inner
voices have been discarded. Vocabulary decreases from 36 to 35 pitches, and
unweighted transitions from 3,251 to 2,409.

An independent per-tick occupancy implementation checked every original work,
selected-note membership, highest-onset pitch, distinct-onset counts and the
coverage loss. See `2026-11-12-onset-projection-independent-review.json`.

## Results, means over five completed seeds per condition

| Condition | Timing NLL | Overlapping onsets | Mean absolute pitch interval | Same-pitch repeats |
| --- | ---: | ---: | ---: | ---: |
| Full staff, event proportional | 7.99011 | .46007 | 6.66020 | .10656 |
| Full staff, equal work | 7.88658 | .27274 | 4.21033 | .21981 |
| Upper onset, event proportional | 8.04924 | .17712 | 5.35172 | .12662 |
| Upper onset, equal work | 8.01776 | .14271 | 5.39933 | .16074 |

NLL is equal-work mean teacher-forced timing loss on the same two **previously
observed original staffs**, not a projected-melody target or fresh holdout.
Lower is better for that timing task only. Projection worsens it in both
weighting conditions. Overlap decreases, but intervals become larger under
equal-work weighting. Therefore the hypothesis that upper-onset selection
universally improves continuity is not supported. Less overlap is not inherently
more musical, and the removed harmony may be valuable.

All 20 candidates completed within the CPU budget with no fixed exact-eight
pitch-sequence flags or structural safety failures. The two full-staff conditions
exactly reproduce cycle31 predictions and generated note bytes. The entire
comparison repeated identically except CPU timing (initial about 2.76 CPU seconds).
These small sample counts do not establish robust effect sizes or listener appeal.

## Next questions

Prefer representations that preserve onset groups and voice uncertainty over
silently promoting the highest note to ground truth. A future study could keep
chord context while learning a separately human-approved melody, or compare
explicit voice-leading hypotheses. No such annotation or model is claimed here.
Corpus acquisition and rhythm-specific data admission are separate from this
representation experiment; do not count reserved drum recordings as added
pitched training works.
