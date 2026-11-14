# Adaptive Mousa research protocol

This is an observation-window research program, not one task per day. Complete
ready work immediately, then choose the next hypothesis from measured failures.
Preparation begins on 2026-11-12. The observation window is 2026-11-13 through
2026-11-26 (Japan time), with a midpoint on November 19 and a final review on
November 26. Dates are reporting checkpoints, not reasons to defer experiments.

## Loop and stop conditions

1. Read the current commits, open PRs and previous results; avoid duplicate work.
2. State a falsifiable hypothesis, competing explanations and a smallest test.
3. Freeze sources, work-family splits, representations, metrics and seeds before
   looking at test outputs. Record any later protocol change as a new experiment.
4. Run bounded CPU experiments, compare with a simple baseline, retain failures.
5. Separate valid MIDI, structural descriptions, human preferences and copying
   risk. A better predictive score does not imply a better melody.
6. Identify the next bottleneck: onset representation, monotony, phrasing,
   harmony, evaluation validity or a different model. Continue without waiting
   for a calendar date or assuming the initial checklist is the final product.

Start with one CPU process, one thread and at most 5 minutes per statistical
experiment; use seeds 7, 17 and 29 and a maximum of 12 initial work families.
These are conservative research choices, not the user's hardware capacity.
Record wall time, peak RSS and CPU configuration. Stop a run at its budget and
preserve partial logs. Do not start GPU training, billable services, deployments,
release publication or merges without prior approval. Keep branches and PRs in
draft. Do not change existing Cantabile projects. After the final report, stop
new research and await the owner's decision; stop active runs safely as needed.

## Dataset and preflight

Use `mousa.research_intake.validate_manifest(manifest, root)` before selecting
training rows. The schema is `mousa.research-intake.v1`; each work has:

- work_id, title, author, source_url, license, terms, acquired_at (timezone-aware),
  sha256, family_id, duplicate_group;
- review_state (`pending`, `approved`, `excluded`), training_allowed and split;
- for approved MIDI: source_kind=`midi`, file (relative to local corpus root),
  and rights records for composition, arrangement and midi_encoding separately;
- each right has training_allowed, basis, evidence_url and reviewed_on.

Unapproved records have training_allowed=false and split=null. They stay
quarantined. Store source bytes and website evidence outside Git; record hashes
and license evidence. Dataset and code licenses are separate. A reviewer assertion
is not cryptographic proof of rights. The validator checks assertions and local
file hashes, not legal status, a complete MIDI parse or approximate duplicates.
A separate parser and duplicate search remain mandatory. Never treat FREE
DOWNLOAD as permission. AudioAnalyzer candidates remain in their existing
human-review pipeline and are not admitted by this MIDI-only preflight.

Group all versions, transpositions and arrangements of a composition before
splitting. Detect identical hashes and normalized melody duplicates, then review
near matches. Group IDs must come from that review, not arbitrary distinct IDs.
No family or reviewed near-duplicate group may cross train/dev/test. Deduplicate
before augmentation. Keep a new sealed test set separate from the three already
inspected Trial 001 sources, which are only a diagnostic reproduction set.

## Initial comparison and evaluation

First compare unigram, first-order Markov and second-order n-gram event baselines.
Use the same source families, priors, seeds and output length. An event-centered
representation is the first hypothesis because grid-v1 mostly predicts HOLD.
Keep the recovered grid-v1 PR pinned and unchanged as a separate reference.
Maidionis owns generic learned numerical components; do not copy its Core here.

Report denominators for next-event pitch, duration, rest and onset metrics
separately; negative log likelihood must state smoothing and vocabulary.
Generation is eight bars in the bounded first profile, not a claim that arbitrary
meters or polyphony are supported. Measure note count, interval distribution,
rest proportion, repeated n-grams, phrase contrast and endings descriptively.
Detect long exact and transposed matches against all training sources. A low
similarity statistic is not a legal originality guarantee.

Human listening uses blinded A/B IDs and equal rendering settings, with A, B,
tie and neither choices plus an optional reason. Ask about coherent phrasing,
variation and intended use independently. Keep responses private and do not
invent labels when no response arrives. Use dev only to select revisions;
open the sealed test only after freezing the comparison. Preserve unsuccessful
seeds, not just pleasant samples. Musical-quality conclusions require listening.

## Records and delivery

Each experiment records hypothesis, parent experiment, exact commits, source
manifest digest, split digest, parameters/seeds, environment, wall time/RSS,
metric denominators, generated MIDI hashes, similarity results, human-review
status, failure/limitation, and the next hypothesis. Store media and weights
outside Git. Public records contain no private preferences or machine topology.

Progress reports describe actual discoveries, improvements and failed attempts,
not calendar checkboxes. Include completed work, measurements, generated MIDI
(or explicitly none), problems, next experiments and PR links. Keep mid/final
observations even when the original tasks finish early. Final contents depend on
what the research discovers; do not promise musical success in advance.

## Implemented research iterations
The dated experiment records are observations, not a schedule. Three cycles ran
on November 12: preparation/event baselines, factorization/timing correction,
and duration-prior/relative-pitch/6/8 transfer ablations. The later records correct
false alarms and preserve tradeoffs. `meter_midi.py` is an explicit narrow
constant-meter profile; never infer general MIDI or learned musical quality from
its successful I/O tests.
