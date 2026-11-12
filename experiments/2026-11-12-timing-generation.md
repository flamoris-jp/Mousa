# Cycle 18: timing prediction versus generated behavior

## Question and fixed comparison

Does the previous-gate timing context, which improved timing likelihood in the
already observed Brahms and Adam probes, also change generated lines usefully?
This is a generation comparison, not a new held-out predictive result. The four
old training works and 364 training events are unchanged. Adam640, Brahms580,
Foster370 and the two scored Schubert works remain observed and unfitted.

Before generation, fix seeds 0..9 and compare only timing context off/on. Both
use pitch continuity, a 1/4 uniform-pitch mixture, exact optimized feasibility,
9216-tick eight-bar 6/8 output, at most 384 ticks trailing silence, the same
256-note budget and polyphony bound 3. Alternate execution order by seed parity.
No seed replacement, output ranking or retuning. Previous-gate shrinkage is k=4.
These are different stochastic systems: same seeds do not align musical events.

## Results

All 10 candidates in each condition completed, with zero copy-guard failures
against the four training works plus observed580/640. The guard checks exact
8-onset interval windows in generation and canonical order. It does not prove
perceptual or legal originality. All 20 MIDI files round-trip exactly, retain
EOT9216, have no active same-pitch retriggers and satisfy polyphony/tail bounds.

Means over 10 accepted outputs per condition:

| Descriptor | Timing context off | Timing context on |
|---|---:|---:|
| Notes | 28.1 | 31.0 |
| Onsets overlapping a previous note | 0.383380 | 0.152751 |
| Silent fraction of timeline | 0.371875 | 0.171875 |
| Distinct pitches | 12.6 | 13.3 |
| Consecutive same-pitch fraction | 0.190241 | 0.226704 |
| Mean absolute pitch interval | 3.305624 | 3.389690 |
| Above-octave interval fraction | 0.031330 | 0.030113 |
| Gates shorter than 24 ticks | 0 | 0 |
| Actual trailing silence, ticks | 220.8 | 240.0 |

Timing conditioning reduces overlap yet also reduces total silence: these are
not equivalent metrics. It produces denser lines and a larger pitch vocabulary,
but more adjacent same pitches. Neither vocabulary size nor same-pitch fraction
alone measures monotony; motif recurrence and phrase-level variation are not
measured in this cycle. A later suggestion to add run/motif metrics arrived
after initial generation had started, so it was not retroactively added to the
predeclared analysis. Do not call these changes an improvement in attractiveness.

Generation-only wall time for 10 seeds was 0.492s versus 0.593s; repeat 0.460s
versus 0.517s. CPU totals and per-output timings are retained. Small local timing
measurements, not an end-to-end performance guarantee. Both conditions used the
same implementation; conditioning adds computation even with fewer overlaps.

## Reproduction and metadata correction

Initial and repeat MIDI bytes and all non-timing condition metrics match. The
context-on files also match the previously generated cycle15 mix1/4/tail384
outputs. This is an ablation of a known system, not 20 independent new samples.

During execution the parent backfilled the observation registry with already
scored1578/1558/370/580 from immutable historical reports. Only that registry's
hash changed between plans, besides creation time and derived plan hash. No
model, training data, generation code or observed score changed. Preserve the
initial plan and record this metadata difference rather than rewriting it.
The registry test verifies those observed works are absent from the fixed
training split and their result digests remain intact. It is not a complete
source inventory or an automatic rights authorization.

## Next hypothesis and human evaluation

Prediction and safe generation are necessary but do not establish a coherent
phrase, meaningful repetition, harmony or cadence. Test phrase recurrence at
multiple scales prospectively rather than minimizing adjacent repetitions.
The separate timing-context listening design fixes seeds0,1,2 before any
listening; preserves failures, overlaps and silence; and separates naturalness,
repetition/variation, ending impression and replay preference. No new audio,
delivery or human responses are claimed in this cycle. Personal preference is
not inferred from an emoji, download or missing answer.

## Source research and verification

Source-rights findings are recorded separately in the cycle18 reserved-source
ledger. A reserved candidate is neither a new training example nor a completed
held-out result. Keep composition/contributor/edition families together, and
freeze the next model and eligibility screen before scoring a new work.

Final tests and independent evidence are recorded alongside this report. No
main merge, public media/corpus release, live Cantabile edits, GPU or paid work.

- New reserved candidate: Telemann TWV40:107 / Juanma Perez (Mutopia1692),
  a new composer/contributor relative to the observed corpus. Explicit legacy
  typesetter PD dedication and 1728–1729 first-edition incipit corroboration,
  not a title-only or free-download inference. Exact edition-wide collation is
  not claimed. First-movement track1 has192notes,4/4,PPQ384 and an explicit
  initial eighth rest192ticks, not a pickup phase correction. Independent exact
  modeled roundtrip passes. No fitting, predictive scoring or similarity
  admission yet; all movements/parts stay one family. Alternative885 remains
  pending edition confirmation;268 has unresolved arranger S.W. rights.
- Full suite208 discovered,207passed,1existing actual AudioAnalyzer integration
  skip. Dependency-free suite208 discovered,170passed,38expected optional skips.
  Compileall and diff checks pass. Test counts include2new generation tests and
  1observation-registry test. No native GUI or human-listening claim.
