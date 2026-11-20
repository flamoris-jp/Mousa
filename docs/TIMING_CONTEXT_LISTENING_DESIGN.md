# Timing-context audition: prospective design, not listening results

This follows cycle 18's matched generation comparison. Timing likelihood,
structural descriptors, technical validity, copying risk and personal preference
are separate outcomes. The Adam work is already observed and remains evaluation
only; no listener answer or source work is added to training here.

## Small first comparison

After generation and source-copy checks, use seed IDs 0, 1 and 2 from both timing
conditions, with the same pitch treatment and output constraints specified in
cycle 18. Do not select a seed by its musical descriptors. A blocked, copy-flagged
or technically invalid candidate leaves its pair missing, with the reason
recorded; do not silently replace it. This is a comparison of full stochastic
outputs, not the same melody with timing edited. The random seed does not align
individual random choices after different models take different paths.

Before delivery, use identical tempo, program, velocity and renderer settings.
The renderer must preserve concurrent notes, exact gates and trailing rests.
The older monophonic grid preview is unsuitable. Check MIDI roundtrip, endpoint,
source similarity, waveform peak and clipping. Keep both methods at the same
fixed gain with adequate headroom rather than individually peak-normalizing
away density differences. Record any duration or loudness difference instead of
hiding it. Store MIDI/audio outside Git and do not modify a live Cantabile project.

Randomize A/B order with recorded seed 20261118. Keep the key private until answers
are recorded. The researcher knows the methods: this is not double-blind. Start
with one pair if the listener wants, not an obligation to hear all three.

## Optional Japanese questions

同じくらいの音量で、まず1組だけ聴いてください。途中でやめても大丈夫です。

1. 音のつながりが自然なのは？ A / B / 同じくらい / どちらも不自然
2. 反復と変化のバランスは？ 各曲で「単調 / ちょうどよい / 落ち着かない / 判断できない」
3. 曲の終わり方は？ 各曲で「終わった感じがする / 急に切れた感じ / 判断できない」
4. もう一度聴きたいのは？ A / B / 同じくらい / どちらも聴きたくない

Record whether both clips were heard. Keep missing responses, ties, neither and
playback faults separate. Preserve the listener's own comments privately; do not
publish identifying feedback. No reply, file access, or emoji is a rating.
A few paired choices by one person inform the next exploratory hypothesis, not
population preference, proof of musical attractiveness, or copyright clearance.
Do not change model parameters while reporting these same pairs as a fresh test.

## Current status

Protocol only. No new audio rendering, delivery, or human rating is claimed by
this document. Private delivery is handled separately after artifact verification.
