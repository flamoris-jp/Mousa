# Eight-bar MIDI from the saved Maidionis encoder

This uses the actual v2 pitch/rhythm checkpoint from #17,not a hand-written count
model or a new training run. Three fixed seeds101/102/103 generate candidates;
all are retained without seed shopping. The protocol and RNG convention were
committed before inference. No dataset-role change or checkpoint mutation.

## Results

|Seed|Notes|MIDI bytes|Longest training interval run|Longest interval/IOI pair run|
|---|---:|---:|---:|---:|
|101|64|614|6|5|
|102|52|512|10|5|
|103|48|470|7|5|

All three pass the frozen structural/copy screens and were exported as private
MIDI. Total1,596bytes.100BPM,4/4,8bars,PPQ480,15,360ticks/19.2seconds each.
This is an enforced output duration,not evidence that the model learned long-form
structure. No human audition has been performed. Subsequent isolated Cantabile import/export and offline rendering are verified below.
No musical-quality or guaranteed-originality claim.

## Model and constraints

External unmodified Core c288e92979d5005742a1bc3f86b389eadbc873d3; v2 manifest,
weights,config and training-data hashes are verified before load. Synthetic
8-pair history is not emitted. StartMIDI60; notes48..84; intervals≤12semitones.
Task1pitch/task2rhythm predictions share the same past; independent draws use
fixed mt19937 uint32/2^32 cumulative sampling. Allowed IOIs are.25/.5/1/2beats,
masked to remaining32beat budget. Durations90% of IOI,velocity80,program0.
These masks alter the unconstrained model distribution. This is not a fully
joint next-event distribution or a harmonic/form model.

CPU0.990852s for all3seeds; exact replay0.933860s,one CPU thread,60CPU-second
ceiling. All fields exceptCPU time match exactly. Independent implementation
checks all328 RNG draws,supports,probabilities,history recurrence and events.
Checkpoint model/optimizer/manifest/results hashes remain unchanged.

## Copy and MIDI guards

References are all128 actual training families,full first2,048highest-onset
projections rather than just sampled32windows. Raw source hashes,PD/BY rights,
allowlists and4,084original training targets are verified. No heldout/reserve
raw files used. Reject if any transposition-invariant exact pitch-interval run
is≥12 or paired interval/IOI run≥8. Thresholds are frozen before generation.
All three pass; seed102's10-interval match remains visible,not hidden.
This is a bounded screen against these references,not comprehensive plagiarism
or legal release clearance.

Exporter reopens each SMF and checks every note,gap,duration,velocity,channel,
program,tempo,meter and end tick. Separate binary SMF parser and independent
DP matching confirm all outputs and reference maxima without importing the
exporter.59tests:58pass,one existing optional skip;5native no-inference negative
checks reject missing/altered checkpoints and existing output. An initial suite
command omitted PYTHONPATH and failed two imports; the documented command below
passes. Original failure log is retained in private evidence.

## Reproduce

Build this directory with the same external Core/CPU Torch2.5.1 toolchain as #17,
target generate_checkpoint. It pins the exact v2 checkpoint and never fits.
The private output directory must already exist and output file must not exist.

```sh
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 90 /path/to/generate_checkpoint \
 /private/v2 /private/new-candidates.json
python experiments/maidionis-checkpoint-generation/validate_export.py prepare-references \
 --historical /private/replayed/data.json --split /private/split-protocol.json \
 --extractor /private/corpus_learning_trial.py --out /private/new-references
python experiments/maidionis-checkpoint-generation/validate_export.py export \
 --native /private/new-candidates.json \
 --references /private/new-references/references-private.json \
 --receipt /private/new-references/reference-receipt.json --out /private/new-export
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Private artifacts

Verified MIDI storage is LIME Files:
`assets/mousa/generated/maidionis-v2-20261115/`
Files are `mousa-checkpoint-seed101-8bars.mid`,seed102 andseed103 counterparts.
They are also delivered as private Library attachments for convenient audition.
No MIDI,model weights,private note/probability traces or raw references in Git;
only scripts,synthetic tests,aggregate findings and artifact digests.
Cantabile projects are not changed. No merge,deploy,GPU or paid operation.

Next: listen privately,record human feedback if provided,and improve the actual
saved-model curriculum/representation. Safe expansion needs explicit dataset
lineage; this generation step intentionally did not bypass the same-data resume
guard or consume reserved validation data.


## Subsequent isolated Cantabile audition verification

Cantabile clean source420f395f187d46072e86912c51bae5a2527a00f1 was built
in a separate cloud directory. Each of the3MIDI files imported into its own
new project,validated and re-exported byte-identically,including15,360tick end.
The official offline Cantabile FluidSynth worker rendered48kHz stereo PCM16
WAVs with TimGM6mb.sf2,program0. Each is19.2seconds music +2seconds release
tail=21.2seconds,4,070,444bytes. All PCM is nonzero with zero clipped samples.

For usable audition volume,all3renders receive the same24x gain into separate
*-audition.wav files. Peaks remain below.565 fullscale; no compression,clipping,
note/timing edit or model change. Raw render hashes and audition hashes are
preserved in audition-verification.json. TimGM6mb installed-package notice
records GPL-2; bank itself is not redistributed. Private audition only,not a
new public-release rights claim.

The connected live Cantabile runtime/document/revision was read-only and
unchanged before/after; no project-switch,import,edit,save or render MCP action
was called on it. CLI/renderer use isolated files,not the active user project.
Human listening and subjective quality remain unassessed.

Audition WAV Library attachments are ready. LIME audio archive/expanded-file
backup is running separately; consult its completion receipt before claiming
that upload finished. No audio bytes or encoded audio are committed to Git.
