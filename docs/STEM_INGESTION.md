# Stem WAV → AudioAnalyzer → Mousa (initial local implementation)

Tracking: [Mousa #7](https://github.com/flamoris-jp/Mousa/issues/7),
[Studio Client #19](https://github.com/flamoris-jp/flamoris-studio-client/issues/19)
and [producer PR #20](https://github.com/flamoris-jp/flamoris-studio-client/pull/20).
The producer reference used by integration CI is Studio Client commit
`ff142fe5527f5df02a28ab4ad9df190d15b9e762`.

**MIDI is not required for this intake.** The first slice accepts source-bound
AudioAnalyzer stem analysis, preserves timing and pitch uncertainty, and exports
only specifically reviewed note annotations. It does not fit a model, publish
music, score musical attractiveness, or edit a Cantabile project.

## Implemented roles

| WAV role | Mousa destination | This slice |
| --- | --- | --- |
| `vocals` | Melody | Raw F0 + monophonic note candidates + reviewed notes |
| `bass` | Bass | Raw F0 + monophonic note candidates + reviewed notes |
| `drums` | Drums | Audio features only; no instrument hit transcription |
| `harmony` | Harmony | Audio features only; no polyphonic note transcription |
| `mix` | Arrangement | Audio features only; no inferred verse/chorus labels |

The producer uses the existing AudioAnalyzer worker for waveform, relative RMS,
BPM/beat estimates and major/minor-triad estimates. Those stem-specific estimates
are not authoritative shared song tempo or harmony. F0 uses an optional pYIN
profile; no neural weights or remote service are required. See the producer's
`docs/stem-mousa.md` for source formats, resource bounds and dependencies.

## Produce and import

Run the producer from its approved checkout with optional dependencies installed:

```bash
python product/audio-worker/stem_export.py analyze \
  --input /chosen/music/vocals.wav --output /chosen/results/lead.analysis.json \
  --song-id song-001 --family-id composition-001 --stem-id lead --role vocals \
  --start 20 --end 28 --offset 0
```

Then, from the Mousa repository (Python 3.11+, standard library only):

```bash
PYTHONPATH=src python -m mousa.stem_intake import \
  --analysis /chosen/results/lead.analysis.json --wav /chosen/music/vocals.wav \
  --output /chosen/results/lead.intake.json
PYTHONPATH=src python -m mousa.stem_intake review-template \
  --intake /chosen/results/lead.intake.json --output /chosen/results/lead.review.json
```

Windows PowerShell equivalent for the environment prefix is `$env:PYTHONPATH='src'`
followed by `python -m mousa.stem_intake ...`. Paths above are examples, not host
configuration. Inputs and output parents must exist; every output name is new.
Links/reparse points are rejected. Hard-link-capable output storage is required
for atomic no-replacement publication. Raw WAV is hashed locally, not copied or
uploaded. No paths/commands in received JSON are followed or executed.

`import` checks the strict closed schema, finite/bounded types, source WAV header,
size and SHA-256, time/role agreement, raw feature source binding, F0 frame order,
voicing thresholds, null unknown pitch, note ranges and non-overlap. Unknown
schemas, duplicate keys, NaN, altered sources and a forged approved flag are
rejected. Imported state is always **pending_review, trainingEligible=false**.
Hashes detect content mismatch, not producer authenticity or musical correctness;
this is a local operator workflow, not a signed authorization system.

## Explicit review and rights gate

The generated review template intentionally has no selected notes, decision
`pending`, an unassigned reviewer and `trainingAllowed: false`. Export fails in
that state. Keep the original intake unchanged. After auditioning the source
and inspecting its candidate notes, edit a separate review record:

- Preserve its exact `analysisSha256`.
- Set `decision` to `approved` and provide an opaque `reviewerId`.
- Record `rights.trainingAllowed: true` and a real local `rights.evidenceId`
  only after reviewing permission to use this material for learning.
- Explicitly select candidate IDs in `notes`, each with `id`, `start`, `end` and
  integer MIDI `pitch`. Correct their source-relative seconds/pitch as needed.
  They must remain ordered, non-overlapping and inside the analyzed excerpt.

No automatic select-all approval exists. IDs/rights evidence are operator
assertions, not an automated legal opinion. Do not commit personal reviewer
histories, production stems or private licensing documents to public Git.

```bash
PYTHONPATH=src python -m mousa.stem_intake export-reviewed \
  --intake /chosen/results/lead.intake.json --review /chosen/results/lead.review.json \
  --output /chosen/results/lead.notes.json
```

The output is `flamoris.mousa.note-examples` v1, not a MIDI file or admitted
Maidionis dataset. It binds analysis/review/source hashes, role/family IDs, source
and song onset seconds, durations, pitches and whether each note was corrected.
It labels the result human-reviewed transcription, **not** preferred/attractive
music. `preferenceLabel` is null and `modelTrainingPerformed` is false. Gaps are
not converted to REST, because an omitted or uncertain interval is not a verified
musical silence. A future event-task adapter must retain this distinction.

## Shared song time and split discipline

**Song time = source time + songOffset.** Original aligned stems usually use 0.
A crop starting at song second 20 but stored from file second 0 uses offset 20.
Raw F0 and notes remain in source seconds; no sixteenth-grid quantization is
performed. Source waveform/beat features cover the full source, while pitch
candidates cover the selected 0.1–30 second excerpt.

All stems, crops, transpositions and arrangements in the same composition family
must share the supplied `familyId`. Intake preserves `splitGroup=work-family:ID`
and never independently assigns a stem/crop to train or test. The later dataset
builder must enforce group-level splits across the complete catalog. This module
does not discover related compositions or guarantee correct user-supplied groups.

## Verification

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
MOUSA_STEM_EXPORTER=/approved/studio-client/product/audio-worker/stem_export.py \
  PYTHONPATH=src python -m unittest discover -s tests -p test_stem_intake.py -v
```

There are 18 pure intake/review tests and one real-producer integration test. The
integration explicitly runs synthetic WAV through the real AudioAnalyzer/pYIN
CLI, imports it, verifies default approval rejection, and exports annotations
under a **synthetic-fixture test review**, not approval of artist material.
Without `MOUSA_STEM_EXPORTER`, only that optional integration test is skipped.
The new workflow pins the producer and sets it, so CI must execute all 19 tests
plus existing MusicIR tests. No private audio or server access is needed.

## Deliberate limits and next gates

This is a local CLI, not deployed software or a GUI review interface. Singing
vibrato/glissando, octave ambiguity, same-pitch re-attacks, backing harmonies,
stem-separation bleed and note boundaries require real-stem listening and manual
corrections. Synthetic tones do not establish vocal transcription accuracy.
Adding new/missing notes, splitting/merging candidate notes, complete phrase/rest
review, separation-model/parent-mix lineage, shared beat maps, full-song batching,
drum/polyphonic transcription, Cantabile review and Maidionis event-model training
remain tracked in #7 and related issues. The existing grid-v1 MIDI experiment is
not silently fed audio-derived guesses or altered by this change.
