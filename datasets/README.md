# Datasets

This directory holds reviewed catalogs and policies, not raw corpora. [trial001-sources.json](trial001-sources.json) lists three exact Mutopia works, source URLs, SHA-256 hashes, selected tracks, edition/inputter details and the publisher Public Domain declaration reviewed on 2026-11-11.

`python tools/prepare_trial_corpus.py --output .cache/trial001-corpus` is an explicit allowlisted download. Add `--source-dir` for offline recovery from existing bytes. It is not a general crawler or automatic legal reviewer. It records its review evidence as text, not as an original HTML snapshot.

Raw/processed material stays in ignored local storage. Consult [DATA_POLICY](../docs/DATA_POLICY.md) before broadening sources; split by composition/arrangement family, preserve transforms and keep rights for code, datasets, weights and media separate.
