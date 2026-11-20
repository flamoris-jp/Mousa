"""Bounded music-feature count baselines, not a deployed Mousa specialist.

Teacher-forced next pitch-interval and quantized inter-onset prediction on an
explicit highest-onset projection. This is not melody annotation or quality.
"""
from collections import Counter, defaultdict
from math import log, log2
import hashlib
import random


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project_events(events, ppq, limit=2048):
    """Highest pitched non-drum note at each exact onset, across tracks.

Ignores durations, tempo, expression, instrumentation and lower simultaneous
notes. No claim that this voice is the intended melody. Clip intervals at 24
semitones and half-octave log2 beat IOI bins at [-6,+6].
"""
    if ppq <= 0 or limit < 4:
        raise ValueError('positive PPQ and at least four onsets required')
    highest = {}
    for tick, pitch in events:
        if tick < 0 or not 0 <= pitch <= 127:
            raise ValueError('invalid event')
        highest[tick] = max(highest.get(tick, -1), pitch)
    points = sorted(highest.items())[:limit]
    pitch = []; rhythm = []
    for (a, x), (b, y) in zip(points, points[1:]):
        pitch.append(max(-24, min(24, y-x))+24)
        rhythm.append(max(-12, min(12, round(2*log2((b-a)/ppq))))+12)
    return {'pitch_interval':pitch, 'rhythm_ioi':rhythm}, len(highest), points


def read_projection(path, expected_sha, limit=2048):
    import mido
    if sha(path) != expected_sha:
        raise ValueError('source hash mismatch')
    midi = mido.MidiFile(path)
    if midi.type == 2:
        raise ValueError('asynchronous type-2 tracks unsupported')
    events=[]
    for track in midi.tracks:
        tick=0
        for message in track:
            tick += message.time
            if message.type == 'note_on' and message.velocity and message.channel != 9:
                events.append((tick, message.note))
    return project_events(events, midi.ticks_per_beat, limit)


class MusicFeatureCounts:
    """Fixed-support additive unigram plus hierarchical Markov backoff."""
    def __init__(self, sequences, support, order, shuffle_seed=None):
        if order not in (0,1,2) or support < 2:
            raise ValueError('invalid model')
        self.support=support; self.order=order
        self.marginal=Counter(); self.local=[defaultdict(Counter) for _ in range(order)]
        self.cache={}
        for index, sequence in enumerate(sequences):
            seq=list(sequence)
            if any(not isinstance(x,int) or not 0 <= x < support for x in seq):
                raise ValueError('token outside frozen support')
            self.marginal.update(seq)
            if shuffle_seed is not None:
                random.Random(shuffle_seed*1009+index).shuffle(seq)
            for n in range(1,order+1):
                for i in range(n,len(seq)):
                    self.local[n-1][tuple(seq[i-n:i])][seq[i]] += 1
        self.total=sum(self.marginal.values())

    def distribution(self, history):
        key=tuple(history[-self.order:]) if self.order else ()
        if key not in self.cache:
            p=[(self.marginal[i]+1/self.support)/(self.total+1) for i in range(self.support)]
            for n in range(1,min(self.order,len(history))+1):
                counts=self.local[n-1].get(tuple(history[-n:]), {})
                total=sum(counts.values())
                if total:
                    p=[(counts.get(i,0)+4*p[i])/(total+4) for i in range(self.support)]
            self.cache[key]=p
        return self.cache[key]

    def score(self, seq):
        # Same targets i>=2 for all arms; no cross-work transitions.
        loss=0.; correct=0
        for i in range(2,len(seq)):
            p=self.distribution(seq[i-2:i])
            loss-=log(p[seq[i]])
            correct += seq[i] == max(range(self.support),key=lambda j:p[j])
        n=max(0,len(seq)-2)
        return {'n':n,'nll_sum':loss,'nll':loss/n if n else None,
                'correct':correct,'accuracy':correct/n if n else None}
