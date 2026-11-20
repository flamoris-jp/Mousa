# Degree + rhythm learning: bounded research

This experiment combines #17's **learned shared encoder parameters** with
#19's **degree/register semantics**, under a distinct task identity
`mousa.degree-rhythm.experimental.v1`. It is not a continuation of either old
optimizer and does not reinterpret a semitone output head as a degree head.
The old embedding and output head are replaced. All 50 compatible positional,
segment and transformer parameter tensors are copied exactly, with named hashes.
Maidionis Core stays external and unchanged. A warm start with changed token and
position semantics does **not** prove that old musical ability is preserved.

## What is learned

Six task queries share eight preceding events: degree/register, next onset gap,
monophonic duration, projected silence, velocity class and a weak phrase-boundary
proposal. Cardinality and current position within a 4/4 bar are inputs; scale
intervals, tonic, Hz and the current target are not. Heads are conditionally independent for the current event given shared past history;
within-event pitch/rhythm coupling is not explicitly modeled. Phrase is an
auxiliary output/history feature and does not directly impose an audible phrase.
The grid is 1/12 beat, which
can represent straight sixteenths and eighth-note triplets. This is representational
support, **not evidence of learned shuffle or swing styles**.

During generation each event is sampled from model probabilities, then enters
history. No rhythmic pattern is selected and pasted. A deterministic constraint
limits IOI to remaining piece time and combines duration/rest probabilities over
legal pairs summing to that IOI. Notes can cross bar boundaries; exact 4/4 piece
length and nonoverlap are guaranteed by rules, not credited to learning.

## Data and limitations

The protocol is frozen in `experiments/maidionis-rhythm-learning/protocol.json`.
Only existing rights-reviewed PD/CC-BY training families and historical-observed
nontraining families from #17 are eligible. No reserve is read or reassigned.
Take the first eligible eight training and four observed evaluation families in
the pinned existing order; require an explicit constant 4/4 and key. Unknown or
off-scale notes are not snapped. Invalid events break histories.

Highest-onset extraction is a **monophonic projection**, not recovered notation
voices: duration is clipped at the next projected onset. Silence is the gap left
by that projection, not necessarily silence in the full score. Phrase labels are
weak labels from gaps of at least one beat, not annotated phrase structure.
Velocity uses fixed bins. Source performances with constant velocity cannot teach
expressive accent variation. Preserve quantization error, clipping and excluded
windows rather than silently rewriting originals.

The first selected cohort has very sparse nonzero rests and phrase positives.
Their apparent accuracy can be dominated by the zero class. This experiment tests
the wiring and exposes that curriculum deficiency; it cannot demonstrate natural
phrasing. Evaluation families were already observed historically: no fresh test
or broad generalization claim is made.

## Comparison and listening

Frozen seeds 101/102/103 produce eight-bar learned sequences. Each fixed-rhythm
comparison preserves the **exact pitch order and note count**, but uses quarter
note IOI, 3/4-beat duration and constant velocity. Consequently fixed versions may
have different lengths. This isolates timing/accents for listening, not a matched
whole-song causal benchmark. Both variants undergo the existing bounded copy
screen against 128 historical training-family references; blocked samples are
retained privately but not exported or replaced by retries.

Report diversity, repetition, silence and offbeat descriptors separately from
mechanical validity. No scalar 'naturalness score' is manufactured. Human listening
should record A/B/tie/neither plus naturalness, repetition and optional reasons.
No human preference has yet been supplied, and no listening quality is asserted.

## Reproduction

The native target is in `experiments/maidionis-rhythm-learning/CMakeLists.txt`.
Use the documented external Core pin and CPU LibTorch 2.5.1 profile from #17/#19.
`prepare.py --help` describes pinned private inputs; it writes exclusively to a
new output directory. `model train DATA OUT LEGACY` fits 60 fixed steps, and
`model serve MODEL` accepts bounded JSON-line inference rows.
`generate.py --help` describes private generation inputs and copy references.
No private paths, raw MIDI, source event streams, tensors or media belong in Git.

This is not a Runtime service, a Cantabile editor, production checkpoint lifecycle,
or a licensed release of source/learned data. No Files connector, merge, deployment,
GPU or paid operation is involved.

A subsequent [whole-piece rhythm-first comparison](RHYTHM_FIRST.md) keeps both
new arms at eight bars and tests a complete timing plan before pitch filling.
The original experiment and its results above remain unchanged.
