# Cycle51: recurrence of ordered onset-group pitches

## Result

All 36 unchanged Cycle49 candidates were reanalysed. Simultaneous notes are grouped before analysis, avoiding arbitrary within-chord ordering. For each candidate, 100 deterministic permutations preserve its exact inventory of pitch groups and group count. This is a descriptive shuffled-order control, not another generated music corpus.

Mean repeated-window fraction for two-onset windows:

| weighting | observed | shuffled control | observed minus control | eligible |
|---|---:|---:|---:|---:|
| raw | 0.006481 | 0.012454 | -0.005973 | 12/12 |
| equal work | 0.002874 | 0.022043 | -0.019170 | 12/12 |
| equal linked family | 0.021852 | 0.026503 | -0.004652 | 12/12 |

No exact four-group window recurred in any eligible candidate: raw 11/12, equal-work 12/12 and equal-family 12/12 eligible. The excluded raw sample has fewer than four onset groups; notes and onset groups are different denominators. This is **not evidence that the music is interesting**. Exact pitch-group recurrence is sparse, whereas perceived monotony can arise from rhythm, contour, harmony, phrasing or missing development. Repetition can also be desirable. The new diagnostic does not justify maximizing uniqueness or selecting a winning weighting scheme.

## Interpretation and next hypothesis

Cycle50's pitch-inventory statistic could not describe order. This diagnostic adds that distinction and does not find excess exact short-sequence recurrence over the shuffled-inventory control in these mode means. It has a floor effect for four-group windows and misses transposed or approximate motifs. We should next investigate rhythm/contour recurrence and controlled phrase return, with listening, rather than treating this zero as success. This is post hoc exploratory analysis of one fixed source corpus, not a causal test or independent held-out evidence. Mode means can hide per-candidate differences; all rows are retained. Overlapping windows are dependent; no p values or significance claims are made.

## Verification and scope

- Run `python tools/run_order_cycle51.py --source <private-cycle49-directory> --output <new-json-path>`.
- All 36 source hashes match the unchanged Cycle49 reproduction ledger before and after analysis.
- Two runs match exactly excluding CPU time (0.138 / 0.108 CPU seconds).
- Five focused tests cover known repeats, order sensitivity, insufficient groups, chord-order invariance, duplicate pitches, invalid values, deterministic controls and nonmutation.
- Full local suite: 452 tests, 451 pass, one existing optional AudioAnalyzer integration skip. No new live integration claimed.
- No new MIDI, training, source admission, evaluation-set use, copy clearance, human rating, GPU operation or deployment. Training remains 18 melodic works. Existing 36 MIDI candidates remain unchanged in private storage; this cycle produces analysis only.
- GitHub PR fetch-with-diff returned transport errors twice. Current PR issue metadata and branch commit were independently read successfully; branch head was Cycle50 before this addition. No concurrent local research process found.
