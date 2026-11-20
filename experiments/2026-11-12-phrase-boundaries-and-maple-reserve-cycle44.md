# Cycle44: both phrase boundaries, plus one verified reserve work

## Phrase variation
The fixed comparison keeps 17 training works and the same five previously inspected seeds. Whole-C octave placement minimizes entrance, internal and exit group-anchor differences together. All timing, held-note lengths, rests, velocities and templates remain unchanged. This is a post-generation minimum-pitch proxy, not a learned melody voice or evidence of attractiveness.

Control completes 5/5; greedy and whole-phrase edits both complete 3/5. Two empty-A failures remain. In one completed example the greedy exit of 15 semitones becomes 3, still exceeding the unchanged exit of 2. Matched mean event gaps are 8.26051 / 7.45716 / 7.36414 for control / greedy / whole-C, while distinct pitches are 20 / 20.3333 / 19.3333. Thus lower movement comes with less pitch diversity. Repetition fraction and every rest/occupancy descriptor remain unchanged between the two edits. Full outputs pass the unchanged 21-reference copy guard. No safety fallback selects an alternative path after rejection.

See [fixed design and results](2026-11-12-phrasewide-register-cycle44-overview.md). The independent synthetic Cartesian oracle passed 1,000 cases; a separately oriented suffix-cost audit and temporal/collision checks passed 3,082 assertions on completed outputs. Repeat files are byte-identical; CPU is excluded from report equality. Prior control and greedy states are exactly reproduced. Known-seed reuse, common denominators, failures and pre-fit code/metadata corrections are retained.

## Material expansion: reserved, not trained
Maple Leaf Rag (Mutopia23) now has individually dedicated Public Domain MIDI/LY and a visually reviewed historical Stark score from Washington University's Gaylord Music Library. The physical impression may be later than the printed 1899 edition: that uncertainty is recorded, not hidden. Original MIDI preserves both staves: 1,193 upper-staff and 1,373 lower-staff notes, including the upper-staff initial 288 ticks and lower-staff onset at zero.

A pre-fixed 25-reference exact-eight-interval / global 0.80 screen finds no flags. This is only the unchanged bounded screen, not legal or plagiarism certification. It is the same Joplin / Chris Sawer / Stark family as existing training work263; it must not be presented as an independent composer or split across a family boundary. It remains **reserved, untrained and unscored** until a separate fixed assignment. Training stays 17 works / 4,319 selected notes / 3,428 onset groups.

[Rights and source ledger](../datasets/research-maple23-reserved-cycle44-20261112.json) · [Independent raw MIDI and source check](2026-11-12-maple-cycle44-independent-review.json).

Elite Syncopations1540 remains pending. A retrieved scan proved to be a modern clarinet arrangement, not the claimed historical piano original, and was rejected. A prior acquired-date field mixed JST into a UTC label; an explicit correction preserves the original snapshot and distinguishes local write time from exact HTTP acquisition time. No pending raw file is admitted or archived as training material.

## Verification and storage boundaries
Final code: 397 tests, 396 pass and one existing AudioAnalyzer integration skip. Dependency-free: 397 tests, 356 pass and 41 expected optional-dependency skips. Compile and diff checks pass. No raw MIDI/LY/audio, private candidate notes or model weights enter Git. LIME archival and exact-head CI are verified separately in the PR after publication.

Groove stays 58 training / 16 observed-untrained / 1,076 unscored-untrained. Dowland remains observed-untrained; Lully remains screen-blocked with blank human-review fields. A–D listening feedback is still unanswered. No human preference, musical attractiveness, independent-composer generalization or production readiness is claimed.
