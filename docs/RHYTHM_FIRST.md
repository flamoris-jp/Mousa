# Rhythm-first comparison / リズム先行方式

Follow-up to [joint degree/rhythm learning](RHYTHM_LEARNING.md). This is a
small, matched-compute experiment, not a claim that one factorization always
sounds better.

## What changed

The rhythm-first arm first generates the complete eight-bar onset interval,
duration/rest, accent and auxiliary phrase plan. Only then does it fill pitches.
The independent baseline remains event-by-event:

- **independent**: degree query sees only the eight previous joint events.
- **rhythm_first**: degree query additionally sees the current generated interval,
  duration and rest. The selected degree then joins those values in history.

The earlier model could not observe current timing when selecting current pitch.
Merely changing call order would not have implemented that dependency. Therefore
both arms are fitted afresh with the same 54-token architecture, initialization,
50 transferred PR17 backbone tensors, 60-step batch schedule and optimizer.
Rhythm-first timing tasks neutralize preceding pitch labels to tonic placeholders
in both training and inference: ungenerated pitches cannot leak into the plan.
This removal of pitch-history is an additional intended architecture difference. The
baseline has three padded suffix tokens; rhythm-first has real suffix values only
in degree queries. A new task identity prevents old checkpoint reinterpretation.
Training uses true current timing as input to the degree target, a conventional
conditional factorization, not the target degree itself.

The complete rhythm plan is sampled before any actual degree choices. In the
second pass, each degree query sees current planned timing and the prior eight
joint events, not the entire future plan. Timing in this arm does not depend on
actual selected pitches. Duration/rest use legal products of model probabilities;
exact length and consistency remain deterministic rules. An earlier eventwise
protocol was superseded before any training and is retained as unrun history.

## Frozen comparison

See `experiments/maidionis-rhythm-first/protocol.json`. Reuse the exact previously
reviewed dataset: eight train families, four historical-observed evaluation
families; no new source, family-role reassignment or reserve read. One training
seed and three generation seeds, each eight bars / 19.2 seconds / C major / 100BPM.
Unlike the earlier fixed-quarter-note comparison, both new arms have the same
piece duration, though their sampled note counts and melodies may differ.

Timing and degree use separate deterministic RNG streams, identically seeded
across arms. Once outputs differ, their subsequent histories and distributions
differ: same seeds do not imply perfectly matched causal draws. The changed
conditioning can also affect the shared backbone and timing predictions during
training. This is an end-to-end architectural comparison, not an isolated pitch
reranking effect.

## Evaluation caveats

Degree NLL on evaluation rows is **oracle-timing-conditioned** for rhythm-first:
true current rhythms are available, whereas generation uses sampled rhythms.
Report it as a conditional prediction diagnostic, not an unbiased verdict on
free-running composition. The cohorts are already observed, and the experiment
uses only one training initialization; no tuning or best-seed selection follows.

Keep mechanical validity, rhythm diversity, repetition, interval descriptions
and human judgments separate. Inherited rest and phrase labels are extremely
sparse; high accuracy at those tasks can equal a trivial majority predictor.
Phrase remains an auxiliary proposal, not an independently verified musical
phrase. Human naturalness/preferences remain unanswered until someone listens.
Triplet-grid support is not established swing/shuffle style control.

All outputs retain the unchanged bounded 128-family copy screen without retries.
A pass is not comprehensive originality clearance. Private audition is rendered
through isolated Cantabile with the same installed piano bank and uniform gain.
No live project editing, Files connector use, merge, deployment or public media
commit is part of this experiment.

## Executed outcome

Both initial-parameter inventory and sampled training-index schedule hashes match.
60 steps each took 44.61 and 43.94 CPU seconds. Final observed IOI NLL changes
1.5891 → 1.5598 and duration 1.6117 → 1.5490 (independent → rhythm-first),
but degree NLL **worsens** 2.9573 → 3.0157 and accuracy 12.02% → 11.16%.
This remains negative even though the conditional evaluation supplies true current
timing. Rest and phrase accuracy merely equal majority baselines.

All six samples passed bounded copy checks and exact eight-bar MIDI validation.
Independent note counts are 51/60/58, rhythm-first 50/57/58. Rhythm-first has
more adjacent rhythmic repeats in all three seeds (51–61% vs 44–51%); that can
be perceived as coherence or monotony and is not rated here. No selected winner.
Same-seed generation traces and MIDI repeat exactly. Isolated Cantabile
roundtrips are byte-identical; six 21.2-second piano previews have no clipping.
87 Python tests: 86 pass, one existing skip; native14 rejection+3 valid
preflight cases pass. The earlier eventwise proposal was never trained.
