# Cycle 36: preserve long initial silence, separate support from corpus expansion

## Result

Purcell2243 was added under the approved fixed screen and new initial-rest profile without removing its 12,672-tick opening silence. The corpus now has 17 training works, 4,319 selected note events and 3,428 onset groups. This is an exploratory training addition, not a fresh holdout.

Neither broader initial support nor the additional work improved the two already-observed timing diagnostics:

| Corpus / initial maximum | Global group-delta NLL | Previous-cardinality context NLL |
|---|---:|---:|
| 16 / 12288 | 4.144505 | 4.799273 |
| 16 / 65536 | 4.153045 | 4.807813 |
| 17 / 65536 | 4.185509 | 4.852378 |

Lower is better. Means weight Adam640 and Chopin921 equally. They remain untrained but repeatedly observed diagnostics. This outcome concerns group timing only, not pitch/template/gate joint probability, raw-event NLL, or musical quality.

## What changed and what did not

The 16 old-cap versus 16 new-cap comparison changes only the initial prior support. Later timing NLL sums are exactly unchanged; the wider uniform prior spreads its fixed total mass more thinly over unseen first onsets. The 16 new-cap versus 17 new-cap comparison additionally changes later timing counts, template frequencies, and pitch-anchor frequencies. Both diagnostic works' later timing NLL also worsened after the addition, so the corpus difference is not solely an initial-support penalty.

Unconditioned initial-delta mass outside the 9,216-tick output target was 7.3533% for16old, 10.9375% for16new, and 15.8854% for17new. Global and context arms share the first-event law. Crucially, **16new and17new have exactly equal initial timing distributions conditional on fitting within the output target**, verified by sparse exact-rational signatures in both arms. Purcell's new first observation is outside that target and is never shortened. This equality does not imply equal later/template/anchor distributions or equal complete generated files.

All original MIDI bytes, leading silence and EOT remain unchanged. Purcell selected track EOT53760 and whole-file EOT54528 retain their distinct meanings. Later IOI/gate support remains12288; the API is finite and fails closed above its declared first support, not an infinite unknown-value model.

## Safety, repeat and controls

- Six conditions, five prescribed seeds each:30/30 complete, no missing conditions, copy flags0. Common complete-seed denominator is5 across all six conditions.
- The same all17 training plus640/921 exact8interval guard was used for every condition. Within-training583↔2243 motif overlap remains documented; seventeen works are not seventeen independent families. A zero flag is not a proof of originality or publication clearance.
- All30 private candidate files were byte-identical on repeat. Group-to-note reconstruction preserved all five note fields; distinct later onsets, bounds, maximum three active notes and no overlapping same pitches passed independent checks.
- Old16/12288's10 private outputs were byte-identical to Cycle34. Diagnostic NLL agrees within1e-12, with only up to3e-15 summation-order differences due to the explicit first/later decomposition. The enlarged copy-reference set was checked separately; both old and current results had zero flags.
- Run/repeat CPU:0.1014/0.0996 seconds. CPU checks are bounded-operation checks, not hard preemption inside every operation.
- No audio or generated notes were placed in Git or training-material storage. Original2243 was already stored in Cycle35; this snapshot adds metadata only.

## Provenance and artifacts

Approved plan SHA: `362b37be07143d863d962e1e9de1a11a6d709a627f1bb48d40f6706334fd395d`.

See `initial-rest-comparison-results.json`, `initial-rest-repeat-verification.json`, `initial-rest-metadata-snapshot.json` (all prefixed2026-11-12), and `../datasets/research-purcell-training-use-cycle36.json`. The appended usage record supersedes the earlier reserved status only for actual use, without rewriting the immutable rights snapshot. Anonymous contributor independence remains unproven; KingArthur/Macfarren edition siblings remain linked.

The supported achievement is a faithful, bounded representation of long opening silence with an isolated support-change control. It is not evidence that adding this work improved composition quality. No parameters were retuned after the results.
