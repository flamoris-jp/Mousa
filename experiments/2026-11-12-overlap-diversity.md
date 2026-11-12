# Cycle11: ornament performance without erasure; diversity-constrained selection

## Source intent and performed MIDI are different layers

Brahms580 bar12's historical score and LilyPond source show a sequential vocal
line with two small grace notes before D, not an intended vocal chord. In the
rendered MIDI, E64 (19200..19655), F65 (19534..19630) and D62 (19584..19776)
overlap. Old LilyPond grace/slur playback is a plausible explanation, but was
not reproduced with the original renderer/version, so it remains a hypothesis.
Keep both the original performance and the notation evidence; do not shorten
or remove notes to make one look like the other.

The new separate `overlap_midi` profile preserves different-pitch overlaps on
one channel, exact event order, velocities, meter/tempo/CC7/program maps and
selected/global EOT. It rejects ambiguous same-pitch retriggers while active,
unmatched note-offs and unsupported controls. Notes have canonical onset/end/
pitch ordering; the separate channel stream retains original same-tick order.
Frozen readers/models remain unchanged. This is selected-track research data,
not a full-project importer or automatic voice/ornament understanding.

## Actual rights-reviewed source preservation

Brahms580 vocal track1 now roundtrips all92 MIDI notes and9 meter declarations
without changing original bytes. Independent raw channel-message signatures
match on export. Maximum simultaneous notes3; overlap occupies242 ticks.
Hypothetically clipping each gate at the next onset would alter4 notes and
remove334 summed gate ticks. We measured that loss but did not perform it.
Overlap-time union and summed gate loss are different quantities.

A diagnostic onset-delta/gate representation exactly reconstructs every note's
start/end/pitch/velocities. Onset deltas may be zero; sounding gates remain
positive and can exceed time to the next onset. No negative rest or truncation
is required. It is NOT the old duration-only alphabet: future predictive models
must jointly specify onset timing, sounding gate and active-pitch constraints.
Same-pitch retriggers need explicit rejection/voice semantics, finite polyphony
and endpoint limits. Metadata/EOT and channel ordering remain sidecars. No new
model was fitted or scored on this source, and no output-support comparison
with incompatible alphabets is claimed.

The work is inspected and representation-tested, not untouched data. It remains
excluded from the old monophonic training corpus. A future held-out predictive
experiment must freeze model/task and perform family/near-duplicate screening
before scoring; this cycle does not claim independent generalization.

## Additional rights review

Cornelius583, *Ein Ton / The Monotone*, has a visually corroborated historical
University Society edition: printed350, composer/title,3/4,E-minor and repeated-B
opening agree with the supplied notation. The copyright leaf includes1909;
Daniel Johnson explicitly dedicates his typesetting to PD. Keep it grouped with
Brahms580 by contributor/publisher despite a different composer. Technical
admission remains untested. Its deliberately single-pitch melody is a useful
edge case, not a broad quality benchmark. Incipits rather than every note were
collated; no lyric use or unrestricted redistribution claim.

## Balancing the earlier selection objective

Predeclared exploratory reanalysis of the already observed20x4 cycle10
candidates, not fresh evaluation. Within each group retain candidates with at
least the control's distinct-pitch count and at most its repeated-pitch interval
fraction, then choose lowest above-octave leap fraction. The original control
is always eligible. No new seed selection, generation, fitting or human labels.

| Equal-group mean | First candidate | Leap-only selection | Diversity constrained |
|---|---:|---:|---:|
| Above-octave interval fraction |0.036151|0.002986|0.018694|
| Distinct pitches |14.20|12.95|15.40|
| Repeated-pitch fraction |0.222049|0.247754|0.194814|
| Mean absolute interval |3.198418|2.511870|2.902962|
| Onsets |31.10|31.30|33.30|

Six of20 constrained selections differ from control; in10 groups only the
control is eligible. This recovers some leap reduction while satisfying these
specific diversity floors. It does not prove better music: distinct-pitch count
can reward aimless motion, repeated notes can be expressive, and all outcomes
are selected using those same proxies. Keep human listening separate. The4
candidate budget and previous narrow copy-screen limits still apply.

## Verification and reproducibility

167 tests discovered,166 passed, one existing actual AudioAnalyzer integration
skip. Seven overlap-profile tests, four selection tests and two onset/gate tests
added. Full repeated source-intake and selection reports are byte-identical;
compileall and whitespace checks pass. No live Cantabile mutation, public audio,
raw corpus, weights, GPU/payment, merge or deployment.

Run `tools/probe_overlap_representation.py --source REVIEWED_580_MIDI --output
NEW_DIRECTORY` and `tools/compare_diversity_selection.py --output NEW/report.json`.
Reports record source/code/plan hashes. Raw selected MIDI stays outside Git.
