# Cycle32: corpus expansion, rhythm reserve and representation controls

## New pitched sources

Czerny Op821 exercises2060 and2061 have original MIDI, paired typesetter PD
notices and visually checked historical edition incipits. The relevant edition
and editor evidence is retained, including limitations of a later reprint.
2060 selects the upper staff (121 notes);2061 selects the lower scalar staff
(70 notes). These are two exercises in one work/editorial cohort, not two new
independent styles. The shared Ruthardt editor links existing Tchaikovsky2080;
within-training exact-eight patterns also link2061 with Beethoven904. Future
splits must retain those links. The original omitted ending rests are not padded.

The proposed 14-work corpus has 3,454 selected events. Fixed crosssplit checks
against the already observed Adam640/Chopin921 diagnostics complete all28 pairs
without flags. The original exact-eight/.80 rules and bounded2048 comparison
remain unchanged. Within-training matches are reported rather than erased.
Grieg1888 and Schumann354 remain rights-pending and excluded.

## Failure retained, not hidden

The first run expanded intake to nine additions but missed the model's own
12-work constructor cap. Base5 fit, prediction and five outputs completed;
expanded factorized counts were constructed before the14-work context model
failed. Thus the two additions were **already used in counts**, even though no
14-work prediction or generation finished. The failure, original plan and partial
outputs remain preserved. It was not a successful expansion or an untouched
reserve at that point.

A separately versioned14-work context profile reuses the old integer count model
and merges sufficient counts without transitions across work boundaries. The
old12-work model and historical results remain unchanged. Before the corrected
prepare accesses original files, it now constructs both models and exercises the
legacy generator on synthetic14-work input. Revised code/tests/profile hashes
are fixed in a new plan, with separate review before actual retry.

## Corrected run completed

The final2 plan (`7037388e94f36b4248288d2253c732ea5e0536dcdbcbda28741f8580103076aa`)
passed independent review:1,800 exact probability checks and240 small generation/
old-model parity cases. Two newly introduced test import dependencies were also
corrected before the real retry; all unrun intermediate plans remain preserved.

The corrected14-work experiment and repeat completed. Both base5 and14-work
conditions generated5/5 candidates, with no fixed copy flags or safety failures.
All10 private generated-note files are byte-identical on repeat; reports match
except CPU timing (initial0.720 CPU seconds). All original hashes are unchanged.

| Fixed comparison | Base5,444 events | Expanded14,3,454 events |
| --- | ---: | ---: |
| Factorized timing NLL | 8.769905 | 9.083682 |
| Context timing NLL | 7.859410 | 8.020197 |
| Mean absolute pitch interval | 3.066789 | 7.025947 |
| Overlapping onset fraction | .131989 | .356005 |
| Same-pitch repeat fraction | .309123 | .076193 |

Timing prediction worsens on the same observed diagnostics, while repetition
falls and jumps/overlap increase. Corpus amount, composition, vocabulary and
natural event weighting are confounded. These figures do not show improved
appeal or fresh generalization. Historical12-work outputs used a different
copy-reference set, so they are not substituted as a newly controlled condition.
The new completed-use ledger supersedes the preserved partial-use state without
erasing it. Two additional originals total2,778 bytes. Immutable versioned
storage snapshots are prepared; read-back status is tracked separately.

## Other completed research

- A prospectively fixed2×2 projection/weighting study retains only the highest
  pitch at each onset as an explicit lossy transformation. It removes842 notes,
  reduces generation overlap, but worsens original-staff timing prediction and
  increases pitch leaps under equal-work weighting. It is not verified melody
  extraction or proof of greater appeal. See `2026-11-12-onset-projection-study.md`.
- The official CC BY4.0 Groove MIDI-only release was acquired and fully inventoried:
  1,150 drum recordings, one byte-duplicate pair, native PPQ480/channel9, no audio.
  This is a separate **untrained rhythm reserve**, not1,150 added melody works.
  Performer/session split overlap and shared evaluation patterns prevent claiming
  unseen-performer or independent-pattern generalization from the supplied splits.
  See `../docs/GROOVE_RHYTHM_RESERVE.md` and its provenance/inventory reports.

## Limits

No fresh holdout result, real listener rating, learned semantic ground truth,
public media release, main merge, deployment, GPU work or paid compute is claimed.
Small CPU count models, conservative rights review and immutable originals remain
the scope. Greater corpus size, stronger musical diversity and better appeal are
separate questions. Results of the corrected run and private-storage read-back
must be reported only after their actual verification.
