# Degree-relative chord progression foundation

コード進行を **音度・種類・長さ** に分け、キー適用後にMIDI化します。
基本形を再現する `amount=0` と、固定ルールで一部を変える設定を比較できます。
「崩し度合い」は変更量の上限です。勇気やセンス、音楽的な良さの得点ではありません。

## Representation and compatibility

`mousa.chord-progression.experimental.v1` is a bounded experimental symbolic
value format, not a Maidionis model task or Cantabile project format.
`Chord(root=Degree(...), quality=..., duration_ticks=...)` uses the **existing**
zero-based `Degree`: I=0, II=1, ... VII=6. `period=-1/0/1` keeps its current
register semantics. Roman numerals below are display labels, not model tokens.
Neither the 192-class degree vocabulary nor any saved checkpoint is changed.

The root moves through `ScaleCondition.pitch_cents`; the explicit quality then
adds semitone intervals relative to that root. Quality is stored separately
because degree alone cannot distinguish V from V7 or a chromatic Vmaj7.
Every resulting tone must belong to the selected scale; the prototype rejects
chromatic/borrowed chords rather than silently changing their quality.

| Quality ID | Semitones above root | Example in C major |
| --- | --- | --- |
| `major` | 0,4,7 | C, F, G |
| `minor` | 0,3,7 | Dm, Em, Am |
| `diminished` | 0,3,6 | Bdim |
| `major7` | 0,4,7,11 | Cmaj7, Fmaj7 |
| `minor7` | 0,3,7,10 | Dm7, Em7, Am7 |
| `dominant7` | 0,4,7,10 | G7 |
| `half_diminished7` | 0,3,6,10 | Bm7b5 |

Only exact seven-note 12-TET **major**, period1200cents, zero tonic offset and
A4=440 are supported here. Matching scale contents are checked, not just the
scale name. Natural minor, pentatonic, microtonal/non-octave scales, detuning,
unsupported qualities and out-of-range MIDI notes fail with `ValueError`.
Existing scale/degree renderers retain their broader capabilities unchanged.
For example I–V–vi–IV gives C–G–Am–F at C3, D–A–Bm–G at D3 and
Bb–F–Gm–Eb at Bb3. Key includes a register; C3 means MIDI48.

`Progression` has a tuple of1..128chords,1..32bars and explicit meter. PPQ is
fixed480; numerator1..12, denominator2/4/8/16. A beat in tempo metadata is a
quarter note regardless of meter. Ticks per bar are `numerator*480*4/denominator`.
Positive integer chord durations must sum **exactly** to the declared bars.
Two chords may share a bar; a sustained chord may cross a bar line without
being rearticulated. No inferred rests, pickup, padding, truncation, tempo/meter
changes, inversions, voice leading or melody/rhythm rewriting are provided.
`start_bar` and `tick_in_bar` in resolved records are zero-based.
`to_dict`/`from_dict` reject unsupported versions, PPQ and unknown fields;
JSON text can be parsed with the existing `mousa.scales.strict_json`.

## Elementary patterns

Each built-in slot is one4/4bar. `make_progression(pattern, repeats=1..8)`
repeats the four-slot example without changing its chord qualities.

| Pattern ID | C major | D major |
| --- | --- | --- |
| `I-V-vi-IV` | C–G–Am–F | D–A–Bm–G |
| `ii-V-I-I` | Dm–G–C–C | Em–A–D–D |
| `I-vi-IV-V` | C–Am–F–G | D–Bm–G–A |
| `I-IV-V-I` | C–F–G–C | D–G–A–D |

These short elementary theory fixtures were independently encoded for this
implementation. No external progression database, score, MIDI, song, textbook
prose or arrangement was imported. Fixture code and generated symbolic
examples use Apache-2.0; this is not a rights claim over songs using similar
progressions. Future imports require the normal per-source terms/provenance
review. All transpositions, patterns and variants share the fixture family
`mousa:major-chord-rule-fixtures:v1`; do not treat them as independent held-out
music families or proof of learned harmony.

## Bounded variation

`vary_progression(progression, condition, amount=0..1, seed=...)` returns a new
immutable progression and an explicit trace under
`mousa.major-harmony-rules.experimental.v1`, `variation_source=fixed_rules`.

- `0` exactly preserves every chord. First and last slots are always protected.
- Budget is `floor(amount * number_of_internal_slots)`. A4chord progression
  has2internal slots, so amounts below0.5 make no changes. An8chord example
  has6internal slots:0/0.25/0.5/0.75/1 allow0/1/3/4/6changed slots.
- A seeded order selects slots. The same seed and inputs give nested changes
  as amount increases; amount does not change the earlier replacements.
- One operation per selected slot: add its diatonic seventh, or replace its
  root with a member of a small experimental function-related candidate set:
  I→vi/iii, ii→IV, iii→I/vi, IV→ii, V→vii°, vi→I/iii, vii°→V.
  Substitution preserves triad versus seventh size and the root's period.
- Candidate tones must pass the same scale/range checks. If no candidate fits
  the MIDI range the slot stays unchanged; `changed_slots` may be below budget.
- Slot count, register period, durations, meter, tempo, program and velocity
  stay fixed. Every actual operation stores index, before and after values.

Substitutions may alter harmonic motion strongly even at low amount; this is
one mechanical change per slot, not perceptual distance, equivalent function,
stylistic correctness or a musical-quality guarantee. Python's seeded RNG is
used; retain the trace and Python version for durable experiment replay.

## Generate and compare

```sh
PYTHONPATH=src python -m mousa.harmony_midi \
  --pattern I-V-vi-IV --repeats 2 --key C3 \
  --amount 0.5 --seed 17 --bpm 100 --out /tmp/new-harmony-comparison
```

The new directory contains `base.mid`, `varied.mid` and `comparison.json`.
Both SMF0files use PPQ480, channel1, piano program0, velocity80, block chords
in root position and full chord-slot sustain. Note-offs precede note-ons at
shared boundaries. Tempo, meter and a conventional major key signature are
written explicitly.8bars at100BPM last19.2seconds in either arm. Shared
sound/instrument/playback settings must also be held fixed when listening.
This intentionally simple voicing isolates chord-content changes; it is not
an arrangement or melody composition demonstration.

The manifest records both symbolic progressions, exact resolved notes, scale
digest/key, shared controls, MIDI hashes, rule seed/amount and all operations.
`amount=0` gives byte-identical MIDI. Outputs are proposals for explicit import
into Cantabile/DAW; no live project is accessed or changed. This foundation
does not claim a completed Cantabile roundtrip or actual human listening.

Python API:

```python
from mousa.harmony import make_progression, resolve_progression, vary_progression
from mousa.scales import Key, ScaleCondition, load_catalogue

condition = ScaleCondition(load_catalogue()["major_12tet"], Key.from_name("D3"))
base = make_progression("I-V-vi-IV", repeats=2)
varied, trace = vary_progression(base, condition, amount=0.5, seed=17)
resolved = resolve_progression(varied, condition)
```

## Verification and next research

The ordinary unittest suite tests all12tonics,4patterns and5amounts, explicit
qualities, duration/bar handling, invalid inputs, schema roundtrip, nested
deterministic changes, and unchanged degree-label/register meaning. With
verification-only `mido==1.3.3`, tests independently parse actual MIDI events,
note lengths/velocities, metadata, final tick, shared-tone boundaries and
zero-amount byte identity. CI installs Mido then runs these harmony tests.
No runtime dependency, fit, checkpoint migration or quality threshold is added.

Development starts at main `25fbc496405eb6b9b9b6d583e153228def890619`.
Rhythm Learning PR#20 head `0d75eae881bc9a38f5090b1618b68c88cadfe8f7` was
reviewed before implementation. Its rhythm/model/experiment files and README
are left untouched; this feature has no dependency on that unmerged PR.

Chipsy's next experiments can condition melody/rhythm on these explicit chord
timelines. Keep **fixed rules** and **learned selection/variation** as separate
arms, use the same key/tempo/length/instrument/seed protocol, and retain original
and changed traces. Measure validity, structural change, held-out family
performance and human A/B/tie/neither preferences separately. Do not use amount
or model confidence as a quality label. Learning where to change is subsequent
work; this PR contains no model training or taste/quality conclusion.
