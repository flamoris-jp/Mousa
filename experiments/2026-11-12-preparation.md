# Adaptive research preparation — 2026-11-12

## Purpose
Finish ready preparation immediately instead of stretching a checklist over
14 days. Related: #2, #3, #4, #7. No original issue is closed by this work.

## Source state
- Main checked out at `3c74f81` (stem intake merged).
- Trial 001 PR #6 separately checked out at
  `83ca8d477b84a7a8ceff0d80e0af4050b5d27b37`; it remains unmerged and untouched.
- Read current Maidionis specialization contract and Cantabile MIDI protocol.
- No changes to production, Cantabile projects, model weights or external assets.

## Actually run
- Main Python tests: 28 discovered, 27 passed, 1 optional AudioAnalyzer integration
  skipped because MOUSA_STEM_EXPORTER was not configured. This is not a full
  integration pass.
- Added a MIDI research-manifest preflight and 15 tests covering rights records,
  quarantine, SHA-256 binding, explicit permission, source paths, family leakage,
  duplicate bytes and refusal of unreviewed audio candidates.
- Combined tests: 43 discovered, 42 passed, the same 1 integration test skipped.
- No GPU, paid computation, native model training or listening evaluation run.

## Finding
The previous research plan confused observation dates with work allocation.
The new protocol is an adaptive hypothesis loop. The known grid-v1 weakness
(1/45 new onsets versus baseline 2/45 in prior CI, not a new measurement here)
justifies an onset/event-centered statistical comparison before enlarging models.
The current main README also predates the merged stem intake; only the observed
status is corrected, and pending PR #6 is not described as shipped.

## Limitations and next experiments
The intake preflight cannot authenticate license claims or find approximate
melody matches. Human source review and a real MIDI parser remain required.
Rights records are research assertions, not a legal opinion. Next: revalidate
exact source evidence, reproduce the pinned MIDI frontend tests, and compare
bounded event baselines with fixed seeds. The known three-song set is a mechanics
diagnostic, not a sealed or sufficiently sized musical benchmark.

## Reproduction preparation completed in the same session

The three exact Trial 001 pages were re-fetched and their Public Domain fields
observed. Exact MIDI bytes were fetched using PR #6's allowlisted, hash-pinned
preparation command. Page hashes, acquisition timestamps, author/inputter,
source editions and source MIDI hashes are recorded in
`datasets/research-source-audit-20261112.json`. They are quarantined for any new
benchmark pending its separate review; existing historical clearance is not
silently promoted to a new training corpus. No raw MIDI or HTML is committed.

The fixed Maidionis education package was installed in an isolated virtual
environment with mido 1.3.3 and jsonschema 4.23.0. The first test attempt passed
15 tests but failed setup because the contracts package had not been installed.
After installing the pinned package correctly, **all 22 Trial 001 Python music
tests passed** in 11.214 seconds, including MIDI roundtrip, family separation,
transposed duplicates and provenance tampering. This was a real local rerun;
it did not run the native trainer or imply a new musical improvement.

Reproduction recipe (separate checkouts, never overwrite existing directories):

```sh
# checkout PR #6 at 83ca8d477b84a7a8ceff0d80e0af4050b5d27b37
# checkout Maidionis at a987eeeea11e3971d3b9708bfff6b3545cdb601f
python -m venv .venv
. .venv/bin/activate
python -m pip install mido==1.3.3 jsonschema==4.23.0
python -m pip install --no-deps "$MOUSA_MAIDIONIS_ROOT"
python tools/prepare_trial_corpus.py --output "$MOUSA_TRIAL_CORPUS"
python -m unittest discover -s specializations/melody/grid_v1/tests -v
```

Set the two environment variables to the chosen dependency/corpus locations
first. This tests Python mechanisms only and is not the native CPU build recipe.
