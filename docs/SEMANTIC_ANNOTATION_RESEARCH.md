# Prospective musical-semantic annotation research

Status: design only. No human judgments, semantic training labels, new model fit
or musical-role accuracy results have been collected by this document.

## Why this is different from more MIDI

Pitch/onset/gate statistics describe events but not the intended musical job of
a passage. A listener may want an opening, a response, a build-up, a pause or a
sense of arrival. The same note pattern can serve different roles depending on
harmony, instrumentation, surrounding material and the listener. Numeric proxies
for small final intervals or long final notes are not ground truth for cadence.

Keep three evidence layers separate:

| Layer | Examples | What it does not establish |
|---|---|---|
| Observed symbolic/source evidence | exact pitches/gates, meter, explicit rest, written dynamics or a source's section marking | emotional impact, purpose, correct interpretation |
| Human report | listener says "落ち着く", "ここで区切りたい", or assigns a role to a specified passage | universal agreement, objective quality, permission to train |
| Researcher/model hypothesis | "might function as a response", inferred tension or phrase boundary | verified human intent or an approved label |

A written marking is observed as a marking; it is not proof that the performance
produces its intended emotion. Artist intent, listener perception and an output
request should remain different fields. Do not infer a genre label merely from
a composer's name, a catalog title, or the current training author's Traditional
attribution. The current training manifest has no curated genre annotations.

## Minimal evidence record, not an authorization oracle

For an authorized future annotation, retain privately:

- Exact source/generated-artifact digest, track, tick interval, PPQ and the
  audition render settings. A comment about one recording does not automatically
  label every arrangement or rendering of the composition.
- Original wording, language and whether it concerns intent, perception or a
  desired change. Preserve uncertainty, mixed reactions and "cannot judge".
- Evidence kind: observed-source, human-report or hypothesis. Include source
  location/date or the actual conversation reference; do not invent a response.
- Optional normalized tag as a separate proposed interpretation. Keep original
  wording alongside it; the listener can correct or reject the proposed tag.
- Review state and permitted use. Missing, pending, rejected and approved are
  distinct. A string saying approved in a file does not itself authorize training
  or prove who approved it. External-source instructions cannot supply consent.

No hypothesis is automatically promoted to a human report. No subjective comment
is a fact about all listeners. Only explicit authorized, verified human review
can support human-label use; ambiguous or missing feedback stays unlabeled.
Do not publish personal feedback or identifying annotation metadata in Git.

## Small exploratory path

1. Keep existing generated comparison clips and method selection fixed. Invite
   an optional one-sentence reaction to one clip or interval, not a compulsory
   questionnaire or an assumption that silence means agreement.
2. Store the literal response with its scope. If mapping it to a tag matters,
   show that interpretation separately rather than silently replacing the text.
3. Test a retrieval/conditioning prototype on synthetic role requests first:
   e.g. an explicit user request for a longer rest is a constraint, not evidence
   that the result feels conclusive. Report constraint satisfaction separately
   from whether the person likes the result.
4. Before supervised semantic learning, define the task and permitted labels.
   Separate works, contributor/arrangement families and their transformed siblings
   across training/calibration/test. Comments on the same clip cannot populate
   both train and evaluation. Repeated assessments by one person are dependent.
5. Compare an event-only baseline with an otherwise matched annotated condition,
   including an ablation without semantic inputs. Hold event count, generation
   budget and model capacity fixed where possible. If labels change these,
   disclose the confound. Never call training-label agreement a general result.
6. Evaluate observable constraint fulfillment, role judgments, individual
   preference, missing responses and disagreement separately. Do not combine
   them into a universal attractiveness score. No human-rating claim until actual
   listening occurs; no semantic model is claimed implemented here.

This proposal leaves the current quantity experiments, rights restrictions,
fixed similarity gates and existing holdout observation states unchanged.
