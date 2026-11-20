# Cycle38 private listening protocol: generated grouped melodies

## Fixed sample and blinding

Use exactly seed0 from each of the four completed Cycle37 conditions. This is a deterministic subset chosen after numerical results existed, not a sample selected before generation and not a representative quality estimate. No candidate was selected by listening or preferred score. Retain all four, including ties, failures and dislikes; do not silently replace an awkward clip.

The listener receives opaque A/B/C/D labels and the same simple analytic timbre, tempo, duration and gain policy. The privately retained mapping and randomization seed are not included in the initial listening packet. This is lightweight method blinding, not a security claim. It does not remove one-listener, order, familiarity or timbre effects.

Preserve every original note field in MIDI. The analytic release-envelope mapping is a declared audition convention, not a claim about a real instrument. Do not normalize each clip independently or imply equal loudness merely because gain is equal. Report measured peak/RMS and note density separately, preferably after initial preferences so those measurements do not suggest a preferred answer.

## Short neutral listener prompt (draft, not yet sent)

「A〜Dを聴いて、もう一度聴きたい順を教えてください。同順位、全部いまひとつ、違いがわからない、でも大丈夫です。気になった箇所や、受けた印象があれば自由に教えてください。」

The files are short synthetic previews, not realistic piano recordings. A comfortable consistent playback volume is useful; changes or replaying clips are allowed and can be noted. Do not force a ranking when the listener cannot judge. Optional timestamps and comments about flow, repetition, pauses or overlapping notes remain self-reported impressions, not automatic semantic truth.

## Evidence and interpretation

- Initially all listening fields are null/unrated. File creation, delivery, play counts, objective metrics or an AI's analysis are not human ratings.
- Record only actual responses, with the conversation/message reference and time privately. Do not invent missing impressions, infer a dislike from no reply, or turn a neutral reaction into a detailed rating.
- Keep observational facts (note timing, measured silence/loudness), the listener's own words/preferences, and researcher hypotheses in separate fields.
- Preserve contradictions and ties. Do not label timing-NLL improvements as musical preference or let one seed decide which model is globally superior.
- One person's response to four clips is exploratory feedback. No confidence interval, population claim or causal feature attribution follows from it.
- Real feedback and label keys remain in private research storage. Do not commit personal quotes or identities to Git without separate authorization. A blank schema is not evidence of a completed study.
- Generated MIDI/audio are listening artifacts, never original training materials. Feedback is not automatically eligible for training or a new ground-truth label. Any later use needs explicit role assignment and leakage review.

## Storage and delivery

Use the owner-designated LIME material folders with separate `private-auditions-cycle38` subfolders under `midi`, `audio` and `metadata`. Manifests explicitly mark generated/private/listening-only/not-training. Preserve prior originals, ZIP and ledgers. The root handles user-facing delivery and any Library attachments; this protocol itself does not mean delivery occurred. Cantabile CLI import/export checks are not live listening or real-instrument rendering.
