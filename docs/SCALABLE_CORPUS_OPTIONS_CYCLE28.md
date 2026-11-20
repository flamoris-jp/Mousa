# Cycle 28: larger, more varied teaching corpora

This is a read-only shortlist, not corpus admission or a training run. No MIDI or
audio payloads were downloaded. Publisher-reported sizes are not locally verified
eligible counts. Evidence URLs, snapshots and SHA-256 hashes of successfully
retrieved source pages/cards are in
[`research-scalable-corpora-cycle28-20261112.json`](../datasets/research-scalable-corpora-cycle28-20261112.json).

## Recommended order

| Candidate | Reported scale and formats | Decision for now |
| --- | --- | --- |
| [IMSLP CC0 subset](https://huggingface.co/datasets/TiMauzi/imslp-midi-cc0-1.0) | 1,113 MIDI entries, 406 composer labels; mostly Western art music, with modern works too | First melodic metadata audit. Every original MIDI and composition/edition needs its own evidence; the compiler's CC0 card is not blanket clearance. |
| [PDMX v9](https://zenodo.org/records/15571083) | Over 250,000 scores; 222,856 in its no-license-conflict subset | Largest promising discovery index, not an already-cleared MIDI corpus. MusicRender JSON and MXL are primary representations; MIDI derivatives exist where available. |
| [Groove MIDI](https://magenta.withgoogle.com/datasets/groove) | 1,150 MIDI files, 13.6 hours, 10 drummers, 18 style labels | Strong provenance for a separate rhythm pilot: Google commissioned performances and releases them under CC BY 4.0. It does not solve melody diversity. |
| [Mutopia](https://github.com/MutopiaProject/MutopiaProject) | Thousands of catalogued scores, not all verified MIDI | Batch metadata and edition-family review instead of one-at-a-time discovery; retain item-level checks. |
| [Keynata Commons](https://carf-coder.github.io/keynata-commons/) | Generated MIDI/JSON/audio; current track count unverified | Pending. Explicit CC0 outputs, but the claimed PDMX/Groove training provenance and actual inventory need review. Generated data is not independent human musical evidence. |

PDMX's maintainers disclose 31,221 discrepancies between website and internal
license fields. `no_license_conflict`, `is_original`, and uploader labels are
useful filters, not proof that the uploader owns a composition or arrangement.
Forty-two corrupt source scores lack the associated MXL/PDF/MIDI files. Do not
report the score count as the number of usable MIDI files. Scores without MIDI
would need a separately audited conversion workflow, not silent conversion.

Groove records improvised drum performances rather than transcriptions of a large
commercial song catalogue. Preserve attribution and license notices, and record
changes. Split by drummer/session and repeated beat identity, not by tiny slices.
Percussion pitches must not be fed into the current melody model as pitched notes.
Avoid downloading its audio when MIDI alone serves the task.

## Popular large datasets that do not currently meet our intake scope

- **[Lakh](https://colinraffel.com/projects/lmd/):** 176,581 MD5-unique MIDI files.
  Its CC BY collection label does not resolve individual composition, arrangement
  or transcription rights. The curator explicitly did not transcribe the files
  and cannot reliably attribute each contributor. No blanket intake.
- **[GigaMIDI v2](https://huggingface.co/datasets/Metacreation/GigaMIDI/blob/main/README.md):**
  over 2.1 million reported files, including other web-derived corpora. CC BY-NC
  and additional research/fair-dealing conditions do not establish the required
  rights for FLAMORIS product training. No access gate was accepted.
- **[MAESTRO v3](https://magenta.withgoogle.com/datasets/maestro):** 1,276 piano
  performances and 198.7 hours. Google provides CC BY-NC-SA terms and explicitly
  supports modeling research. This is **not a statement that AI training is
  forbidden**. Compatibility with commercial/product use, underlying repertoire
  and any downstream obligations remain unresolved. A separately approved,
  genuinely noncommercial study is a different scope, not current admission.

Likewise, converting a scraped corpus to synthetic audio or generating loops from
it does not automatically clear its underlying compositions. A public-domain mark
is a status claim, not necessarily a rights-holder's CC0 dedication. Repository
software licenses do not determine dataset rights.

## Next safe metadata-only batch

1. Freeze the current five-work/four-family/444-event inventory and existing
   observed, reserved and blocked statuses. No old result becomes fresh again.
2. Prepare **100 candidate metadata rows total**, initially 50 IMSLP and 50 PDMX,
   selected across composer/contributor, instrumentation and era before viewing
   prediction results. Retrieve only metadata fields, not raw MIDI-byte columns.
   Save version/URL/hash, license URL, source edition, uploader/composer identity,
   format availability and declared genre. Missing metadata stays missing.
3. Audit **10 source families** from this inventory at the original pages, keeping
   all failures. Check ownership or historical edition/arranger evidence and the
   exact encoding license. The aim is a larger eligible pool, not a promised
   admission count. Do not choose records because they evade the similarity gate.
4. Separately inspect Groove metadata for a proposed rhythm-only pilot of up to
   50 records. Verify its recording/session grouping and reader requirements.
5. Only after rights approval, acquire a bounded MIDI pilot with original hashes,
   preserving unsupported semantics and reporting failures. Fix family splits and
   apply the unchanged similarity gate before any predictive evaluation. Counts
   of works, events, families and verified styles must be reported separately.
6. Expand the successful intake process to hundreds of verified works only after
   measuring audit yield, technical support and computational cost. Use metadata
   indexing and repeated-edition evidence to reduce effort, not to waive checks.

Pitched melody and percussion need separate experiments. Compare natural and
matched event budgets without inventing cross-work transitions. Existing
Telemann1692, Clementi804 and Mendelssohn1741 blocks remain intact. No human
listening approval, legal guarantee, large-scale learning benefit or new corpus
admission has been established by this survey.

## Actual acquisition in this pass

A bounded metadata-only demonstration retrieved ten Satie entries from the
official Mutopia index and linked pages. IDs, titles, original page URLs, declared
CC BY-SA 4.0 license, editions and available formats are saved in
[`research-metadata-batch-cycle28-20261112.json`](../datasets/research-metadata-batch-cycle28-20261112.json).
No MIDI payloads, score files or large tables were downloaded. All ten remain
pending, and this is one composer/piano cohort, not ten independent families or
an achieved diverse corpus. The larger IMSLP/PDMX metadata batch above remains a
proposal, not completed acquisition. Direct site failures and the web-reader
fallback are recorded; the evidence hash covers a saved reader extract, not the
original MIDI. Keynata remains an unverified creator claim, not a rights authority
for its upstream PDMX inputs.

This ten-row Mutopia probe is a <=20-row route-feasibility check, not the proposed
50+50 IMSLP/PDMX audit batch. The operational ceiling of 100 rows per route is a
maximum; this document's 100-row total initial proposal is a smaller starting
budget, not a competing policy.
