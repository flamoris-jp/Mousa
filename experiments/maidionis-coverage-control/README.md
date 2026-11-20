# Actual Maidionis matched-coverage learning and reserved evaluation

Follow-on to #15. The question is whether the encoder learns useful next-interval
predictions when its training exposure exactly matches count baselines. This is
an actual six-arm CPU fit of external, unmodified Maidionis Core, not an emulation
or the complete production education pipeline. Initial preparation record is
preserved in PREPARATION.md/plan.json; execution-plan.json supersedes its
preparation-only/old-test-only scope and was committed before reserve extraction
and fitting. execution-input.json pins the resulting native input before fitting.

## Fixed protocol

128 original training families,4,084 windows,one complete shuffled pass per arm.
Seeds42/43/44 each use ordered and independently context-permuted training;
paired conditions share batch indices and initialization.127 batches32 + last20,
128 updates; same encoder/AdamW configuration as #14,one CPU thread,300 CPU-second
fit guard. Unigram and trigram consume those exact observations once, fixed
smoothing1/4. Counts use shorter contexts and different capacity/compute; equal
exposure is not algorithmic equivalence. No checkpoint selection, early stopping,
test tuning, additional epochs or alternative-source retries.

Evaluation is separated into old16 families/512targets and20 previously unscored
reserved families/640targets. Never pool them to imply all36 were fresh.
634 available metadata/ledger/journal files and205 hash-verified historical
documents had no prior-use matches for the20 reserves. This supports 'previously
unscored in available records', not untouched data or absolute external-history
proof. Curation previously inspected metadata/fingerprints. Eight validation
reservations were not opened. Reserved20 are now observed-untrained and cannot
be used as fresh again.

The pinned metadata audit checks documentary composition/MIDI rights separately,
PD dedication, family closure, no SA/no prior-role bridge, structural gates and
exact-file hashes. Only files excluded solely for reservation were eligible for
evaluation-only admission. All training prohibitions remain. Selection uses a
fixed SHA ranking, sometimes choosing an individual instrumental part; the
highest-onset8-interval projection is not an annotated melody and discards rhythm,
velocity,tempo and lower simultaneous notes. No quality/generation claim.

## Reproduce

First reproduce PR14 private inputs and run prepare.py as in PREPARATION.md.
Then prepare_reserved.py requires the pinned metadata audit, original exact raw
files and hash-pinned Cycle53 extractor; it rejects evidence/hash/role changes.
Raw-source path relocation is explicit via --raw-root. Private archive contains
the already prepared native data for replay without rereading raw material.
Build the unchanged native harness following ../maidionis-midi-learning/README.md,
using external Core c288e92979d5005742a1bc3f86b389eadbc873d3; do not copy Core here.
Run it once on the prepared private data, then:

```sh
python experiments/maidionis-coverage-control/summarize.py --run /private/run
PYTHONPATH=src python -m unittest discover -s tests -v
```

Summarizer checks exact input digest, all six arms,128updates,finite loss,
parameter updates,prediction identity/label alignment and disjoint families.
Keep all private data,per-family predictions,attribution and weights outside Git.
No new generated MIDI, audio, Cantabile session, merge or deployment.

## Executed results

Six actual native fits completed in99.503988 CPU seconds (build/setup excluded).
Native Core model tests pass.44 Python tests:43pass,one existing optional skip.
An independent implementation checked all13,824 initial/final evaluation rows,
all24,504 final-training rows,paired initial outputs,finite losses and parameter
updates. Two preparation runs matched byte-for-byte; full neural replay was not
performed in this run.

Reserved20-family macro NLL,lower better:

|Seed|Initial encoder|Ordered encoder|Permuted encoder|Ordered trigram|
|---|---:|---:|---:|---:|
|42|3.74828|2.96957|3.10142|3.11920|
|43|4.29654|2.98971|3.09180|3.11920|
|44|3.95130|2.95042|3.09573|3.11920|

Ordered unigram3.15012;uniform3.89182. All three ordered encoders improve NLL
versus initialization,permuted control and exposure-matched count baselines.
This supports actual learning of predictive interval/context features on these
previously unscored reserves. It does not establish musical attractiveness.

**Negatives:** trigram accuracy23.44% still exceeds encoder21.41/20.94/20.16%.
Seed42 worsens one of20 families versus initialization; ordered beats permuted
on14/17/16 families,not all20. Historical16 ordered final NLL is separately
3.01517/3.13210/3.06169; no claim that all36 families were new.
No population-wide confidence claim from treating640notes as independent.

The historical100-step comparison cannot isolate coverage from the increased
128-update horizon or last-batch weighting. Model checkpoints were not saved by
the unchanged diagnostic harness: this is actual fitting evidence,not a reusable
production music model. Next priority is versioned checkpoint persistence/reload
and music-specialist training including rhythm,not indefinite baseline studies.

## Evidence and follow-through

LIME Files verified archive:
`assets/mousa/materials/metadata/maidionis-coverage-reserved-20261115-evidence.zip`
1,674,033 bytes,SHA256
`e6840c9b23ac21192681b0fb286cb2687196f82d77e2c2328d6575fe53244371`.
Archive includes exact native inputs/results,admission/attribution audit,plans,
scripts and logs,not raw MIDI/audio/Core source/weights. Its README predates this
storage paragraph. Separate supplemental count audit verifies all48 public
summary rows and13,824 count-score rows exactly with standalone Counter code
(no primary implementation imports). The archive's neural audit already checks
13,824 initial/final neural prediction rows. The reserved20 public catalogue-family
identifiers appear in the frozen plan to make cohort selection auditable; all
note windows and per-family predictions stay private.

The separate final observation ledger permanently marks these20 families
observed-untrained; eight validation reserves remain untouched. No shared
latest-state pointer is overwritten. Do not repeat this test as fresh.
