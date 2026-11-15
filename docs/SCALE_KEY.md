# Experimental scale and key conditions

Mousa can now describe a scale independently of its tonic, enumerate exact
scale-degree pitches and mark eligible pitch candidates. It can export original
monophonic ascending/descending MIDI exercises for inspection. This is a
music-specific Python prerequisite for conditioned experiments, not a newly
trained AI or an accepted Maidionis/Cantabile wire contract.

スケールの形と主音を分離します。音階名・地域や用途のタグ・出典を持つ
数値定義から、キーを指定して自作の確認用MIDIを生成できます。
コード進行・装飾・自動的な調判定・追加学習はこの段階に含めません。

## Parameters and meaning

| Field | Meaning |
|---|---|
| `scale_id` + `scale_sha256` | Exact registered scale definition; an ID alone cannot silently select changed intervals |
| `intervals_cents` | Sorted offsets from the tonic, starting at 0; repeated upper endpoint excluded |
| `period_cents` | Repetition interval, normally 1200; not hardcoded to an octave |
| `key.tonic_midi` | Integer anchor in 0..127; scientific C4 = MIDI 60 |
| `key.tonic_offset_cents` | Additional tonic offset in -100..100 cents |
| `key.reference_a4_hz` | Independent reference tuning, initially bounded to 300..600 Hz |
| `traditions`, `genre_tags` | Non-exclusive discovery metadata, not genre rules or aesthetic labels |
| `approximation`, `source_urls` | Exact interpretation/limitations and consulted references |

Pitch targets are degree + repetition index, not rounded MIDI integers.
Nominal cents = `100*tonic_midi + tonic_offset_cents + period*period_cents + intervals_cents[degree]`.
Frequency = `reference_a4_hz * 2**((nominal_cents - 6900)/1200)`.
Concert tuning therefore does not change which degree belongs to the scale.

The catalogue has six initial entries, not an exhaustive world-music database:

| ID | Offsets in cents | Interpretation |
|---|---|---|
| `major_12tet` | 0,200,400,500,700,900,1100 | Major in twelve-tone equal temperament |
| `natural_minor_12tet` | 0,200,300,500,700,800,1000 | Natural minor; no harmonic/melodic-minor alterations |
| `major_pentatonic_12tet` | 0,200,400,700,900 | Yonanuki-major / major-pentatonic pitch set |
| `ryukyu_12tet` | 0,400,500,700,1100 | Common Ryukyu reference, explicitly 12-TET approximation |
| `miyako_12tet` | 0,100,500,700,800 | Miyako pitch-set reference, explicitly 12-TET approximation |
| `equal_24_test` | 0,50,...,1150 | Original mathematical 24-EDO test; no traditional-style claim |

Intervals were independently encoded as numerical facts from Toru Kato's
[Meiji University teaching reference](https://www.isc.meiji.ac.jp/~katotoru/ongakutokagaku.html)
and [music21's scale documentation](https://music21.org/music21docs/moduleReference/moduleScale.html).
No source MIDI, performance, score, article text or Scala archive was copied.
The [Scala format](https://www.huygens-fokker.org/scala/scl_format.html) is a
reference for preserving cents rather than reducing every scale to integer
semitones; this change does not implement an SCL/KBM importer. References were
checked on 2026-11-15. Source sites retain their own rights.

Traditional tuning, variants and melodic behavior are not captured by one
pitch set. The catalogue tags do not establish that a composition belongs to a
tradition. Additional scales need their own named variant, source and tuning
interpretation. Unequal, direction-dependent and context-dependent tuning must
not be mislabeled as 24-EDO.

## Python use

```python
from mousa import Key, ScaleCondition, load_catalogue

catalogue = load_catalogue()
condition = ScaleCondition(catalogue["ryukyu_12tet"], Key.from_name("D4"))
parameters = condition.to_dict()
assert condition.pitch_cents(0) == 6200
assert condition.candidate_mask([6200, 6300, 6600]) == (True, False, True)
assert ScaleCondition.from_dict(parameters) == condition
```

The closed experimental condition contains only scale identity/digest and key.
`candidate_mask` reports scale eligibility; it does not choose a note or apply
a model's softmax. An all-false result is valid and requires an explicit caller
decision. It never substitutes a nearest note. To preserve microtones, future
model heads should select degree/period or another explicitly continuous-pitch
representation. An integer-semitone output head cannot emit the missing pitches
merely by receiving these conditions.

PR #14's frozen 49-class interval diagnostic and its metrics remain unchanged.
It has not been retrofitted to use this condition. The next conditioned learning
experiment must bind the new input/target semantics, data and baselines before
fitting. Real training works need verified source-family splits and explicit
scale/key annotation; this catalogue does not automatically label them.

## Original MIDI fixtures

From the repository root, with Python 3.11+:

```sh
PYTHONPATH=src python -m mousa.scale_midi --scale ryukyu_12tet --key D4 \
  --out /path/outside-git/new-ryukyu-D4
PYTHONPATH=src python -m mousa.scale_midi --scale equal_24_test --key C4 \
  --tonic-cents 33.333 --a4-hz 442 --out /path/outside-git/new-microtonal-test
PYTHONPATH=src python examples/export_scale_examples.py \
  --out /path/outside-git/new-scale-fixture-pack
```

Every output directory must be new. The pack contains one canonical C4 exercise
per scale: six MIDI files plus JSON sidecars and a SHA-256 manifest. Key is a
separate parameter; no twelve-key copies are stored. For a different tonic,
recompute degree pitches through `ScaleCondition` and render only when needed.
Transposition adds cents/MIDI semitones, or multiplies frequency by
`2**(shift_cents/1200)`. Microtonal MIDI output must recompute note-plus-bend
events rather than multiplying integer MIDI note numbers.
Each exercise uses 100 BPM, PPQ 480, fixed durations and one ascending/descending
period. There are no chords, ornaments or copied melodies. All examples share
`family_id=mousa:synthetic-scale-exercises:v1`; their transpositions and related
synthetic pitch sets must not be split across train/test. They test rules and
transport, not musical attractiveness or generalization. Twelve-key transposition
checks run in memory in the unit tests; they do not expand the stored pack.

The narrow exporter writes SMF type 0, one monophonic channel, explicit pitch-bend
sensitivity RPN +/-2 semitones, a bend before every note and a final reset.
Fourteen-bit bend quantization has a maximum rounding error of about 0.01221 cents for
this range. Out-of-range exercises fail without silently clipping pitch.
The JSON sidecar is authoritative for names, source metadata, exact pitches,
conditions and MIDI digest; an ASCII condition echo is also embedded in MIDI.

The [MIDI Association's MPE explanation](https://midi.org/midi-polyphonic-expression-mpe-specification-adopted)
describes why ordinary pitch bend affects the whole channel. This fixture
exporter therefore only emits sequential notes; it does not implement MPE,
MTS, polyphonic microtuning or a general MIDI editor. Receiving software must
honor pitch bend and the explicit RPN range. Cantabile's documented SMF0/1 and
raw controller/pitch-event preservation are compatible at the format level;
its actual import/render and DAW playback are separate acceptance checks.
No open Cantabile project is touched by fixture generation.

Original synthetic exercises, original metadata and the implementation use
Apache-2.0, following the repository's original symbolic fixtures. No third-party source rights are
relicensed. Keep generated packs outside source control.

## Verification

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
python -m pip install mido==1.3.3
python tools/verify_scale_pack.py /path/to/new-scale-fixture-pack
```

The independent parser checks hashes, condition echoes, note timing, note
pairing, monophony, explicit tuning range, pitch-bend reset and reconstructed
frequency against every sidecar target. It is also run in CI. Mido is a test
dependency only; catalogue/conditioning/export need no added runtime package.
Actual audio listening and musical-quality evaluation are not implied.

Related work: [Issue #3](https://github.com/flamoris-jp/Mousa/issues/3),
[Issue #4](https://github.com/flamoris-jp/Mousa/issues/4).
