# Groove MIDI: a separate rhythm reserve

Cycle32 acquired the official **Groove MIDI Dataset v1.0.0 MIDI-only ZIP**.
This is not a count-only catalogue survey: all 1,150 MIDI files were extracted
privately, matched one-to-one to the supplied CSV, hashed, parsed and verified
against the archive again. The unchanged archive is 3,260,318 bytes; its MIDI
members total 5,273,095 bytes. No audio was downloaded.

## Rights and attribution

Google LLC directly distributes this dataset under CC BY 4.0, both on its
[official page](https://magenta.withgoogle.com/datasets/groove) and in the archive's
LICENSE. The source describes commissioned and additional drummers improvising
beats and fills, rather than an unverified collection of song transcriptions.
This scoped research relies on that creator-issued grant, not on free access or
an inferred worldwide public-domain status.

Credit: Groove MIDI Dataset, Google LLC and the contributors acknowledged on the
source page. Citation: Jon Gillick, Adam Roberts, Jesse Engel, Douglas Eck, and
David Bamman, *Learning to Groove with Inverse Sequence Transformations*, ICML2019.
License: https://creativecommons.org/licenses/by/4.0/ . Retain supplied credits,
notices and source links, indicate modifications, and do not imply endorsement
or add restrictions. The originals are unchanged; newly derived audit metadata
is explicitly distinguished. Full provenance and contributor credits are in
`datasets/research-groove-rights-cycle32-20261112.json`.

## What the inventory establishes

- 1,150 recordings, 1,149 distinct byte hashes. One duplicate pair is within the
  original train split; both originals remain preserved and marked.
- Ten anonymized drummers, 25 sessions and 18 top-level source style labels.
  These labels came from the performers, not invented listener impressions.
- The supplied train/validation/test counts are 897/124/129. Nine drummers and
  17 sessions occur in more than one split. Therefore these splits are not a
  test of unseen performer or unseen session generalization.
- Four drummers perform the same ten evaluation patterns, forming 40 related
  recordings. Different performances are not necessarily independent musical
  material. Retain those pattern-family links across any future split.
- The audit counts 446,312 positive-velocity note-on messages, not the official
  page's 445,494 hit total. The difference is 818. It counts all original files,
  including the duplicate, across all tracks, excluding meta messages, offs and
  zero-velocity note-ons. The source discrepancy is unresolved; no values were
  altered to match the page. Note-on/off totals matching is not full note-pair
  validation.

## Not yet done

No rhythm model has been fitted, no predictions have been scored, and no claim
of increased pitched-melody training is made. These are drum instrument keys on
MIDI channel 9, **not melodic pitches**. This reserve is separate from the
12-work pitched experiment (and any subsequent explicitly recorded expansion).

Before fitting: define the drum vocabulary without discarding expressive timing,
validate note pairing and control semantics, preserve the native PPQ480 timing
(the pitched timing model assumes PPQ384), examine near-duplicate pattern
families, and freeze a conservative performer/session/pattern-aware split. A
small model should compare drum timing/groove tasks, not reuse melodic pitch
interval metrics. Recording count is not composition count, and styles alone do
not certify broad musical diversity.

Private storage uses the owner-designated materials location, with an unchanged
archive and versioned manifest/inventory. Storage success requires an independent
read-back verification; a local extraction by itself is not a backup claim.
No raw external MIDI or audio is committed to Git.
