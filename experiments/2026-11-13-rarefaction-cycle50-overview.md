# Cycle50: equal note-count pitch diversity, exploratory

Read-only reanalysis of all 36 already-observed Cycle49 outputs. No new training, generation, held-out test, source admission, source modification, or copy re-clearance. All input hashes match the Cycle49 reproduction ledger before and after analysis. This is a new analysis, not new musical experience.

## Finding

The raw/work-equal/family-equal output mean observed distinct pitches were 19.25/17.67/17.33, but output note counts also differed. Exact combinatorial rarefaction gives expected distinct **exact MIDI pitches** in a uniform subset of k note events, without replacing notes. It ignores temporal order, duration, harmony and perceived repetition.

| k | raw mean | work-equal mean | family-equal mean | eligible per mode |
|---|---:|---:|---:|---:|
| 4 |3.776552|3.746059|3.743687|12/12|
| 8 |6.942562|6.810511|6.807346|11/12|
|16 |12.037790|11.655026|11.652992|11/12|

At four notes, all candidates are eligible and expected distinct pitch counts are close. Thus the larger unadjusted distinct-count gap should not be interpreted as equally large loss of pitch diversity at equal note count. This does not isolate a causal weighting effect or prove equivalence: both pitch distribution and output length are model outcomes, twelve seeds are not independent corpora, and source corpus remains fixed. The k=8/16 estimates condition on eligibility and omit one explicitly reported sparse candidate per mode, not necessarily the same seed; do not silently compare them as complete-cohort results.

The k values are an exploratory choice after observing Cycle49, including knowing its smallest output had four notes. No significance test, new model selection, or music-appeal ranking is claimed. Rarefaction also does not detect whether an identical phrase repeats. Original silence and original output distribution remain unchanged.

## Reproduction and limitations

`tools/run_rarefaction_cycle50.py --source <private-cycle49-directory> --output <new-json-path>` recomputes the result from unchanged private files and the committed reproduction ledger. All exact rational values, per-output eligibility and input hashes are retained in the report. Replay matches all fields except CPU. Four synthetic tests include exhaustive enumeration of all subsets of all sequences over three symbols with lengths 0 through 5, invalid input, insufficient notes, and source nonmutation. This verifies the formula, not its musical adequacy.

Next useful work is human listening and order-aware repetition analysis, or an explicitly controlled leading-rest generation experiment, not maximizing this descriptor. Training remains 18 works/5512 notes/4190 groups; rights-clear new admissions 0. A-D feedback remains unanswered. No background generation remains running after this bounded analysis. Future scheduled work must inspect the newest PR/storage receipts and coordinate a single writer before changes.
