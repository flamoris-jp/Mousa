# Staged, rights-aware expansion beyond five works

## Decision at cycle28

Prioritize **metadata-first collection review**, rather than continuing only
one historical piece at a time. No new corpus is admitted by this document.
Counts below are publisher claims, not verified local inventories. Dataset
licenses do not automatically clear underlying composition, arrangement, edition,
performance or MIDI rights. The evidence ledger is
`datasets/research-scalable-corpora-cycle28-20261112.json`.

| Route | Why investigate | Key boundary |
| --- | --- | --- |
| PDMX | Hundreds of thousands of symbolic scores, license/conflict fields, duplicate metadata | Score count is not usable MIDI count; PD labels and conflict-free status are not per-work clearance |
| IMSLP CC0 compilation | About1,113entries with original source links; small enough for a metadata audit | Compiler cannot dedicate somebody else's work; modern repertoire needs explicit authority |
| Mutopia structured batches | Known contributor/source-edition fields and existing exact-source review experience | Batch discovery saves work but does not waive edition/encoding review or old similarity blocks |
| Groove MIDI | Official CC BY4.0 commissioned drum performances; multiple drummers/styles | Rhythm-only separate task, not pitched-melody corpus; session/drummer grouping and audio rights remain separate |

Lakh's collection license does not resolve per-file transcription and composition
rights. GigaMIDI has additional noncommercial/research/legal-jurisdiction scope
conditions and mixed provenance. MAESTRO's NC/SA terms do not inherently ban AI
research, but compatibility with a potential FLAMORIS product needs a separate
scope decision. None enters the present general corpus. No gated terms were
accepted and no credentials or personal data were submitted.

Generated CC0 collections are not independent human-composed repertoire and
cannot erase upstream provenance problems. Investigate them separately; they
must not become an unlabelled substitute for human music or a human test set.

## Phase A: low-cost discovery, not training

- Fetch metadata only via documented public tables or indexes. Cap the initial
  retrieved table at100rows per route, prefer column projection and avoid raw
  MIDI bytes, embedded audio, huge archives or executable source.
- Keep all attempted rows and failures. Record original IDs, stable URLs,
  composer/contributor/edition, declared licenses, format availability and current
  collection version. Unknown is not false and must not be filled by inference.
- Select a transparent candidate batch across different composer/contributor
  cohorts and declared instruments/eras where available. Metadata diversity is
  not verified genre diversity. Do not count alternate parts, editions or
  transpositions as independent compositions.
- Review10original-source cohorts before considering a pilot. Reuse common legal
  evidence only when the exact scope actually covers every item, not because
  filenames or publishers are similar. Preserve item-specific evidence.

## Phase B: admitted pilot, only after rights and split review

- Freeze exact admitted IDs/hashes, grouping, roles and maximum acquisition size
  before fitting. Pending/rejected items remain separate. Store original bytes
  privately; verify their hashes and support without executing untrusted source.
- Prefer original available MIDI. If only MusicXML/native scores exist, separate
  any future conversion experiment: original preserved, tool/version/options
  recorded, timing/voices/ornament loss measured. Do not claim conversion was
  performed or that all scores have MIDI derivatives.
- Keep a fresh family-level evaluation reserve, old diagnostics and training
  additions distinct. Cross-check sources across collections, not only within
  each archive. Published train/validation/test labels are not accepted until
  family separation is verified. Preserve prior observed/blocked status even when a work appears
  under another ID. Source hash deduplication alone is inadequate.
- Current conservative similarity decisions remain binding for their saved
  experiments. Prospective synthetic characterization informs review but does
  not authorize a threshold change or turn a known candidate into a fresh test.
- A separate percussion pilot needs drum semantics and grouping by performer,
  session and repeated pattern. Feeding MIDI drum key numbers into the melody
  pitch model is not a valid cross-genre comparison.

## Phase C: staged comparison after enough material is admitted

Pre-register actual subset membership and event budgets, not just desired sizes.
Aim initially for multiple independent composition cohorts rather than a large
file count. Report composer/contributor/instrument coverage, known biases and
rejection/attrition. Compare equal-event and natural-event budgets; retain whole
work boundaries and per-work outcomes. More music may reduce single-work bias,
but does not guarantee better melody, and sampling may still overrepresent one
tradition. Missing evidence must not be replaced by marketing claims of breadth.

Use small CPU experiments and existing fixed baselines first. Resource increases,
paid acquisition, public data/model release and deployment are outside current
authorization. Continue recording generation failures and source-copy screens.
Only actual listener feedback can support preference claims; objective metrics
remain separate. A five-work result is not evidence for large-scale learning.
