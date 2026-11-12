"""Prospective bounded32-work integer-count profile; frozen models unchanged.

Chunking validates counts with the original model; it never concatenates works
into a temporal sequence. No new probability formula or inference policy.
"""
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.onset_gate_model import OnsetGateModel, GATE_SIZE, _pairs


class BoundedContextModel(ContextOnsetGateModel):
    def __init__(self,sequences,pitch_sequences,*,timing_context=False,pitch_continuity=False,strength=4):
        if type(sequences) is not list or not 1<=len(sequences)<=32:
            raise ValueError('one to thirty-two works required')
        if type(pitch_sequences) is not list or len(pitch_sequences)!=len(sequences):
            raise ValueError('aligned pitch work list required')
        flat=[]
        for seq,pitches in zip(sequences,pitch_sequences):
            _pairs(seq)
            if not isinstance(pitches,(tuple,list)) or len(pitches)!=len(seq) or any(type(p) is not int or not 0<=p<=127 for p in pitches):
                raise ValueError('aligned MIDI pitches required')
            if len(flat)+len(seq)>100000:raise ValueError('aggregate event bound')
            flat.extend(seq)
        _pairs(flat)
        options=dict(timing_context=timing_context,pitch_continuity=pitch_continuity,strength=strength)
        super().__init__(sequences[:12],pitch_sequences[:12],**options)
        if len(sequences)<=12:return
        for start in range(12,len(sequences),12):
            chunk=ContextOnsetGateModel(sequences[start:start+12],pitch_sequences[start:start+12],**options)
            for gate,counts in chunk.contexts.items():self.contexts[gate].update(counts)
            self.pitch_counts.update(chunk.pitch_counts);self.intervals.update(chunk.intervals)
        self.base=OnsetGateModel(flat,factorized=True)
        self.vocabulary=tuple(sorted(self.pitch_counts));self._delta_cache={}
        total=0;self._gate_prefix=[]
        for gate in range(1,GATE_SIZE+1):
            total+=self.base.gate_counts[gate];self._gate_prefix.append(total)
