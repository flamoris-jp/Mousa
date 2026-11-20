# Cycle 53: larger cleared-corpus learning diagnostic

## Executed scope

This is an actual CPU fit of fixed music-feature count baselines, not a trained
Maidionis specialization, deployed Mousa service, or subjective composition test.
No GPU, generation, audio rendering, Cantabile project mutation, merge or release.

A pre-metric split selected one deterministic representative MIDI from each of
428 conservative source-family components: 307 train, 66 validation, 55 test.
All exact MIDI bytes, rights/quality allowlists, attribution and grouping evidence
were independently checked. 284 representatives are PD-declared and 144 CC BY;
CC BY-SA, unresolved rights, transcription warnings and protected-cohort families
are excluded. Six previously seen components were locked to training only.
Family closure includes known related pieces, editions and approximate matches.
The screen is bounded and is not proof that every shared motif was found.

The model projects the highest non-drum pitch at each exact onset across tracks.
It does **not** identify an annotated melody. It discards note duration, dynamics,
other simultaneous voices, tempo and instrumentation. At most the first 2,048
onsets of each representative are used. Pitch differences have 49 fixed clipped
bins; inter-onset intervals have 25 fixed half-octave log2 beat bins. Predictions
are teacher-forced, and all models score identical target indices starting at 2.

Plan v3 was frozen before scoring. Earlier v1/v2 plans were superseded during
static safety review, before any predictive metrics; those records are retained.
No model or hyperparameter was selected using validation or test outcomes.

## Results

Natural-log NLL, **macro-average over 55 test families**, lower is better.
Each feature has 25,030 test targets. Accuracy is shown separately in the JSON.

| Training / model | Pitch interval NLL | Rhythm IOI NLL |
|---|---:|---:|
| No-data uniform | 3.8918 | 3.2189 |
| Full train unigram | 3.1851 | 1.5878 |
| Full train bigram | 2.7185 | 1.0257 |
| Full train trigram | 2.7155 | 0.9104 |
| Full train shuffled trigram | 3.3112 | 1.0831 |
| Primary nested 18 / trigram | 3.2442 | 1.0508 |
| Full 307, equal token budget / trigram | 3.0634 | 0.9452 |

Full-train trigram accuracy: pitch **25.65%**, rhythm **74.85%**, family-macro.
Uniform top-1 ties use the lowest token deterministically, so its accuracy is
not a randomized chance-level estimate; uniform NLL is the useful no-data bound.

The primary 18-family subset contains 8,354 feature tokens versus 144,453 for
full training. The equal-budget condition distributes exactly 8,354 tokens over
307 deterministic family prefixes. It still has fewer within-family trigram
transitions (7,740 vs 8,318), different repertoire and shorter-prefix bias.
This therefore does not isolate a causal effect of “number of songs.”

Three additional fixed 18-family seeds all had higher test NLL than full training:
pitch 3.1554–3.4267; rhythm 1.0382–1.1569. All corresponding equal-budget runs are
reported, not selected. Validation results and pooled metrics are retained too.

Improvement is heterogeneous: relative to primary-18 trigram, full training
improved pitch NLL in all 55 test families, but **rhythm worsened in 19 of 55**.
Against full unigram, trigram worsened on 2 pitch and 3 rhythm families. Context
helps on average; this is not a promise that every item improves.

## Reproducibility and safety

Run 1 consumed 19.32 CPU seconds; replay 20.79 CPU seconds. All result fields
except measured CPU time match exactly, and private count-table bytes match.
Replay uses the same already-observed cohort and is not independent validation.
No projection failures occurred. The durable attempt journal marks families
before every score; the actual-use ledger marks all training and observed
validation/test family members, so none may later be relabeled a fresh test.

Independent checking recomputed all 10,890 row denominators, 180 aggregate rows,
analytic uniform NLL, and 242 full-model family/feature probability evaluations.
The unit suite ran 475 tests: 474 passed and one pre-existing external AudioAnalyzer
producer integration skipped because `MOUSA_STEM_EXPORTER` was not configured.
The 18 new core/runner safety tests passed, including exact failure reasons.

The earlier Cycle 52 result used 18 historically observed works, retrospective
linked-family folds and previous-duration context for exact timing. Its metrics
are **not numerically comparable** with this new binned, highest-onset task.
This experiment shows transferable predictive structure in cleared material;
it does not establish musical appeal, originality or publication eligibility.

## Reproduce

Use the private, hash-pinned split and evidence files from LIME, preserving
attribution and updating only machine-local input mappings in a separately
recorded reproduction manifest. Do not silently rewrite the frozen split.
The runner requires optional research dependency `mido` (tested 1.3.3), Python
3.12.14, and no GPU. Core repository tests remain dependency-light.

```
python tools/run_corpus_learning_trial.py prepare --split SPLIT.json --plan PLAN.json
python tools/run_corpus_learning_trial.py run --split SPLIT.json --plan PLAN.json --out NEW_RUN
PYTHONPATH=src python -m unittest discover -s tests -v
```

No raw MIDI, token sequences, count checkpoints or machine-specific paths are
committed. Private checkpoints must retain their linked source attribution
sidecar and extraction-change notice. The result JSON carries digests and
artifact references; storage completion must be verified separately.
