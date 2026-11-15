# Degree-native generation

The primary representation is now **which scale degree, in which repetition
register**, rather than a number of semitones. The AI selects ordinal labels;
the deterministic scale/key renderer converts them to cents, Hz and MIDI.
Scale interval tables are rules, not examples mixed into model training.

AIが「音階の第何音か」を選び、その後にスケールとキーを適用します。
同じ第2音でも、長音階なら200セント、24等分なら50セントになります。
微分音、主音の微小オフセット、基準調律の変更も描画段階で扱えます。

## Semantics and compatibility

The new immutable task ID is `mousa.absolute-degree.experimental.v1`.
`Degree.degree` is zero-based: 0 is the first note, 1 the second. `period` is
-1, 0 or +1 relative to the tonic's register. The bounded numerical label is
`(period+1)*64+degree`, yielding a 192-class head with unused degrees masked
for the selected scale size (1..64). No label means a semitone interval.

Model input is `[CLS, cardinality, eight previous degree labels]`.
Cardinality is an integer count, not a pitch table. The model never sees
the scale's cents, tonic, MIDI pitch or concert tuning. Thus the same generated
ordinal stream can be rendered with multiple scale shapes of the same size
and with any supported key. A different scale size changes the model's
cardinality input and legal degree labels.

The external unchanged Maidionis encoder supplies the numerical implementation:
256 hidden, four layers/heads, FFN1024, 259-token vocabulary, 192 outputs,
zero dropout, CPU FP32. This composition has a distinct model/task identity.
Historical 49-class semitone checkpoints are explicitly rejected; their class
numbers and embedding tokens cannot be relabeled as degrees. The older
`mousa.scale_generation` path remains a documented legacy experiment, not a
microtonal fallback for this path.

## Python semantics

```python
from mousa import Degree, Key, ScaleCondition, decoded_pitches, load_catalogue

catalogue = load_catalogue()
labels = [Degree(0).label, Degree(1).label, Degree(2).label]
major = ScaleCondition(catalogue["major_12tet"], Key.from_name("C4"))
micro = ScaleCondition(catalogue["equal_24_test"], Key.from_name("C4"))
assert [x["pitch_cents"] for x in decoded_pitches(labels, major)] == [6000,6200,6400]
assert [x["pitch_cents"] for x in decoded_pitches(labels, micro)] == [6000,6050,6100]
```

Unknown degrees fail rather than snapping to the nearest pitch. Repetition uses
the scale's declared period, including a non-octave period. The renderer keeps
cents until choosing a MIDI note plus pitch bend and declares RPN sensitivity
explicitly. It fails on unsupported MIDI range instead of changing the degree.
The current exporter is monophonic; chords and ornaments remain future work.

`degree_for_pitch(condition, nominal_cents)` provides a strict annotation
helper for future reviewed music data: the scale/key must be supplied, and
off-scale, ambiguous or out-of-register notes are rejected. It does not infer
keys or silently fix a source melody. Source rights, verification, family
lineage and train/selection/test splits still require the normal intake review.
Pitch cents here use the condition's concert reference; they are not Hz.

## Build and try

Use the external Core and pinned CPU toolchain documented in
[the native build instructions](../experiments/maidionis-scale-generation/README.md).
The same CMake composition now also builds target `degree_model`:

```sh
cmake --build build/scale-generation --target degree_model -j1
PYTHONPATH=src python examples/degree_model_trial.py \
  --binary build/scale-generation/degree_model --out /private/new-degree-trial
PYTHONPATH=src python -m mousa.degree_generation \
  --binary build/scale-generation/degree_model \
  --model /private/new-degree-trial/model \
  --scale equal_24_test --key D4 --tonic-cents 33.333 --a4-hz 442 \
  --out /private/new-degree-candidate
```

Reconfigure the CMake source directory before building when upgrading an older
build that does not know the new target. Every output directory must be new.
Only trusted locally created/native archives should be loaded; a digest is
integrity evidence, not a sandbox for hostile archive content.

The example trial freezes its plan before fitting, creates **original ordinal
motifs**, trains for 60 fixed AdamW steps and saves new model/optimizer archives.
It does not read any scale MIDI or external music corpus. Four motif families
are instantiated at cardinalities5/7/24; all 384 windows are train-only, and
variants retain the same family. This is a mechanical learning/reload test,
not musical training material of proven quality or a held-out evaluation.
No optimizer-resume or full education lifecycle qualification is claimed.

The generation wrapper checks task/model hashes, every ordinal label, zero
probability for nonexistent degrees, masked-logit normalization, sampling and
full chosen-history feedback. Key/scale rendering occurs only after this
validation. Default output is 64 notes at fixed half-beat spacing, 100 BPM,
PPQ480 and exactly15,360ticks (eight4/4bars including the last release gap).
These timing rules are deterministic, not learned long-form structure.

The trial obtains one ordinal stream per cardinality and renders six catalogue
scales at C4, one MIDI per scale. Key changes are checked in memory rather than
stored as duplicate training material. Traditional scale entries retain their
explicit 12-TET approximation labels; 24-EDO remains a mathematical test grid.

## Verification and next learning work

Run the ordinary unit suite and independently parse the generated MIDI:

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
python tools/verify_scale_pack.py /private/new-degree-trial/midi
```

Actual fit/render acceptance is recorded in
`experiments/maidionis-degree-generation/verification.json`. It includes the
new model's identity, train-only measurements, microtonal note count, independent
MIDI parsing and legacy-checkpoint rejection. No musical-quality or fresh
generalization conclusion follows from fitting these tiny motifs.

Next, annotate rights-reviewed music with explicit scale/key and ordinal
targets, preserving original families and split roles, then compare learned
phrase behavior. Do not feed arbitrary source MIDI into this new task or
rewrite an old checkpoint manifest to bypass the semantic boundary.
