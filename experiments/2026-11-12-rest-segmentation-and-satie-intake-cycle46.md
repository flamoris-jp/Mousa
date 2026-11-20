# Cycle46: rest-aware segmentation and two blocked new sources

## Generation diagnosis and controlled variation
Density must be separated from where silence falls. The earlier 18-work outputs include a candidate with 7,872 ticks of leading silence and only six notes, while another has dense middle blocks. Original introductions, exact note lengths and meters remain intact.

The fixed experiment uses complete-sound gaps of at least192 ticks to delimit convenient segments, not asserted musical phrases. It re-presents pitch classes from the first segment in the third, with legal whole-template octave placement. This does not change time, rests, note counts or density. Known/new random cohorts are kept separate; no replacement seed or segment is selected after failure.

All six unedited outputs completed. Edits completed for one of three known seeds and two of three new-random seeds. Two failed because the fixed source segment was too short; one failed because changed pitches produced a sustained same-pitch collision. The rejected collision was independently reconstructed and not rescued. Successful candidates passed the unchanged22-reference copy screen and retained all nonpitch fields.

For the two successful new-random candidates, mean event gap fell8.84276→7.85650 and immediate pitch repetition rose0.01136→0.04598. These are selected pairs, not a population quality estimate. Rest amount did not improve because it was fixed by design. Human musical impressions remain unobserved.

[Detailed experiment and limitations](2026-11-12-silence-return-cycle46-overview.md).

## New repertoire: rights reviewed, not admitted
Two Gymnopédies by Satie, contributed by Evin Robertson, were obtained as original MIDI/LY files. Historical score incipits were visually compared. The LY explicitly excludes modern Dover translation additions and dedicates the typesetting to Public Domain; that is a legacy dedication, not CC0 or a universal legal guarantee. The exact Dover physical impression was not established and the comparison is not exhaustive collation.

- No.1 / Mutopia37: original upper-track MIDI has two unmatched note-offs at tick13824, channel0, pitch66. Independent event pairing confirms the issue. No repair, note deletion or lower-track substitution was performed. **Technical-blocked, untrained, unscored.**
- No.2 / Mutopia38: original upper track has306 notes/124 groups and is accepted unchanged. A pre-fixed26-reference screen detects one exact eight-note interval pattern shared with Beethoven904. **Screen-blocked, untrained, unscored.** This is not a copying or copyright determination; different source provenance does not automatically override the gate.

Both belong to one Satie/Robertson source series and must not be split across roles. New composer/contributor provenance is useful, but neither work has increased the actual training set. Original bytes are reserved in separate blocked categories, not mixed into training materials.

[Rights evidence](../datasets/research-satie-cycle46-20261112.json) · [Latest status](../datasets/research-satie-status-cycle46-20261112.json) · [Independent source check](2026-11-12-satie-cycle46-independent-review.json).

## Verification and current state
Final local414 tests:413 pass, one existing AudioAnalyzer integration skip. Dependency-free414 tests:373 pass,41 expected optional skips. Compile/diff checks pass. Independent segmentation audit200 cases/1284 checks, output audit148 assertions, repeat exact except CPU and known-control parity are recorded. No raw MIDI/LY/audio or private generated sequences enter Git.

Training remains18 works/5512 selected notes/4190 onset groups; Groove58 training/16 observed-untrained/1076 unscored-untrained. Dowland remains observed-untrained, Lully screen-blocked, A–D human feedback unanswered. Exact-head CI and LIME readback are recorded in the PR after publication, not presumed here.
