# Mousa experiment evidence

## Trial 001 recovery

The actual `Maidionis_Music_Trial_001.zip` was recovered and verified on 2026-11-11. All 429 inventoried members match. [trial001-recovery.json](trial001-recovery.json) records the archive hash, exact source hashes and historical results. Music-only code was migrated into [Melody/grid_v1](../specializations/melody/grid_v1/README.md) with an external pinned Maidionis dependency.

Three publisher Public Domain declarations were rechecked for the exact works in [the source catalog](../datasets/trial001-sources.json). Raw MIDI, the original archive, old weights and old previews are not included in Git. Current preparation writes clearly labeled review records rather than impersonating archived HTML evidence.

## Fresh native acceptance: passed

[GitHub Actions run 43006693911](https://github.com/flamoris-jp/Mousa/actions/runs/43006693911) completed successfully on 2026-11-11 for source commit `c92766bb44b23b66a2de5ef72336a90c24881c9e` (PR test merge `6487522bb357b3900459ae96f0c7e5b198949401`). Its downloaded artifact SHA-256 was verified. [The acceptance record](trial001-ci-43006693911.json) retains exact identifiers and results, separate from the recovered historical evidence.

Observed in that fresh run:

- 9 MusicIR tests and 22 music tests passed.
- Native C++ built against the external pinned Maidionis and LibTorch 2.5.1 CPU profile.
- Real 30-epoch training updated the 16,667 model parameters.
- Checkpoint export, fresh-process reload and two 8-bar MIDI candidates completed.
- All 9 native verification checks passed, including repeated-seed generation, wrong export-pin and modified-weight rejection, and exact state/best/final-weight equality between 30 continuous epochs and fresh-process 2+28 resume.

The current ChatGPT container separately ran 10 MIDI frontend tests and checked source intake; it did not execute the pinned native stack. Native acceptance above belongs to the recorded GitHub runner, not a local GPU or deployed service.

## Numerical result and limitations

| Test diagnostic | Model | Previous-token/position baseline |
| --- | --- | --- |
| Correct tokens | 184 / 248 | 193 / 248 |
| Correct new-note onset tokens | 1 / 45 | 2 / 45 |
| Cross-entropy (nats) | 1.1936701507 | 1.4429554736 |

These fresh measurements reproduce the historical weakness. Most labels are HOLD. The model improves cross-entropy over this baseline but not argmax token accuracy; neither establishes attractive music. Generated candidates contain 19 and 31 notes over 8 bars at 120 BPM, including the supplied four-note primer. Sine WAV previews are not Cantabile rendering or verified AI listening.

The three public works are now familiar development diagnostics. This is not fresh sealed generalization evidence. Future experiments need broader reviewed work families, event/phrase representation and independent human comparisons.

## Evidence storage

The workflow artifact contains reports, sampling records and previews, not raw corpus or weights. Actual repository retention is **3 days**, overriding the requested 14 days; preserve needed evidence separately rather than relying on that ephemeral ZIP. The committed acceptance record and source hashes remain after artifact expiry.

Native reports bind dataset, code-build, environment and export hashes. No Critic, preference learning, Runtime-serving qualification, GPU acceptance or Cantabile editing is established by this trial.
