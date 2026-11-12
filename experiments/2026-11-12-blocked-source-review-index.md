# Cycle27: review index for three already blocked candidates

This index summarizes saved screens. It does not re-run source comparisons,
provide a new prediction, change thresholds or admit any candidate. Neither
rights review nor musical commonness waives the saved eligibility gate.

| Candidate | Flagged reference comparisons | Reference IDs with pitch+onset signature matches | Highest flagged whole-line interval similarity |
| --- | ---: | --- | ---: |
| Telemann1692 | 3 | 252 | 0.272321 |
| Clementi804 | 9 | 202 | 0.284058 |
| Mendelssohn1741 | 2 | 804 | 0.256250 |

Counts are flagged reference comparisons, not independent pieces, occurrences or
human-rated meaningful matches. The three candidates were selected because they
were already blocked: these counts cannot estimate a corpus-wide false-alarm
rate. Each block is caused by the unchanged exact-eight-onset pitch-interval
rule, not the whole-line 0.80 threshold. Exact onset agreement here is the saved
relative-onset signature, not a claim of equal note lengths, dynamics, tempo,
perceptual resemblance or copyright infringement.

## Evidence and status

- [1692 full screen](2026-11-12-telemann1692-independent-screen.json): references
  888 (training), 2245 (previously observed) and 252 (rights unresolved).
  Its `match_diagnostics` records matching-window positions and timing details.
- [804 full screen](2026-11-12-clementi804-independent-screen.json): references
  376, 2245, 1361, three separately listed 885 movements/files, 1692, 202 and 214.
  These are not nine independent families. `stop_pattern_diagnostics` contains
  location evidence. 583 did not flag. Source586 uses paired-note-only diagnostics
  because its full reader rejects CC7; this is not complete-file admission.
- [1741 full screen](2026-11-12-mendelssohn1741-independent-screen.json):
  reference580 (observed; related to augmented training583) and804 (blocked).
  Current training5 comparisons were clear but do not override the all-known
  reference rule. `match_diagnostics` provides window locations. 1042 required
  a declared larger read-only exact-distance resource bound; the threshold and
  formula were unchanged. The record states the remaining coverage limits.

Composition/encoding rights snapshots and current blocked statuses are separate
in `datasets/`. All three remain unfitted and predictively unscored in their
proposed transfer studies. Source snippets are not republished here; positions
and private originals support authorized review.

A future reviewer can use [the review checklist](../docs/CORPUS_EXPANSION_REVIEW.md)
to distinguish mechanical matches, family linkage, incomplete coverage and actual
human judgment. No such human judgment has been collected in this cycle.
