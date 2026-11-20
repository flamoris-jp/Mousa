# Cycle38: verified listening artifacts and unstable cohort effects

## Four private listening previews

Exactly seed0 from each of the four Cycle37 pitched conditions was fixed for audition. This is a deterministic subset selected after numerical results existed, not a preregistered pre-generation sample or a quality-selected winner. Four opaque-labelled MIDI/WAV pairs are now prepared outside Git, explicitly generated/private/listening-only/not-training.

The new exporter preserves all five note fields, same-tick ordering, PPQ384,tempo120,6/8 and EOT9216. Internal MIDI byte roundtrips and isolated Cantabile CLI import/export passed. Cantabile serialization bytes differ, while checked musical/performance fields do not. An independent direct MIDI-event parser also reconstructed all four source note multisets exactly. No live project was touched or human listening claimed.

Each WAV is12seconds,mono22050Hz16bit PCM using the same own analytic oscillator and gain, with declared velocity/release mapping. There is no SoundFont, external recording, hidden per-file normalization or clipping. Peak remains below0.473. RMS differs by roughly3.1dB across clips; equal gain does not mean equal perceived loudness. Re-rendered files are byte-identical. Independent actual-PCM readback checked file format, durations, no saturation and quantization-tolerant peak/RMS agreement.

A blind-listener packet is prepared separately from technical reports and the correspondence key. It contains four WAV files and a ZIP of the four MIDI files. The root controls actual Library/user delivery; file creation does not mean delivery or playback occurred. The correspondence table is retained separately for later interpretation, not initially disclosed in the listener packet. Real human ratings remain unrecorded by this experiment; the feedback template is entirely blank and training-ineligible. The neutral protocol permits ties, dislikes and inability to judge. It separates measured facts, actual listener comments and researcher hypotheses.

## Portability failure found and corrected

Independent dependency-free testing found that the new MIDI roundtrip test raised ModuleNotFoundError for optional mido. Only that test received an availability skip; analytic tests still run. The historical test/hash, failure and exact diff are retained. A new code-bound portability plan re-rendered the four clips, and all eight MIDI/WAV files matched the already prepared artifacts byte-for-byte. Renderer, source candidates, label mapping, old manifest and old snapshots were unchanged. Additional metadata records the correction rather than rewriting the original run.

Resource checks are parent-process CPU between bounded clips plus a20-second timeout per native CLI operation, not a joint OS CPU quota across processes. This was small local synthesis/verification, with no GPU, paid action, release or deployment.

## Groove: the same person can reverse direction on other recordings

A separate read-only analysis uses only saved12/35-model result JSON for the earlier and later eight-recording cohorts. There is no original-MIDI access, new fit, predictive scoring or new evaluation selection. All16 recordings are now observed and belong to the same four heldout drummers.

Among24 drummer×condition comparisons, the pooled effect of adding training material reverses direction across cohorts in9 cases; recording-macro reversals occur in8. For unigram, drummer10 changes from+0.072126nats/event worse to−0.751619 better, while drummer9 changes from−0.510882 better to+0.092639 worse. Quotient/residual's test pooled change reverses from+0.077252 to−0.014823. These are descriptive overlapping comparisons, not independent hypothesis tests or stable drummer traits.

Earlier validation's four exact-IOI conditions improve event-pooled loss but worsen recording-macro loss. Later recordings improve under both. Long performances dominate pooled means, whereas short fills have equal recording weight in macro means. Content, event support, session/style and duration remain confounded. A support-composition mediation study is a future hypothesis, not implemented evidence or a new model adopted from these results.

## Verification and unchanged corpus roles

Groove result repeats match, and120 independent aggregation checks pass. Final installed-dependency suite:364tests,363pass,one existing integration skip. Dependency-free:364tests,323pass,41expected optional skips. Compileall/diff checks pass.

Pitched training remains17works/4319notes/3428groups. Groove remains35train/16observed-untrained/1099unscored-untrained. New audition MIDI/audio are stored only in separate owner-designated LIME subfolders; they are not additions to either training corpus. Original files, ZIP and historical ledgers remain unchanged. No raw media, label key or generated source-note arrays are committed.

See `2026-11-12-group-audition-preparation.md`, portability records, independent review, `2026-11-12-audition-evaluation-protocol.md`, and `2026-11-12-groove-cycle38-cohort-comparison.md` for full constraints and denominators.
