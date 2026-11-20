# Cycle21: separate event budget, generation and new source reservations

## Fixed60-event contrast

Quantity and content changed together in cycle20. This follow-up holds total
training events at60, using deterministic original-order prefixes:376=60;
888+889=30+30;789=60; balanced three-family mix=20+10+10+20. The related888/889
works stay together. Every work boundary resets context, and original firstdelta
is retained; no fabricated joins or rewritten source MIDI. Plan precedes scoring.

With unchanged model/support/prior settings, equal-work timing NLL on already
observed580/640 is:

| Composition | Factorized | Previous-gate k4 |
|---|---:|---:|
| 376family | 5.835025 | 5.190185 |
| 888/889family | 8.271614 | 7.728546 |
| 789family | 14.826696 | 14.579674 |
| Balanced3families | 6.128316 | 5.557497 |

The balanced mix is not best even at the same note-event budget. This separates
one obvious count confound, not all content/style effects. Prefix sampling favors
beginnings; work counts1/2/1/4 imply59/58/59/56within-work transitions. There is no
random sampling, causal diversity estimate, fresh held-out evaluation or quality
claim. The independent reviewer reran all conditions and reproduced exact scores.

## Full-source generation contrast

Separately, use all events from each of the three single families versus all
four works, with seeds0..4 fixed before generation. The four conditions have
159/85/120/364events and pitch vocabulary sizes10/13/9/17. Same contextk4,
feasibility, uniformmix1/4 and tail384 constraints; no retrospective singleton
selection. This generation experiment is NOT the60-event contrast above.

All20candidates complete; narrow source-copy flags0, CPU skips0. Equal-output
means across five seeds each:

| Training composition | Notes | Distinct pitches | Same-pitch fraction | Overlap fraction |
|---|---:|---:|---:|---:|
| 376family | 21.6 | 8.0 | .201 | .184 |
| 888/889family | 26.2 | 9.4 | .389 | .140 |
| 789family | 31.2 | 8.4 | .210 | .329 |
| All4works | 29.8 | 12.2 | .259 | .117 |

The full model uses more pitches but repeats adjacent pitches more than two
single-family conditions. Its vocabulary is larger by construction. Do not
attribute everything to quantity or call this less monotonous/more appealing.
All20MIDI safety/roundtrip and repeat bytes pass. The full-data five MIDI outputs
match oldercycle15outputs, not new independent draws. Failures and budgets would
have remained reported; none occurred in this small sample.

## Private audition preparation

Seed0 from all four conditions, without cherry-picking, was rendered as four
opaque12-second clips. Analytic sine plus harmonic tones, same fixed gain, exact
overlap/gates and silence; no external recordings. Peaks remain below0.315,
zero clipping, all four repeated WAV bytes match. Renderer tests verify overlap
is added rather than overwritten and tail silence is preserved. MIDI/audio and
method key stay outside Git. This is not a Cantabile render or public originality
clearance. No delivery or human ratings are claimed here. A separate opt-in
listening protocol preserves ties, neither and missing responses.

## Source rights and splitting

Chopin921/Roland Goretzki is a new reserved composer/contributor candidate.
Composition, historic Scholtz/Peters editorial tradition and typesetter PD
contribution were reviewed separately, with historical incipit corroboration.
Selectedtrack1 has92notes,2/2and an explicit quarter-note pickup. Track2 fails an
unsupported-control check: do not claim full-performance fidelity or repair it
silently. No source similarity admission, training or scoring yet. The original
and rights evidence remain intact, and future score/split planning must precede
predictive calls.

Burgmüller202/214 remain pending. A Litolff2355catalog record dated1905does not
prove it is the contributor's cited edition or replace an edition scan. No
uncertain source was admitted. Telemann1692remains blocked under its fixed gate.

No main merge, publicmedia/corpus release, liveproject edits, GPU or paid work.

## Final checks

Full suite228discovered,227passed,1existing actual AudioAnalyzer integration
skip. Dependency-free228discovered,190passed,38expected optional skips.
Compileall/diff checks pass. The six new tests cover fixed-budget allocation and
prefix preservation, generation comparisons, and overlap-preview behavior.
No actual Windows/Cantabile audition or human preference is claimed.

Independent audio review reproduced every PCM sample with a separate additive
implementation, checked private source/WAV hashes and measured the retained
overlap and endpoint-silence frames. Public audition metadata omits MIDI linkage
and note counts; the complete provenance stays in the private manifest. Opaque
names are a convenience, not a guarantee of listener blinding.
