# Cycle23: fictional semantic evidence and explicit five-work augmentation

## Semantic data/evaluation prototype

`mousa.semantic_evidence` validates bounded **fictional** evidence records and
reports separate descriptive counts. Source/artifact digests, tick interval,
PPQ/render reference, literal wording, optional proposed tag, evidence layer,
provenance, review state and permitted-use string are distinct fields.

Only synthetic sources and explicitly fictional actors are accepted. Observed
symbolic descriptions, fictional listener reports and hypotheses have distinct
perspective/actor constraints. Changing only a hypothesis kind to human-report
fails validation. Original wording is not replaced by a normalized tag.
`training_eligible` always returns false, including when review says approved.
Neither a file's approval string nor schema validity proves identity, truth,
consent or authorized training use. This prototype does not ingest real comments.

Five constructed examples produce3validrecords and2rejections. Actual human
reports=0 and eligible training labels=0. Additional tests exercise duplicate
IDs, bounds/types, prohibited real provenance, missing audition scope, unknown
fields and review states. These counts evaluate schema behavior, not semantic
accuracy, musical meaning or human preference. The fictional phrases are clearly
marked inventions; none is attributed to the owner. No semantic model was fitted.

## Authorized data increase, with a changed split explicitly recorded

Cornelius583 was previously reserved, rights-reviewed and technically inspected,
not predictively scored. Its exact80-note selected vocal track is now explicitly
assigned to exploratory augmentation. Original sources and immutable rights/
prior split snapshots remain unchanged. The new assignment records5works,
4conservativefamilies and444events versus old4works/3families/364events.

583and580share DanielJohnson/UniversitySociety provenance. Therefore580is
excluded from this comparison's evaluation, and its observation record now
warns against treating it as independent for583-trained models. Only already
observedAdam640andChopin921are diagnostic targets, never fitted or called fresh.
A fixed exact8interval/global.80screen against allfive training sources passes
before either model fits. This is not a new independent test or genre benchmark.

Frozen factorized and contextk4models keep support/priors unchanged. Results:

| Training | Factorized equal-work NLL | Context equal-work NLL |
|---|---:|---:|
| Old4works,364events | 8.506000 | 7.637873 |
| Augmented5works,444events | 8.769905 | 7.859410 |

Both diagnostic works worsen in both models. The added composition is a
legitimate single-pitch work, not thereby bad data or bad music. Its distribution
is different; more examples do not automatically improve every target task.
Quantity, content and a new source family change together. This small comparison
does not isolate a causal quantity effect or establish large-scale behavior.
The old4condition reproduces historical640/921scores.

## Generated behavior under identical controls

Contextmodel only, seeds0..4, same1/4uniformpitchmixture, feasibility, tail384,
target9216and256-note bound. Bothconditions use the same copying references:
all5trainingworks plus2observeddiagnostics, with generated/canonical-order checks.
All10outputs complete with zero narrowcopyflags. Private symbolic note arrays,
not MIDI/audio, are retained for safety/reproduction checks.

Equal-output means old4→augmented5:

- Notes29.8→23.2; distinctpitches12.2→10.0.
- Same-pitch fraction0.258867→0.309123.
- Rest fraction0.208333→0.333333.
- Above-octave fraction0.033808→0.012500.

Fewer large leaps coexist with more repetition and silence. These are measured
tradeoffs, not an attractiveness verdict or a reason to invent semantic labels.
A later role-conditioned model might handle differing musical purposes, but no
such improvement is claimed here. No new audition or human feedback collected.

## New independent source reservation

Clementi804/BrianD.Rude advanced from pending to rights-reviewed reservation
following Rochester/Sibley Schirmer1893album inspection. Composition, historical
edition and PDtypesetter contribution are recorded separately; incipit and
editorial details corroborated, not complete note-by-note collation. Track1,
firstmovement has227notes,2/2and no pickup. No similarity admission, modelfit or
predictive score yet. Allmovements/hands/alternateeditions stay onefamily; shared
Schirmer publisher ancestry is disclosed. Priorpending evidence stays historical.
Burgmüller pending, Telemann blocked and Chopin observed states are preserved.

No main merge, publicmedia/corpus release, liveproject changes, GPU or fees.

## Verification

Independent augmentation rerun matches every non-timestamp report field and all
10private note-array hashes. Checks cover<=256notes, maximum3active pitches, no
active same-pitch retrigger and final sounding endpoint<=9216with tail<=384.
No MIDI file was emitted, so this is a generation-horizon check, not an actual
MIDI EOT/roundtrip claim. Six new tests (five semantic, one split-assignment)
pass. Fullsuite236discovered,235passed,1existing AudioAnalyzer integration skip;
dependency-free236discovered,198passed,38expected optional skips. Compileall and
diff checks pass. All prior frozen models/splits remain unchanged.
