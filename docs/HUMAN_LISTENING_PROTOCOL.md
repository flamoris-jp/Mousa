# Private melody listening protocol (exploratory, opt-in)

## Question, not a universal score

Does an explicit A–A′–B–A″ two-bar-block template make the generated eight-bar
melody feel more coherent, or merely more repetitive, compared with direct
sampling from the same fitted model? The template is handcrafted. It is not
learned formal understanding and a preference does not establish originality.

## Fixed preparation

- Three seeds selected before audition: 7,17,29. Retain all complete pairs;
  report blocked generation rather than replacing an inconvenient sample.
- Same six reviewed reference sources; no new or unreviewed training data.
- Same meter6/8, length8 bars, tempoquarter120, register, note velocity, neutral
  analytic sine preview renderer, and playback gain. No external sampled sound
  or commercial recording. The same-seed pairing controls initialization only:
  restructuring is expected to alter notes, not just arrangement.
- Export identical naming/metadata style, using opaque pair/clip IDs. Assign
  A/B presentation order once with a recorded randomization seed. Keep the
  model-key file separate from listener instructions until feedback is recorded.
  The researcher knows the methods; this is not claimed double-blind.
- Keep original MIDI and technical hashes. Check exact duration, MIDI roundtrip,
  peak/clipping and the limited eight-onset source-copy guard before delivery.
  Do not discard a musically weak clip because of a quality proxy.
- Source rights, generated-output resemblance and renderer rights are separate
  checks. Private research audition does not imply public-release clearance.

## Listener instructions (Japanese)

好きなタイミングで、まず1組だけ聴いてください。途中でやめても大丈夫です。
同じくらいの音量でAとBを両方聴けた場合だけ答えてください。

1. まとまり・流れが自然に感じるのは？ A / B / 同じくらい / どちらも不自然
2. 繰り返しは？ AとBそれぞれ「少ない / ちょうどよい / 多い / 判断できない」
3. もう一度聴きたいのは？ A / B / 同じくらい / どちらも聴きたくない
4. 気になった部分があれば、開始からのおよその秒数と理由をひと言。

「片方しか聴けなかった」「音が出ない」「今回は答えない」も有効な回答です。
これらは音楽の評価点に変換しません。正解はありません。

## Record and analyze without inventing labels

Record pair IDs, both-listened status and the person's own response. A missing
answer remains null, not a tie, dislike or zero. Preserve ties, neither and
technical failures separately. Do not infer a rating from a download or emoji
unless the person explicitly states its meaning for that pair.

Keep feedback in private user-authorized storage, not a public Git commit.
Never include personal listening preferences or identifiable raw responses in
public research artifacts. Only share anonymized aggregates if separately
appropriate and authorized. Feedback is not automatically a model-training
label; record its scope and obtain authorization before repurposing it.

For one listener/three pairs, report counts and verbatim feedback privately,
not population confidence or significance. Reveal the method mapping after
recording answers. Human attractiveness, structural descriptors, next-event
prediction, MIDI correctness and reproduction risk remain separate outcomes.
No response is required before unrelated rights or technical research continues.
