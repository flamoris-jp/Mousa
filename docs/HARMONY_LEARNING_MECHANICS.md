# Chord-conditioned degree learning: mechanics only

## Why this is not yet a real-music learning result

Merged #21 supplies explicit degree-relative chord timelines and fixed-rule
variations. The reviewed real-music inputs used by #20 contain pitches, durations,
velocities and weak phrase labels, **but no trusted chord timelines**. Assigning
chords from those same melody notes and calling them independent ground truth
would produce a circular experiment. Genuine repertoire-based chord/melody/rhythm
learning is blocked on a separately reviewed annotation source and family-level
split. No new reserve or unreviewed material was used to conceal that gap.

This bounded test instead teaches a fresh native Maidionis model a deliberately
simple, original arpeggio rule. It only asks whether explicit chord root, seventh
flag, beat phase and inter-onset interval can reach a degree generator, change
its learned distributions, survive checkpoint reload, and render valid MIDI.
It is **rule distillation**, not musical-taste learning, generalized harmony,
or proof that an AI learned where to alter a progression.

## One synthetic family, train-only

All four independently encoded #21 progressions, amounts0/.5/1 with seed17,
and half/one-beat rhythm variants share the same existing fixture family
`mousa:major-chord-rule-fixtures:v1`. Transpositions and variants are never counted
as held-out independent works. No external MIDI, score or chord database is read.
The teacher cycles through diatonic chord degrees; it is explicitly visible in
`experiments/maidionis-harmony-mechanics/prepare.py`, not attributed to composers.

The new immutable task `mousa.harmony-degree-mechanics.experimental.v1` keeps
ordinal output192 and cardinality7, with eight preceding degree labels plus
current root, triad/seventh flag, phase and rhythm-gap class. Its14-token/vocab278
configuration is distinct from #19/#20. Fresh initialization, seed314,60fixed
CPU steps,batch32; no old model or optimizer is relabeled or overwritten.
External Maidionis Core stays unchanged and pinned. Root/quality choice and
rhythm are supplied conditions, **not learned outputs** in this trial.

## Fixed-rule versus model preview

An eight-bar I–V–vi–IV example and its amount.5/seed17 fixed-rule variation
are each rendered with (a) the deterministic arpeggio teacher, and (b) model
sampling at seed101. Rhythm, chord timeline, tempo100BPM, keyC, instrument,
64note count and length19.2s remain matched within each pair. Chords useC3,
melodyC4; simple block accompaniment is not voice-leading or arrangement work.

There is no held-out or human preference result. Training loss, parameter
updates, reload equality, independent MIDI parsing and root-counterfactual
probability changes are separate mechanical observations. Chord-tone percentage
is teacher adherence, not an aesthetic score. Counterfactual root changes may be
outside a particular training context and do not establish musical correctness.
The fixture pattern itself is familiar elementary theory; no originality or
public-release clearance is asserted.

## Follow-on blocker

Before claiming progress on the user's larger goal, acquire or create trusted,
rights-reviewed chord annotations aligned to the melody/rhythm corpus, preserve
family splits and annotation uncertainty, then compare chord-conditioned learning
against fixed rules under a frozen evaluation protocol. Human listening must
remain separate. Learning **whether/where/how much** to vary chords is still
unimplemented; #21's variation budget remains a deterministic rule.

No Files connector, live Cantabile edits, merge, deployment or GPU is involved.
The open #20 experiment stays untouched; this additive trial starts from merged
#21 main. Original mechanism results do not depend on merging #20.

## Executed mechanics result

1152 original synthetic rows, 60 steps in12.49CPU seconds. Training-only NLL
3.43276→0.07952; embedding changed and reload probe matched exactly. Two model
melodies have chord-tone adherence95.31%/100% versus teacher100%/100%. Changing
only root in the same query changes probability vectors (mean L1 1.65/1.54).
These establish response to the conditioning interface, not good harmony.

Four MIDI examples contain64melody notes each and end exactly at15360ticks.
Replay is exact. Cantabile import/export preserves every parsed MIDI message,
but not the byte encoding (initial stricter byte assertion failed and was
retained). Four21.2second piano previews have zero clipped samples, same gain.
86Python tests:85pass,one existing skip;17native validation cases pass.
Real chord annotation and independent evaluation remain blocked, not solved.
