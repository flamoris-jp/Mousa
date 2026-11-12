# Second research cycle: representation, copying warnings and MIDI timing

## Questions
1. Does factorizing pitch and duration improve sparse-event prediction?
2. Can an explicit adapter preserve trailing silence and original generated pitches?
3. Does the first experiment's 70-step match actually contain a copied melody?

Use the same three already-inspected diagnostic works. This is not new held-out
evidence. Keep order=1, prior mass=1, seeds 7/17/29 and 128 output steps fixed.
Both variants use the SAME context/backoff, 26 pitch/rest symbols and 128 positive
durations: 3,328 event outcomes. Joint uses a joint table; factorized uses pitch
and duration marginals from that same context. Their NLLs are comparable to each
other, NOT to the previous train-vocabulary-plus-UNK metric. No test-fitted
vocabulary or changed source split.

## Measurements

| Model | Dev pitch / 36 | Dev duration / 36 | Test pitch / 52 | Test duration / 52 | Test event / 52 | Test NLL |
|---|---:|---:|---:|---:|---:|---:|
| Joint | 2 | 4 | 4 | 8 | 1 | 9.601986 |
| Factorized | 2 | 14 | 4 | 27 | 2 | 8.116599 |

Duration generalization in this tiny diagnostic improves; pitch remains poor.
This does not establish musical appeal. Uniform prior over durations 1..128 also
produces sparse generations (as few as five onsets across eight bars), a new
failure to investigate rather than hiding behind lower NLL. Next: compare a
musically motivated duration prior under unchanged held-out evaluation and use
relative pitch while preserving separate representation-ablation controls.

Twelve MIDI files were generated (2 models × guard on/off × 3 seeds), with exact
candidate hashes and metrics reproduced by a second run. All twelve round-trip
back to exactly the generated tokens with the new adapter, including original
pitches and end-of-track silence. PR #6 remains untouched; the adapter wraps its
strict parser, does not introduce general MIDI support, and explicitly normalizes
source melodies only when requested. Optional mido 1.3.3 tests cover restoration.

## Corrected interpretation of the earlier copy warning
The old 70-step longest exact substring contains **68 REST and 2 HOLD tokens,
zero note onsets**. It is therefore NOT evidence of a copied melodic phrase.
The prior warning was a diagnostic false alarm caused by the representation.
The first report is historical; this correction is the current interpretation.

Added an eight-note phrase fingerprint: seven intervals, eight durations and
seven inter-note gaps. It detects exact rhythm/interval phrases under constant
transposition, ignoring leading/trailing silence. A generation guard rejects
matching windows, with a bounded 64 retries then explicit `blocked` result,
not an arbitrary fallback. A constructed repetitive-source test demonstrates
blocking and deterministic behavior. The twelve diagnostic candidates triggered
zero phrase rejections and zero matching eight-note phrases, so these particular
samples do NOT demonstrate a measured improvement from enabling the guard.
Shorter, transformed and perceptual similarities remain untested. No candidate
is declared legally original or musically attractive without further review.

## New independent-source investigation
Three candidate works, Mutopia 888, 889 and 789, have per-version PD evidence and
typesetter contribution dedication in their LilyPond source. Their composition,
historical arrangement and linked MIDI encoding evidence is separated in
`datasets/research-candidates-20261112.json`, with URLs, acquisition dates and
hashes. They are **not used for training**. All are 6/8; the current reader only
accepts 4/4. Do not silently change meter. 888 and 889 share a source collection;
family/near-duplicate and collection-correlation review remains necessary.
No raw MIDI, LilyPond, HTML, contact details or audio is committed.

## Verification and limitations
- With optional mido installed: 62 tests discovered, 61 passed, existing real
  AudioAnalyzer integration skipped (environment not configured).
- Without mido: adapter tests are additionally skipped, not called passed.
- New workflow runs the tests with mido installed; it still does not run the
  AudioAnalyzer integration or native neural trainer.
- First comparison attempt failed on a duplicate result-dictionary key. The
  harness was corrected before measurements; failed output was retained locally.
- JSON result records exact source hashes, metrics, costs and MIDI hashes.
- No GPU, paid service, merge, release, deployment or Cantabile edit performed.

Reproduce with the same prepared/pinned inputs as the first comparison, replacing
`tools/compare_event_baselines.py` with `tools/compare_factorization.py` and using
a fresh output directory. Both scripts refuse overwriting earlier experiments.
