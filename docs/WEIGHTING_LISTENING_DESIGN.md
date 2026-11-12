# Private weighting comparison

Three opaque clips use generation seed0 from raw-count, equal-work and
nine-declared-family-balanced conditions. All three use the same12sources,
3263weighted note mass, vocabulary, priors and new exact integer sampler.
Historical raw12audio is not a control because its pitch RNG algorithm differs.
Sample choice and private ordering were fixed before fitting. If any seed0
sample fails generation or copying checks, do not replace it with a nicer seed.

Each12-second preview preserves overlapping notes, gates and tail silence.
The fixed6/8header gives8bars at120BPM, but the model did not learn meter or form.
Rendering uses the same analytic tone and per-note gain, not sampled recordings
or an external SoundFont. Denser overlaps can sound louder; no per-clip loudness
normalization hides that difference. This is not a real Cantabile rendering.
MIDI is also prepared for later compatible playback without changing a live
project. File validation and actual application audition are separate outcomes.

The method key stays private until after optional feedback; the researcher knows
it, so this is not double-blind. Only one example per condition is heard. A
listener's preference is useful feedback, not evidence that one training policy
is universally better. Copyright/perceptual originality is not cleared by the
finite source-copy screen; public release remains a separate decision.

Optional, non-leading questions:

- もう一度聴きたいのはどれ？ 同じくらい／どれも好みでない／判断できない、でも大丈夫。
- 音の動きは単調・ちょうどよい・落ち着かない、のどれに近い？
- 音の重なりや跳び方で気になったところはある？

Preserve actual comments verbatim and privately with the relevant clip identity.
Listening failure, incomplete listening, missing answers and ties remain distinct.
No comment is fabricated; silence or an emoji is not a rating. Do not promote
feedback to training labels without authorization. Preparation, delivery and
actual listening are separate and must be reported separately.
