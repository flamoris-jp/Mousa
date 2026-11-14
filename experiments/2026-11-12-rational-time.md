# Cycle 8: rational durations and a qualified composer-transfer result

## Exact timing without deleting ornaments

Implemented `rational_events.py`: positive exact Fraction durations in quarter
note units, a note/rest identity, and note/release velocity. Preserve leading,
inter-note and trailing rests and adjacent repeated-pitch note onsets. Canonical
JSON uses reduced integer numerator/denominator pairs; no floats. Exact return
to requested PPQ either succeeds or explicitly rejects, never rounds.

Tempo, CC7 volume, program, original same-tick order and meter remain in the
original TickMelody; the rational event list is **not** a replacement for that
performance representation or Cantabile. Note velocity is preserved, not the
entire expressive performance in the event list alone. Originals stay unchanged.

Limits:8193events/4096notes,1024quarters, denominators<=32767 and joint minimum
PPQ<=32767. The combined bound rejects incompatible prime denominators before
large fraction accumulation and guarantees a possible MIDI resolution. Tests
cover1/384-quarter timing, repeated pitch, all rests, JSON strictness, absent
metadata, incompatible PPQ and invariance between384/480PPQ.

Compare three rights-reviewed sources without fitting/scoring a new model:
1578 is already observed from cycle7 and is only the on-grid control;
1585/1587 are preserved technically but remain unscored and excluded from the
frozen sixteenth model.1040 is omitted from this new experiment because its
cited edition is still too vague; earlier diagnostic observations remain history.

| Work | Notes | Rational events | Minimum exact dense-grid cells | Compact rational JSON bytes | Compact tick JSON bytes |
|---|---:|---:|---:|---:|---:|
|1578|170|180|552|1621|1634|
|1585|100|110|31488|1009|968|
|1587|108|120|27552|1124|1048|

For the two off-grid sources, an exact dense grid needs384 steps/quarter,96times
sixteenth resolution. Rational events avoid the long sequence and preserve the
2/6 ornaments that hypothetical sixteenth rounding would collapse. Full note
start/end/pitch/velocity and selected EOT round-trip exactly; doubling original
PPQ and every source event tick leaves canonical beat events identical.

These are representation counts and explicitly defined serialized formats,
not measured neural memory/runtime or musical-quality improvements. Hypothetical
uint8 dense-grid bytes equal the cell counts and omit velocity. Full descriptive
rational JSON including velocities is larger:16711/10219/11168bytes. On the
already-on-grid1578, its552-byte hypothetical grid is smaller than either JSON
event form. Compact integer-tick events plus a PPQ header are also slightly
smaller than fractional JSON on the off-grid pieces. Fractions provide normalized
cross-PPQ musical units, not automatic byte compression or a free generative
model. No fine-grid arrays or rounded corpus are emitted.

## Another previously unscored work, not another independent contributor

Foster's Slumber My Darling (370) passes exact-grid projection unchanged. Named
composer1826–1864,1862 Horace Waters edition independently corroborated by Johns
Hopkins Levy068/113, and Stan Sanderson's exact contributed MIDI/source PD
statement support local melody research. The same contributor also encoded
train376: this is **new-composer transfer with contributor overlap**, not a
fresh contributor-family benchmark. It was technically inspected earlier but
never fitted or scored before this run. The source has eight full-bar score
rests, not a pickup; origin0 and first note atstep96. No cropping.

Retain the original cycle6 model/config hashes and four training works. The two
Schubert works already scored in cycle7 are explicitly marked observed and are
not rescored as fresh here. Source similarity checks still include them.
Foster370 is test-only;113events,108notes. Fixed-model results:

| Model | NLL/event | Exact event count | Pitch count | Duration count |
|---|---:|---:|---:|---:|
| selected bar k1 |3.832389|17/113|26/113|75/113|
| same bar k0 |4.524361|10/113|20/113|66/113|
| melodic, no position |4.111161|30/113|42/113|66/113|

NLL favors the selected model; exact and pitch top-one counts favor the melodic
control. Report both, without redefining the objective after inspection. This
is one additional work, not broad generalization or evidence of attractive
composition. The piece is now observed; no future fresh-set relabeling.

## Search limitations and reserved sources

A bounded five-candidate pass found Bach Air1534, contributor Mike Blackstock,
a genuinely different composer/contributor from fitted data. Exact-tick reader
accepts its flute part and preserves ornaments. The source describes a **new
flute/guitar adaptation** from Bach-Gesellschaft and dedicates the contribution
to PD, but a separate adaptation author is not explicit. Conservatively keep
it pending until attribution is sufficiently established; no fitting or scoring.
Do not pretend this is the original orchestral instrumentation or silently use
its off-grid melody in the old model. This cycle does not complete a new
contributor-independent evaluation set.

Foster371 remains pending an edition-catalog mismatch.1536 fails supported meter
and source retrieval;645 source archive retrieval timed out. No unsupported
meter conversion or archive-rights guess. Exact URLs/hashes/failure records are
in the reserved-source ledger; contact details and local paths excluded.

## Verification and next hypotheses

- Full suite139 discovered:138 passed, one existing actual AudioAnalyzer
  integration skip. Eight new rational-representation tests.
- All three representation roundtrips and original-file hashes pass. Repeated
  canonical hashes/metrics match excluding timing. Foster report repeats exactly.
- Frozen model/old-reader hashes unchanged; source-specific metadata-only driver
  label update prevents calling Foster a Schubert contributor-family test.
- No new neural model, rational-duration generator, human rating, audio release,
  GPU/paid operation, deployment, main merge or live Cantabile modification.

Next compare a generative rational-duration model with a properly fixed output
support and unknown-duration policy; likelihoods from incompatible alphabets
must not be compared as if equivalent. Preserve the current frozen baseline,
reserve genuinely unscored independent rights-cleared sources, and retain the
human listening questions as separate evidence. A representation's exactness
does not tell us which ornamental timing a person will prefer.

Reproduce `tools/compare_exact_time_representations.py` with reviewed `--source-root`,
`--rights-review datasets/research-rational-source-review-20261112.json` and new `--output`. Frozen
Foster evaluation uses the existing driver with the new Foster manifest; no
Schubert scores are used for fitting or model reselection.
