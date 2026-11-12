# Cycle33: performer-grouped rhythm pilot and16 pitched works

## A separate drum prediction task, not melodic learning

The official Groove MIDI originals remain unchanged. Twelve complete recordings
from drummers1–6 supply5,034 training events. Four recordings from drummers7–8
provide2,758 validation events; four from drummers9–10 provide3,850 test events.
No drummer or session crosses these new splits. The original release splits
remain provenance only. All40 known shared-pattern evaluation recordings remain
reserved and unused. Whole performances are selected by fixed hash order, at
most two per drummer and4,096 events per performance; eight oversized recordings
are not truncated. Some selected fills contain only six or fourteen events.

The fixed screen checks original hashes and full instrument/onset signatures,
exact tempo/offset-normalized sequence fingerprints, and comparison-only
8-event instrument/coarse-IOI shingles. Of12,416 selected-to-other-split comparisons,
67 have weak shared windows; no selected item has the fixed strong unresolved
match. These are limited screening results, **not proof that all musical patterns
are independent**. Common drum figures can legitimately match, and variation
can evade the screen. No thresholds or candidates were tuned to model scores.

The prediction target is exact inter-onset ticks in native PPQ480, with positive
support0..30,720. Drum key numbers identify instruments, not pitched melody.
Control: prior-smoothed global IOI counts. Comparator: previous-instrument local
counts plus four global-empirical pseudo-counts and total uniform prior mass one.
Initial/unknown contexts use the control. The exact equation, code, tests,
20 IDs/hashes/splits, rights and screening artifacts were fixed before fitting.

## Negative result retained

| Held-out split | Control pooled NLL | Previous-instrument pooled NLL |
| --- | ---: | ---: |
| Validation,2 drummers /4 recordings | 5.165146 | 5.462280 |
| Test,2 drummers /4 recordings | 6.353313 | 6.898952 |

The comparator is worse on **all eight** held-out recordings. All6,608 target
events are scored without clipping or quantization. Repeated results match
except CPU timing (approximately0.253 and0.276 CPU seconds). Original hashes
remain unchanged. These eight recordings are now predictively observed, never
fresh again. No generated music or subjective evaluation is claimed.

The source-style composition is uneven: train has nine rock recordings and one
each blues, latin and reggae; test has two jazz and two rock recordings. These
are source-supplied labels, not invented impressions. Style, performer, event
count and recording length are confounded; none is established as the cause.
Same-tick source ordering also affects the previous-instrument feature. Note
pairing, gate/velocity/controller modeling and audio quality are outside this
pilot. A rhythm generator is not implemented by a successful prediction run.

### Posthoc error decomposition, not a new experiment

Reconstructing the same frozen training counts reproduces all16 recorded
performance×condition NLL sums exactly. No held-out previous-instrument label
is unknown. The largest loss occurs when an IOI was seen globally but not after
that particular previous instrument:306 validation events and853 test events,
with mean context-minus-control loss about+3.878 and+3.855 nats. Locally observed
IOIs improve on average. Global-unseen IOIs total21/2,758 validation and254/3,850
test events. This identifies sparse conditional support in this fixed model as
an error category, not a demonstrated causal effect of genre or musical appeal.
No smoothing parameter, source choice or model was changed after seeing scores.
A future prospectively fixed study can test stronger backoff or a reversible
coarse-timing/residual representation, keeping the original ticks intact.

## Pitched corpus grows to16 works /4,150 events

Original Haydn186 upper staff (383 notes) and Rameau487 upper staff (313 notes)
were acquired with explicit typesetter PD notices and historical incipit review.
Rameau is a new named composer/contributor/editor series; Haydn has documented
editor/contributor/publisher links to pending or blocked sources. Those sources
remain excluded. Eight within-training similarity links remain recorded.

A separate bounded32-work profile prevents repeated per-small-increment capacity
patches. It retains the original probability formula, within-work boundaries,
100,000 aggregate event limit, old source gates, fixed2048 interval screen and
small CPU budget. Actual16-work synthetic construction/generator preflight runs
before original source access. Independent630 probability comparisons and48
seeded legacy-output comparisons passed. Historical models/plans are unchanged.

The fixed5-versus16 comparison, on the same **already observed** Adam640/Chopin921
diagnostics, gives context NLL7.859410→7.368052 and factorized NLL8.769905→8.489451.
This timing prediction improves, while mean pitch interval3.07→7.22 and overlapping
onsets.132→.371 increase. Both conditions complete5/5 generations, with zero fixed
copy flags; repeat reports and all10 generated-note files match, originals unchanged.
No claim of greater musical appeal, legal originality clearance, or fresh
holdout generalization follows. Quantity, repertoire and event weighting change
together. Initial CPU time was about0.770 seconds.

## Preserve polyphonic information before choosing a voice

An additional note-only onset-group view keeps every selected note, original
index, onset/end, pitch and velocities. On the14-work starting corpus,3,454 notes
form2,610 groups and restore the exact original note state/order, with identical
repeat reports. Independent synthetic checks cover up to4,096 notes. Unlike the
previous highest-onset selection, this view loses no selected notes. It does not
identify the true melody, infer voices/chord function, or replace original MIDI
metadata/channel-event order. No grouped-event model is claimed yet.

## Storage and limitations

Versioned metadata distinguishes12 drum training recordings,8 observed diagnostic
recordings and1,130 unused recordings (including40 reserved shared-pattern
examples). The original Groove ZIP is not re-uploaded or altered. New pitched
originals and separate experiment metadata are handed to the owner-designated
store for full read-back verification, with prior snapshots unchanged. A handoff
alone is not reported as completed storage.

No real human labels, main merge, deployment, public media/corpus release,
GPU operation or paid compute. Fixed results and failures remain visible.
