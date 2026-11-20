# Groove exact-tick IOI pilot: a negative conditional-model result

This rhythm-only experiment used original Google Groove MIDI Dataset v1.0.0 MIDI-only performances under the reviewed CC BY 4.0 scope. It did not use melody models, generate music, acquire audio, or assess attractiveness. Original MIDI bytes were unchanged. Credits, license/source links and restrictions remain in `datasets/research-groove-rights-cycle32-20261112.json`.

## Fixed selection and split

The predeclared SHA-ordered selection retained 20 complete performances: 12 train recordings from six drummers (5,034 note-on events), four validation recordings from two different drummers (2,758 events), and four test recordings from two further drummers (3,850 events). Sessions stay inside drummer groups. All 40 known shared-pattern evaluation-session recordings were reserved. Eight over-cap performances were ineligible; nothing was truncated. Short six- and fourteen-event fills remain selected, so equal drummer counts do not balance event mass, duration or style.

The preparation verified all 1,150 source hashes and 446,312 positive-velocity note-ons. Selected-versus-cross-split screening covered 12,416 comparisons. No cross-split exact bytes, full onset/key fingerprints or full tempo/offset-normalized fingerprints matched. Sixty-seven pairs shared coarse eight-event windows; maximum whole-set Jaccard was 0.01102, below the predeclared 0.80 review threshold. These common-window matches are not proof of copied works. This bounded screen does not establish independent patterns or compositions. Original release splits are historical metadata only.

## Model and outcome

Targets are original integer-tick inter-onset intervals at PPQ480, support 0..30,720 inclusive. Instrument keys condition one model but are not melodic pitches or prediction targets. The unigram uses uniform total prior mass one. The alternative adds four global-empirical pseudo-counts to each seen previous-instrument context before adding the same prior. This is count shrinkage, not a fixed mixture of two smoothed probabilities. Initial/unseen contexts back off to the control. Work boundaries reset context: 5,034 training events yielded 5,022 within-work context transitions.

| Fixed condition | Validation pooled NLL (nats/event) | Test pooled NLL |
|---|---:|---:|
| Unigram | 5.165146 | 6.353313 |
| Previous-instrument context, k=4 | 5.462280 | 6.898952 |

**The conditional model was worse on all eight evaluated performances**, not just on pooled means. Per-performance, per-drummer and macro means with denominators are retained in the results JSON. Four validation/test recordings per split represent two drummers, not four independent performers. No subset, threshold or k was changed after seeing the outcome.

Both runs completed within one CPU second each (approximately 0.25 seconds initially); exact results matched after excluding CPU time only. All 6,608 evaluation events were supported without dropping or quantization, and all source hashes remained unchanged. CPU timings are local measurements, not a comparative speed benchmark.

## Limits and state

Previous-instrument conditioning is sensitive to the source ordering of simultaneous hits; this is not causal groove learning. IOI prediction omits velocities, controllers, note-off pairing/gates and tempo-to-seconds performance semantics. Those properties were not validated by this task. Predictive likelihood does not establish musical preference or generation quality. The small selected sample and unresolved near-pattern relationships limit generalization.

The eight evaluated recordings are now predictively observed; they must not be presented as fresh test data in subsequent work. The separate usage ledger records 12 train-used, eight predictively observed, and 1,130 not used in this experiment (40 reserved plus 1,090 others). Historical prospective rights/intake snapshots remain unchanged. No raw MIDI, audio or fitted model artifact is included in this report or its metadata snapshot.
