"""Fourteen-work integer-count profile; frozen twelve-work model unchanged.

For <=12 works, construction is exactly the original implementation. Larger
inputs are validated in original-valid chunks, then sufficient counts merge
without adding transitions at work or chunk boundaries. All global event bounds
remain enforced by the original factorized model constructor.
"""
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.onset_gate_model import OnsetGateModel, GATE_SIZE


class FourteenContextModel(ContextOnsetGateModel):
    def __init__(self, sequences, pitch_sequences, *, timing_context=False,
                 pitch_continuity=False, strength=4):
        if type(sequences) is not list or not 1 <= len(sequences) <= 14:
            raise ValueError('one to fourteen works required')
        if type(pitch_sequences) is not list or len(pitch_sequences) != len(sequences):
            raise ValueError('aligned pitch work list required')
        kwargs = dict(timing_context=timing_context, pitch_continuity=pitch_continuity, strength=strength)
        super().__init__(sequences[:12], pitch_sequences[:12], **kwargs)
        if len(sequences) <= 12:
            return
        remainder = ContextOnsetGateModel(sequences[12:], pitch_sequences[12:], **kwargs)
        for previous_gate, counts in remainder.contexts.items():
            self.contexts[previous_gate].update(counts)
        self.pitch_counts.update(remainder.pitch_counts)
        self.intervals.update(remainder.intervals)
        self.base = OnsetGateModel([pair for seq in sequences for pair in seq], factorized=True)
        self.vocabulary = tuple(sorted(self.pitch_counts))
        self._delta_cache = {}
        total = 0
        self._gate_prefix = []
        for gate in range(1, GATE_SIZE + 1):
            total += self.base.gate_counts[gate]
            self._gate_prefix.append(total)
