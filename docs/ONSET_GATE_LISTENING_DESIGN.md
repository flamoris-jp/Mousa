# Proposed private onset/gate listening comparison

This is a design, not a completed listening experiment or permission to release
media. Keep timing prediction, overlap safety, melody descriptors and actual
human preference separate. No response has been inferred from prior downloads,
emoji or missing feedback.

## Question

Does conditioning the next onset on the previous sounding duration, together
with learned pitch-interval continuity, make a short generated line feel more
natural? Or does it remove useful expressive overlap and make pitch movement
predictable? Counting fewer overlaps or leaps cannot answer this alone.

## Prospective preparation, after technical verification

Use the unchanged factorial experiment's baseline (neither context) and combined
condition (both contexts), with seed IDs0,1,2 fixed for a small exploratory
comparison. Do not replace a blocked or copy-flagged pair with a nicer seed.
Log missing pairs explicitly; technical failure is not a dislike score. This
selection is for an audition design and must not be called a new sealed model
benchmark or retroactively used to select parameters.

Use identical8-bar6/8 duration, tempo, register constraints, velocity and neutral
analytic renderer without external sound recordings. Preserve overlapping notes
in the render; the earlier monophonic grid preview function is not suitable if
it discards overlaps. Exact MIDI events, output endpoints, peak/clipping and
source similarity must be checked before any private delivery. Do not touch a
user's live Cantabile project. Store generated audio outside Git.

Randomize A/B order with recorded seed20261113 and opaque names; keep the method
key separate. Methods are known to the researcher, so do not claim double-blind.
The two methods can produce different content under the same random seed; this
is a comparison of full generation systems, not an isolated edit of one tune.

## Listener questions, optional

まず1組だけ、同じくらいの音量で聴いてください。途中でやめても大丈夫です。

1. 音のつながりが自然なのは？ A / B / 同じくらい / どちらも不自然
2. 音の重なりは？ 各曲で「心地よい / 気にならない / 濁って聞こえる / 判断できない」
3. 音の動きは？ 各曲で「単調 / ちょうどよい / 飛びすぎる / 判断できない」
4. もう一度聴きたいのは？ A / B / 同じくらい / どちらも聴きたくない

Only record choices if both clips were heard. Keep technical playback issues,
missing answers, ties and neither distinct. Preserve the listener's wording
privately, not in public Git. Do not turn personal answers into training labels
without authorization for that use. One listener and a few exploratory pairs do
not establish population preference or legal originality.
