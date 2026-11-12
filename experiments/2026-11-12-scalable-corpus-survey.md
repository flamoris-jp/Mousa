# Cycle28: scalable corpus survey, not corpus training

## Priority change

The owner prioritizes learning from more varied and substantially more material,
not merely locating another isolated historical piece. We therefore compared
collection-level routes and designed a metadata-first staged intake. No larger
training run is claimed: current augmented training remains5works/444events.

## Findings

Eight routes were compared with primary source links in
`datasets/research-scalable-corpora-cycle28-20261112.json`.

- **PDMX** offers250K+symbolic scores and associated MIDI where available, not a
  verified250K-file MIDI corpus. Its own update reports31,221internal/public
  license conflicts and recommends the no-conflict subset. That filter is useful
  but is not proof of underlying rights. This is the strongest scale-oriented
  metadata candidate, with per-item authority review still needed.
- **IMSLP CC0 compilation** reports1,113entries/406composers and original source
  links. Its card says this version filters toPD/CC0, but this is a compiler claim.
  The original composer/arrangement/encoding evidence, especially modern works,
  must be checked. Published train/validation/test assignments are not accepted
  without family verification.
- **Mutopia batch discovery** can amortize existing contributor/edition work
  without assuming every member has identical rights or fresh status.
- **Groove MIDI** has the most direct commissioned-performance CC BY4.0 route
  among the reviewed candidates, with1,150MIDI files/13.6hours. It teaches rhythm,
  not melody. Any future pilot must use percussion semantics, drummer/session
  grouping, attribution and original MIDI only; audio is separately scoped.
- **MAESTRO/GigaMIDI** have noncommercial and other scope conditions. These do
  not inherently forbid AIresearch, but compatibility with intended FLAMORIS
  product use is unresolved; they are not added to this general corpus.
- **Lakh** has unresolved original transcription/composition authority despite
  its collection-level license. Size and research popularity cannot clear it.
- **Keynata Commons** describes generated CC0 outputs with upstream statistical
  inputs. That does not make it an independently verified human-music corpus or
  remove upstream rights/duplication questions. It remains low-priority pending.

These counts are source-page snapshots, not local inventories or admitted
training material. Retrieved evidence HTML/README hashes are recorded when
available; inaccessible files and web-only evidence are identified separately.
No authentication gate, license acceptance, paid purchase or bulk download took
place. No collection's names or statistics become human semantic labels.

## Next staged procedure

[The intake plan](../docs/SCALABLE_CORPUS_INTAKE.md) prioritizes bounded public
metadata retrieval, followed by exact source rights and family audits. Only then
can an admitted pilot receive fixed source hashes, split roles, resource limits
and registered comparison subsets. Existing candidate blocks, observed diagnostic
status and583/580family exclusion remain unchanged. New formats require their
own loss-aware conversion experiment rather than silently replacing originals.

This cycle makes expansion more scalable at discovery and review; it does not
claim that the legal/provenance bottleneck is solved. Classical source bias and
lack of actual listener preferences remain substantive limitations.

## Actual bounded discovery result

A first metadata-only route probe retrieved10official Mutopia Satie entries,
with original page links, edition/license claims and format fields, in
`datasets/research-metadata-batch-cycle28-20261112.json`. The saved evidence hash
covers the web-tool extract, not original HTML or MIDI. Contributor fields missing
from excerpts remain null. Direct Haydn index retrieval failed503; a guessed
index-file URL failed404. These failures are recorded, not hidden by a success
claim for the originally proposed IMSLP/PDMX batch.

All10entries remain pending. They share one composer/piano/style cohort, and at
least six share a contributor: this is a route feasibility probe, NOT10independent
families or achieved stylistic breadth. CC BY-SA metadata needs its own exact
scope/edition review; it is neither CC0 nor an intrinsic AItraining ban. The
proposed100-row IMSLP/PDMX diversity audit has not been executed. No MIDI payload,
source score or audio was fetched for this probe and no new work was fitted.

## Verification

The two new ledgers parse as JSON; all8corpus routes and10metadata entries remain
unadmitted. Internal review checked the distinction between claimed scale and
eligible files, noncommercial scope and AItraining, separate rhythm semantics,
and preservation of old evaluation states. No code changed in cycle28; the full
suite was nevertheless rerun on the final tree:260tests,259pass,1existing skip;
dependency-free260tests,222pass,38expected optional skips. Compile/diff checks pass.
