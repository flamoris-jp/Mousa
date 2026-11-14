"""Research adapter separating timing-work and pitch-work count inputs.

Both paths are validated through the unchanged ContextOnsetGateModel. Each path
resets context at work boundaries; no fractional weights or new probability
support. This intervention does not isolate quantity from source content.
"""
from mousa.context_onset_gate import ContextOnsetGateModel


class SeparatedCountContext(ContextOnsetGateModel):
    def __init__(self, timing_sequences, timing_pitches, pitch_sequences, pitch_pitches):
        super().__init__(timing_sequences, timing_pitches, timing_context=True,
                         pitch_continuity=True, strength=4)
        pitch_model = ContextOnsetGateModel(pitch_sequences, pitch_pitches,
                                           timing_context=True, pitch_continuity=True, strength=4)
        self.pitch_counts = pitch_model.pitch_counts.copy()
        self.intervals = pitch_model.intervals.copy()
        self.vocabulary = pitch_model.vocabulary
