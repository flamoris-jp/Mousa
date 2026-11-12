# Cycle31: weighting, event-order texture and private audition prototypes

## Why investigate texture, not only corpus size

A post-hoc audit of the twelve-work corpus finds842simultaneous-onset transitions
among3251adjacent-event pitch transitions. These are event-order relationships,
not melodic succession. Their mean absolute interval is6.248219semitones; the
2409later-onset transitions average4.200083. Later-onset ordering still does not
identify musical voices: it may jump from the last note of one chord to the first
note of the next.

All149source transitions exceeding an octave occur in three keyboard staffs:
Handel5, Joplin105andBeethoven39. Of these149,147have later onsets and2share an
onset. The original monophonic teaching sources do not contribute such jumps.
This is a descriptive clue, not proof that polyphony alone caused generated
leaps. Vocabulary size, uniform pitch mixing, source weighting and feasibility
constraints also changed over earlier experiments. No human semantics or quality
labels were inferred from these counts.

## Comparison frozen before actual fitting

Three conditions use the same12sources,36pitch vocabulary, observed640/921
diagnostics, priors, contextk4, seed0–4schedule and joint feasible generator:

- **raw:** each event weight1.
- **equal_work:** each work contributes3263/12note mass.
- **equal_declared_family:** each of9declared groups contributes3263/9note mass;
  within a group each event has the same weight, so longer member works contribute
  more. This is not equal contributor weight because contributor links can cross
  declared edition groups.

All conditions have exact weighted note mass3263. Transition/context mass is
not identical:3251raw,3232.175211equal-work and3235.353328family-balanced, because
sequence boundaries are not invented transitions. Local count mass relative to
context strength4also changes. Timing, initial pitch counts and interval counts
are weighted together; this experiment does not isolate those pathways.

The new sampler retains Fraction counts and scales finite integer draw vectors
exactly, including the gate's uniform prior. It does not duplicate the corpus or
round weights. Integer pitch sampling replaces historical floating-point
`random.choices` for ALL three conditions. Consequently raw likelihoods agree
with the earlier model, but historical seed bytes/metrics are not this experiment's
control. Raw was regenerated alongside both weighted conditions. All3retain the
25%uniform pitch mixture and the same vocabulary, including infrequent pitches.

## Failed prototype found before real fitting

Independent synthetic review found that the first weighted subclass inherited
an unsafe legacy sampler with a stale raw gate prefix. A tiny1/100weight fixture
returned an invalid fractional gate338406/25. The dedicated new sampler was
correct, but the inherited route was not. No real corpus was fitted or scored
using that prototype.

The corrected weighted model is standalone, explicitly reusing only validated
count/likelihood methods. Old sampling methods and external legacy generator
routes reject it. The initial unrun plan, intermediate correction and final
pre-fit plan are retained, with regression tests and the failure explanation.
Independent review enumerated87,016gate draw positions for four tiny caps and
verified exact observed-plus-uniform masses and endpoints. Five model tests
cover parity, conditioning, reproducibility, resources and old-route rejection.

## Results

All15candidates completed with no copy flag or resource rejection. Initial CPU
was1.915seconds against a shared120secondbudget. Since the budget is global and
condition order fixed, an incomplete run would not justify a fair ranking; that
limitation is explicit. No budget exhaustion occurred here.

| Condition | Factorized timing NLL | Context timing NLL | Mean absolute interval | Overlap-onset fraction | Same-pitch repetition |
| --- | ---: | ---: | ---: | ---: | ---: |
| raw | 9.055696 | 7.990111 | 6.660196 | 0.460069 | 0.106560 |
| equal_work | 9.106083 | 7.886584 | 4.210332 | 0.272736 | 0.219808 |
| equal_declared_family | 9.174167 | 7.979924 | 4.627830 | 0.261456 | 0.172442 |

Equal-work weighting improves context timing likelihood but worsens factorized
likelihood. It reduces leaps/overlap and increases repetition. Family weighting
has similar structural tradeoffs with a smaller context likelihood change.
None is established as more attractive. These are only two already observed
predictive diagnostics and five generation seeds per condition. No fresh test
set, user ratings or universal model ranking is claimed.

Exact raw context probabilities match the old model on all190diagnostic events;
raw NLL differences from the historical calculation are at most1.78e-15from
floating-point accumulation. All weighted counts retain3263note mass. Gate-scale
bit lengths are1/62/48and maximum cached delta-weight bits32/152/131, below the
2048bit ceiling. This ceiling is still an explicit resource limit, not permission
for unbounded input. Repeat predictions, metrics and all15private note files
match, except measured CPU time. Independent checks confirm original hashes,
maximum3voices, no active same-pitch duplicates, tail≤384and copy0against all14
training/diagnostic references. Copy0does not establish originality.

## Private A/B/C prototypes

Generation seed0from every condition was selected before fitting; allthree were
eligible, with no substitution or cherry-picking. Opaque order and its method key
remain private. Three MIDI files preserve every generated note, gate, simultaneous
event order and ending silence. The fixed6/8export header gives8bars at120BPM and
9216ticks, not evidence of learned meter or phrase structure.

Each WAV is12seconds/264600monoPCM16frames at22050Hz, using the same analytic
fundamental-plus-second-harmonic renderer and per-note gain. No external recording
or SoundFont is used, no clip is individually loudness-normalized, and clipping
is0. Denser overlaps can still sound louder. Repeat WAV bytes match. These are
analytic previews, not actual Cantabile audio renders.

An isolated Cantabile CLI imports, validates and exports allthree MIDI files.
Decoded headers and ALL message streams match; raw serialization bytes differ,
so native byte identity is explicitly NOTclaimed. The research writer's own
byte roundtrip does match. No live project was opened or changed. Actual UI
playback and human listening remain separate, unperformed checks. The optional
questions and non-training feedback policy are in
`docs/WEIGHTING_LISTENING_DESIGN.md`.

Generated previews are not original teaching data and must not be silently fed
back into training. Public release and perceptual/copyright originality remain
uncleared. Preparation does not itself claim user delivery, listening or storage.
The prior12originals/metadata have separately been saved by the authorized
material-storage workflow; this cycle does not alter its fixed snapshot.

## Verification

Fullsuite279discovered,278passed,1existing actualAudioAnalyzer integration skip.
Dependency-free279discovered,240passed,39expected optional skips. Compileall and
diff checks pass. Three audition WAVs were independently reconstructed sample
for sample, and all decoded native MIDI messages verified. No identifying human
feedback, raw teaching MIDI, generated audio/video or private method key enters
Git. No main merge, deployment, GPU or paid computation.
