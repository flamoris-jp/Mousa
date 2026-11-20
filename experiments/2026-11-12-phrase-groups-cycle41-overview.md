# Cycle41: fixed return editing fails at sustained-note boundaries

The exploratory hypothesis was whether a fixed two-bar return with +2-semitone variation could be inserted into existing eight-bar group outputs without cutting sustained notes. It was not a new hypothesis that repetition is attractive: Cycle6 already tried handcrafted transposed forms.

## Fixed comparison

The unchanged global timing model was fitted to the same 17 training works (4,319 notes / 3,428 groups). Seeds 0–4 reproduced the **already generated and diagnosed Cycle37 pool**. This is a new editing policy on known outputs, not prospectively unseen generation or independent evaluation.

Control: unchanged eight-bar output, PPQ384, 6/8, target9,216 ticks, tail≤384.

Intervention: replace generated C onsets in [4,608,6,912) with all A groups from [0,2,304), shifted +4,608 ticks and +2 semitones. Preserve each copied onset, gate, velocity, release velocity and member order; preserve its relative rests. C removal would be generated-output editing, not deletion of training originals. It would change note count, register, density and silence, so it would not isolate repetition's musical effect.

Any note spanning a fixed boundary at2,304,4,608 or6,912 rejects the intervention. Notes ending exactly at a boundary are legal. No clipping, boundary search, seed replacement or shift adjustment. MIDI pitch0–127, max256 notes, max3 voices, no same-pitch overlap and whole-group reconstruction are checked.

Both conditions use the same exact eight-note interval copy screen over all17 originals plus observed640,921 and Dowland21,1691, including joined output and canonical note order. Internal intended repetition does not exempt source matches.

## Actual result

| Outcome | Unchanged control | Protected replacement |
|---|---:|---:|
| Candidates | 5 | 5 |
| Complete | 5 | 0 |
| Boundary-sustain blocked | 0 | 5 |
| Complete source-copy flagged | 0 | 0 |
| Common complete seeds | 0 | 0 |

All five interventions were blocked before an edited output existed. Thus zero copy flags for complete edits is **not evidence of safety or success**: there were none.

Fourteen note/boundary crossings were found:4 at2,304,4 at4,608,6 at6,912. All generated source candidates remain unchanged. Seed0 was blocked only by a note from6,380 to7,148 crossing the final replacement boundary; all individual failures remain in the results.

There is no treatment mean or preference comparison to report. This negative result shows the fixed edit was infeasible in this particular known five-output pool. It does not establish that repetition is undesirable, that all music needs these boundaries, or a population failure rate.

## Verification and next hypothesis

- Frozen plan SHA256:5f6e62034a10b4bc68d6609ee631ef28a1f8760921598f547880a6b9485fdd57.
- Initial/repeat reports identical excluding CPU0.280769/0.317816sec; all five private output files byte-identical.
- All five original note and group arrays exactly equal Cycle37 global outputs.
- All original MIDI bytes unchanged. No new train sources, predictive observations or human ratings.
- Five synthetic tests pass: all-field/order preservation, exact group reconstruction, rests, legal half-open endings, each sustain boundary, joined copy detection, emptyA, pitch and note/voice bounds.
- Independent parent synthetic audit:100 cases/700 checks, performed separately; not claimed to precede this real run.
- No generated notes, MIDI or audio in Git; metadata-only snapshot prepared for separate archival.

A future, separately planned comparison could condition generation on legal phrase-boundary sustain behavior instead of editing finished outputs. It would change the generative law and could introduce artificial silence or short gates; those costs would need explicit controls. That proposal is **not implemented or selected here**. No feedback was inferred from the unanswered earlier listening request.
