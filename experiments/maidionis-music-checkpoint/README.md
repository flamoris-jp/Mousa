# Persistent Maidionis music encoder: pitch and rhythm

This advances actual AI training rather than extending the baseline comparison
series. An external,unmodified Maidionis encoder jointly learns two supervised
tasks from shared interleaved pitch-interval/rhythm history. It now has saved,
versioned weights and AdamW state and can resume in a new process. This is an
offline research checkpoint,not a validated production bundle or full education
lifecycle implementation. No Core source is copied into Mousa.

## Frozen scope and data

Plan and exact input hash were committed locally before fitting. Same128 reviewed
PD/BY training families and4,084event windows as #14,now two tasks per window:
8,168 rows. Only the16 historical observed evaluation families/512events are
loaded (1,024task rows). No new holdout claim. The8 reserved validation families
remain untouched;20 already-consumed #16 reserve families are not loaded here.

A separately audited extractor reconstructs144 exact-hash raw sources,checks
rights/allowlists and matches all old pitch contexts/targets. Inputs contain
8 strictly preceding pitch/IOI pairs,not current targets. Control1 predicts
49 pitch-interval classes;control2 predicts25 log2 beat-IOI classes. Rhythm
outputs25..48 are masked before loss/evaluation. This is shared-history learning,
not a complete joint distribution over the next note and its duration. Highest
onset projection discards other simultaneous notes,duration,expression and
instrumentation. It is not an annotated melody or music-quality judge.

Core's supported encoder profile is256hidden,4layers,4heads,FFN1024; it does not
support the initially considered smaller profile,which was not fitted or patched
into Core. Input17tokens,vocabulary77,output49. Seed42,dropout0,AdamW0.0003,
weight_decay0,clip1. One complete no-replacement epoch per version,256updates,
batch32,last8. v1 then a separate process reloads it and trains v2 for one more
epoch. No metric-based checkpoint choice,tuning or stopping.

## Actual results

|Task|Initial NLL|v1 NLL|v2 NLL|v1 accuracy|v2 accuracy|
|---|---:|---:|---:|---:|---:|
|Pitch interval|3.87609|2.98143|2.85495|21.29%|23.05%|
|Rhythm IOI|3.18108|0.88041|0.87950|77.34%|74.41%|

Lower NLL is better.16family-macro,512targets per task,previously observed test.
**Negative:** rhythm accuracy falls after the second epoch,despite a tiny NLL
improvement. Both versions are retained; v2 is not declared universally better.
No musical-attractiveness or fresh-generalization claim. There is no generated
MIDI or Cantabile change in this checkpoint step.

CPU41.420351s for v1 and40.283672s for v2,build/setup excluded; one CPU thread,
180CPU-second guard and240wall-second process timeout per phase. No GPU/paid
compute. Each model is13,080,352bytes; optimizer state about26.14MB. No weights,
optimizer tensors,raw MIDI,private windows or audio in Git.

## Persistence and verification

Every new output directory must not exist. Files use exclusive creation/fsync;
manifest is written last,so incomplete runs are not resumable. Manifest pins
data/config/weights/optimizer/results digests. Roundtrip checks cover every model
parameter/buffer,AdamW moment/step/options and fixed-probe logits exactly.
v2's fresh-process initial evaluation equals all v1 final predictions exactly;
AdamW steps restore256 and advance to512. Dropout0 and explicit schedules avoid
unrecorded stochastic training state in this fixed configuration.

51 Python tests:50pass,one existing optional skip.13 additional native no-fit
negative cases reject invalid task/tokens/labels,schedules,family leakage,existing
output,missing/incomplete/altered resume. Independent reconstruction verifies
all144 sources and9,192task rows,causal histories and three exact-once schedules.
No uninterrupted two-epoch parity run was performed; exact reload/state checks
and the actual separate-process continuation are the evidence.

## Build and use

Use external Core at c288e92979d5005742a1bc3f86b389eadbc873d3,CPU Torch2.5.1,
CMake3.31.6,nlohmann_json3.12.0,GCC14.2,C++20,Release -O0 -g0.
Configure this directory with the same external MAIDIONIS_SOURCE,
CMAKE_PREFIX_PATH and NLOHMANN_JSON_INCLUDE_DIR variables documented by #14;
build target train_checkpoint. Do not substitute a different Core revision.

```sh
# Preparation uses the historical split,source files and hash-pinned extractor.
python experiments/maidionis-music-checkpoint/prepare.py \
 --historical /private/replayed/data.json --split /private/split-protocol.json \
 --extractor /private/corpus_learning_trial.py --out /private/new-data
# Verify the resulting hash against input-pin.json before fitting.
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 240 /path/to/train_checkpoint \
 /private/new-data/data.json /private/new-data/v1 1
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 240 /path/to/train_checkpoint \
 /private/new-data/data.json /private/new-data/v2 1 /private/new-data/v1
python experiments/maidionis-music-checkpoint/summarize.py --root /private/new-data
```

Resume currently requires the same dataset digest. Expanding the repertoire
requires an explicit new dataset version/lineage design,not editing an old
manifest to bypass the guard. Runtime/Cantabile deployment remains separate.

## Storage and next work

Both immutable checkpoints exist and pass local digest/reload verification.
LIME multipart backup is being written under
`assets/mousa/materials/metadata/music-checkpoint-20261115/`; consult its
completion receipts,not merely this planned path,before claiming remote backup.
Parts plus reconstruction manifest reproduce exact original files; do not assume
a single-file archive exists. Metadata evidence is saved separately.

Next prioritize training growth and bounded generation with the saved model:
versioned corpus expansion,explicit musical timing representation and guarded
8bar output suitable for later human audition. Preserve negative rhythm findings
and don't turn the already-observed cohorts into fresh tests again.

Independent checkpoint archive inspection additionally verifies53 model tensors
and106 optimizer moment tensors per version,finite and shape-matched. After
resume,5/16 pitch families and8/16 rhythm families worsen in NLL despite the
aggregate changes above. Do not hide these regressions.
