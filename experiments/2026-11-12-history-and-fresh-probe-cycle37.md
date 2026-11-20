# Cycle37: probability coverage, sounding history and a prospective recording probe

## Drum-model instability accounted for, not hidden

A fixed-count posthoc audit reproduced all96 old/expanded recording-condition NLL sums exactly. The exact support contains281 old-known intervals,86 newly known intervals and30354 still-unseen integers. For a still-unseen unigram outcome, increasing counts while leaving prior mass1 fixed reduces its probability by5035/19410, adding1.349375 nats per such event. Drummer9 gains from83 newly known intervals but loses on137 remaining unknown intervals. Quotient/residual probabilities redistribute mass differently: having familiar components does not guarantee that a particular exact outcome gains probability.

These are exact probability/accounting observations, not a causal attribution to style, performer skill or musical quality. All six models and per-drummer denominators remain visible. A smoothing-ratio idea is recorded as a hypothesis only, not implemented or selected.

## Sustained-history comparison for pitched groups

Four fixed arms use the same17 training works, observed640/921 diagnostics, first65536/later12288 support, whole-group generator and copying reference set: global, old cardinality, previous maximum gate, and active horizon across all earlier accepted groups. The two duration contexts share predeclared192/384/768/1536-tick bin boundaries and identical k4 backoff. The next interval is never used to construct its own context. Rejected proposals do not update history.

Equal-work group-delta NLL: global4.185509,cardinality4.852378,previous-max-gate3.714385,active-horizon3.747764. Thus duration context improves these already-observed timing diagnostics, while retaining longer sounding history slightly worsens prediction relative to the shorter-history arm. No fresh pitched test or inferred voice/phrase label is claimed.

All20 candidates complete and repeat byte-for-byte, limited copy flags0; old two-arm10 outputs reproduce Cycle36 exactly. Interval-union metrics distinguish actual silence from gaps between note onsets. Mean internal silence is2681.6 ticks for previous-max-gate versus1216 for active horizon; mean maximum contiguous silence2880 versus1267.2. Fewer long silences is a structural change, not proof of preferable phrasing. Full four-arm measurements, rejections and denominators are retained. Whole source/template note fields and original long rests remain intact.

## New recording-level evidence, now observed

Before scoring, a separate plan fixed eight previously unscored recordings from heldout drummers7–10, excluding prior used identities/bytes and all shared evaluation performances. Fixed screening found0strong flags in8872 comparisons, with92weak matches retained. Independent review recomputed selection and gates. Same12/35 training and six models were scored without retuning.

On this new4779-event probe, all pooled and recording-macro means improve with35 recordings. For example, pooled test unigram8.009007→7.444297 and quotient/residual6.352690→6.337867. This does not erase quotient models' negative result on the old recordings. Several models still worsen on the new drummer9 subset; event mass is highly unbalanced across people. These are new recordings from previously observed heldout performers, not new-person generalization, representative genre coverage or musical appeal evidence.

The probe's12 construction/96 prediction journal stages and repeat passed. Its eight recordings are now permanently observed/untrained, never fresh again. Current Groove roles:35train/16observed-untrained/1099unscored-untrained (40reserved+1excluded exact alias+1058other). Pitched roles remain17works/4319notes/3428groups. No new training source or original download was needed this cycle.

## Scope and artifacts

All raw originals and generated notes/media stay outside Git. New LIME snapshots contain metadata only; historical source-use ledgers remain immutable. No main merge, release, deployment, GPU/paid action, invented human feedback or live Cantabile modification.

- `2026-11-12-groove-cycle37-loss-mass-analysis.md` and exact mass/loss results
- `2026-11-12-gate-context-comparison.md`, final plan, corrections, review and verification
- `2026-11-12-groove-fresh-recording-probe.md`, fixed plan/screen, review, results and cumulative journals
- `../datasets/research-groove-fresh-observations-cycle37.json`

Final local verification:359tests discovered,358passed,one existing integration skip. Dependency-free359:319passed,40expected optional skips. Compileall and whitespace checks passed.
