# Cycle 6: explicit form comparator and a fresh-set admission failure

## Fresh evaluation: freeze first, admit zero rather than relax silently

Saved the selected cycle5 score-origin/bar/relative/empirical model at k1,
controls k0/no-position, training IDs, exact source-code and manifest hashes
before any new-source model scores. Selection is based only on the previous
exploratory family diagnostic. See `2026-11-12-frozen-transfer-plan.json`.

The Finnish candidates remain pending because actual old-score melody identity
is unverified. A bounded six-candidate named-composer pass did not produce an
admissible new test piece:

- Schubert1578,1585,1587,1558: individual PD declarations and contributor
  dedication, historical edition evidence, but actual MIDI tempo changes.
  Independent mido inspection confirms 7,2,5,3 distinct tempo values respectively,
  not merely repeated equal-tempo metadata. No timing controls were discarded.
- Schubert1040, Wiegenlied D498: individual PD encoding declaration; Schubert
  Online independently dates the composition to late1816. Selected melody
  fails exact sixteenth-grid timing. No rounding or truncation was applied.
- Bach40 BWV772: old composition does not make the contributed MIDI PD. The
  encoding uses CC BY-SA3.0, and candidate tracks also fail the monophonic
  reader. No blanket claim is made that CC BY-SA forbids training, but this
  source was not approved in the current priority/scope review.

Exact acquisition evidence, source hashes and failure reasons are preserved in
`datasets/research-named-source-rejections-20261112.json`. No training or model
scoring on these six, no new held-out claim. A future tempo-map-aware parser or
finer rhythmic representation requires separate design/tests and provenance,
not an unreported relaxation to obtain a favorable benchmark.

## Form hypothesis and implementation

Does explicit return/variation give a greater sense of coherent flow, or simply
sound repetitive? Added a **handcrafted comparator**, not learned musical form:
2-bar A, transposed A′, independently generated 2-bar B, transposed A″. A′/A″
use a seeded nonzero semitone shift from±1/±2. Rhythm and rests are preserved in
the shifted motif. Chromatic transposition does not establish tonal coherence,
and the two shifts may be equal. This is a limited baseline to expose the next
research question, not a finished form model.

`generate_phrase_form` wraps the unchanged selected model. Pitch-range failures
reject an attempt rather than clip notes. Every merged eight-bar result gets
source-copy and consecutive-rest checks again across block joins. Bounded
fragment/whole-form attempts return an explicit blocked result, never an
unverified fallback. All selected seeds, transforms and failures are retained.

Three seeds fixed before audition (7,17,29), same model/6/8/8bars/tempo/register/
preview gain/rest cap12. Direct generation versus form gives six complete MIDI
and analytic sine previews. One form attempt rejected a pitch-range violation;
no source-copy or joined-rest rejection in these particular samples. Constructed
unit tests do exercise both join failures and exhausted retries.

All six pass exact MIDI roundtrip, no matching transposed eight-onset source
phrase, zero clipping, identical peak PCM16=9805, same preview duration. MIDI,
WAV and method-key hashes repeat exactly. Direct mean note count29.33 versus
form39; density changes along with form. Even a clear listening preference would
not isolate repetition as the cause, and these descriptors are not beauty scores.

## Private, optional listening

`docs/HUMAN_LISTENING_PROTOCOL.md` defines Japanese listener questions and a
recording contract: coherence, too-little/right/too-much repetition, replay
preference, optional timestamp/reason. A/B/tie/neither, technical failure and
missing feedback remain distinct. A missing answer is never scored zero.
No response has been collected or invented. Feedback is not automatically
training data and identifiable preferences must not enter public Git.

The renderer is the exact inspected `midi_io.py` from existing PR6 commit
`83ca8d477b84a7a8ceff0d80e0af4050b5d27b37`, verified by SHA before import.
It creates analytic sine plus second harmonic; no sampled SoundFont, outside
recording or commercial audio. Source licensing, renderer licensing, generated
similarity and public-release clearance remain separate. These are private
research auditions, not publicly cleared music. No audio/MIDI committed.

Opaque clip labels and presentation order are fixed with a recorded order seed;
the model-key is separate from listener materials and remains outside Git.
The researcher knows the methods, and deterministic reproduction permits
recovery: this is presentation masking, not a double-blind or security claim.
For a single listener/three pairs, report descriptive responses, not population
significance. Prior A/B feedback, if supplied, must retain its original IDs and
must not be silently reassigned to these new pairs.

## Verification and what remains

- Full suite113 discovered:112 passed, one existing real AudioAnalyzer test
  skipped because its integration environment is absent.
- Seven new form tests pass: deterministic exact length, non-clipped bounds,
  actual source-match across joins, rest-run join, exhaustion, settings.
- Repeat artifacts, compileall and diff checks pass. No live Cantabile mutation,
  new data admission, GPU/paid operation, deployment, main merge or media release.
- No human listening yet, no independently enlarged evaluation set this cycle.

Next: preserve the frozen model while reviewing tempo-map/finer-grid extraction
as a separate technical experiment; locate a historical score incipit for the
reserved folk sources; use opt-in feedback to decide whether repetition is
helpful before building a more elaborate form model.

Reproduce private artifacts with `tools/prepare_phrase_audition.py --corpus`,
`--manifest`, `--origins`, `--preview-module` (exact pinned PR6 file) and a fresh
`--output`. Reference manifest/origins are the cycle4 exploratory and cycle5
metrical-origin files. Do not put generated media or listener responses in Git.
