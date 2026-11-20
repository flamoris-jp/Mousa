# Cycle27: fixed-gate synthetic benchmark and corpus expansion preparation

## Question and prospective scope

Can the current conservative source gate both reject separately constructed
common patterns and miss known mechanical derivatives? Cycle20 had already
shown examples, so this is a prospectively frozen construction batch, not a new
hypothesis or an untouched real-music evaluation. No existing candidate is
rescored or released and the exact-eight-onset / whole-interval0.80 rule remains
unchanged.

The plan and deterministic fixture rules were saved before benchmark scoring.
There are10strata with8variants each, seeds2700–2707. The plan records code hashes,
transform positions, seed offsets, bounds and diagnostics. The report binds both
plan and fixture hashes. Independent rerun report bytes are identical.

## Results

| Construction stratum | Cases | Gate flags | Constructed misses / collisions |
| --- | ---: | ---: | --- |
| Uniform pitch transposition | 8 | 8 | 0 misses |
| Double all onset intervals | 8 | 8 | 0 misses |
| Alternating one-tick timing perturbation | 8 | 8 | 0 misses |
| Three inserted notes | 8 | 0 | 8 misses |
| Three deleted notes | 8 | 0 | 8 misses |
| Seven-note excerpt from16notes | 8 | 0 | 8 misses |
| Separately constructed ascending scales | 8 | 8 | 8 construction-label collisions |
| Separately constructed repeated-note lines | 8 | 8 | 8 construction-label collisions |
| Separately constructed alternating lines | 8 | 8 | 8 construction-label collisions |
| Separate random-walk recipes | 8 | 0 | 0 construction-label collisions |

“Miss” means a known transformation passed this mechanical gate. “Collision”
means two separately executed recipes received a flag. Neither is a finding
about copyright, meaningful resemblance or human perception. Common recipes
intentionally share structure and can yield mathematically transformed sequences;
they are not genuinely independent musical compositions. Each common-pattern
stratum contains justONEdistinct interval contour with8offset variants. Other
strata share the same8base random walks across transformations. Consequently no
pooled population false-positive/negative rate or independence claim is justified.
The random-walk comparison is not evidence of musical unrelatedness either.

Seven-note excerpt misses do not mean the global metric always ignores short
sequences: the unit test shows two identical seven-note sequences flag through
global similarity1.0 even with no eligible eight-note window. Length mismatch
matters. Three spread-out insertions/deletions break local-window coverage in
this design. Nothing here measures actual ornamental performance robustness.

## Review support and larger-data preparation

Diagnostics now enumerate interval-match location pairs, with the first8pairs
showing zero-based note positions, interval sequences and raw/scale-normalized
onset-rhythm agreement. All pair counts and truncation are explicit. These are
synthetic sequences only; rhythmic descriptors never waive a pitch-only block.

[The blocked-source index](2026-11-12-blocked-source-review-index.md) makes the
saved1692/804/1741decisions inspectable without rescoring or publishing source
passages. Its flagged-reference counts are not family counts or an error-rate
sample. [Corpus expansion review](../docs/CORPUS_EXPANSION_REVIEW.md) separates
rights, family grouping, technical admissibility, observed versus fresh roles,
fixed-gate review and later human judgments. It also lays out natural-budget
and equal-event-budget comparisons without promising a larger admitted corpus.

The current augmented training set remains5works/4conservativefamilies/444events.
The original4work model remains separately frozen. Observed640/921are diagnostic
only, and580must stay out of583-augmented independent evaluation. No human
comments or preference labels were fabricated, collected or trained.

## Verification and limits

Full suite:260discovered,259passed,1existing realAudioAnalyzer integration skip.
Dependency-free suite:260discovered,222passed,38expected optional skips.
Four new benchmark tests pass. No production metric/model/threshold changed.
No new real-source prediction, generated MIDI/audio, main merge, deployment,
GPU computation, paid operation or public corpus release occurred.

## Independent material search

New named composer/contributor candidate Dvořák2211, String Quartet Op96 /
Sébastien Manen, remains pending. Mutopia names Simrock1894 and Public Domain;
historical catalogues identify the1894first edition and plate10,133. Direct
original downloads failed (503; legacy mirror404), so an alternative official
Mutopia GitHub tree was checked. Commit-pinned `header.ily` and `dvorak-o96.ly` were
retrieved without execution: the header confirms source, contributor, ID2211and
an explicit typesetter Public Domain dedication. URLs and hashes are in
`datasets/research-dvorak2211-pending-20261112.json`.

This improves encoding-rights evidence but does not finish admission. Original
MIDI bytes and historical score incipit are not yet verified. No conversion,
source execution, fit, score or similarity screen took place. All movements and
parts remain one composition family, not four or more independent training works.
A different named composer/contributor is not proof of publisher or infrastructure
independence. Corpus size did not increase in this cycle.
