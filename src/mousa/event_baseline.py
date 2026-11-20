"""Bounded music-event n-gram diagnostic, not a learned quality evaluator."""
from collections import Counter, defaultdict
import math
import random


def events_from_grid(tokens):
    """Convert validated grid-v1 into (REST=-1 or pitch token, duration) events."""
    if not isinstance(tokens, list) or not 1 <= len(tokens) <= 4096:
        raise ValueError('bounded token list required')
    result = []
    for token in tokens:
        if type(token) is not int or not 0 <= token < 27:
            raise ValueError('invalid grid token')
        if token == 1:
            if not result or result[-1][0] == -1:
                raise ValueError('HOLD without active note')
            pitch, duration = result[-1]; result[-1] = (pitch, duration+1)
        elif token == 0 and result and result[-1][0] == -1:
            pitch, duration = result[-1]; result[-1] = (pitch, duration+1)
        else:
            result.append((-1 if token == 0 else token, 1))
    return result


def _events(values):
    if not isinstance(values, (tuple, list)) or not 1 <= len(values) <= 4096:
        raise ValueError('bounded event sequence required')
    if any(not isinstance(e, tuple) or len(e) != 2 or type(e[0]) is not int or
           e[0] not in {-1, *range(2, 27)} or type(e[1]) is not int or
           not 1 <= e[1] <= 4096 for e in values):
        raise ValueError('invalid event')


class EventNGram:
    def __init__(self, sequences, order=1, alpha=0.5):
        if type(order) is not int or not 0 <= order <= 2 or not math.isfinite(alpha) or alpha <= 0:
            raise ValueError('invalid model settings')
        if not isinstance(sequences, list) or not 1 <= len(sequences) <= 12:
            raise ValueError('bounded training work list required')
        self.order, self.alpha = order, alpha
        self.tables = [defaultdict(Counter) for _ in range(order+1)]
        for sequence in sequences:
            _events(sequence)
            for i,event in enumerate(sequence):
                for n in range(min(order,i)+1):
                    self.tables[n][tuple(sequence[i-n:i]) if n else ()][event] += 1
        self.vocabulary = tuple(sorted(self.tables[0][()]))

    def counts(self, history):
        for n in range(min(self.order,len(history)),-1,-1):
            context = tuple(history[-n:]) if n else ()
            if context in self.tables[n]: return self.tables[n][context]
        raise AssertionError('unigram table required')

    def evaluate(self, sequence):
        _events(sequence)
        loss, correct, unseen = 0., 0, 0
        for i,event in enumerate(sequence):
            counts = self.counts(sequence[:i]); total = sum(counts.values())
            # Train vocabulary plus ONE explicit unknown category. Test vocabulary
            # never changes the trained distribution; unseen count is reported.
            probability = (counts[event]+self.alpha)/(total+self.alpha*(len(self.vocabulary)+1))
            loss -= math.log(probability)
            prediction = min(self.vocabulary,key=lambda x:(-counts[x],x))
            correct += prediction == event; unseen += event not in self.vocabulary
        return dict(events=len(sequence),correct_events=correct,unseen_events=unseen,
                    nll_per_event=loss/len(sequence))

    def generate(self, seed, steps=128):
        if type(seed) is not int or type(steps) is not int or not 1 <= steps <= 4096:
            raise ValueError('invalid generation settings')
        rng=random.Random(seed); events=[]; tokens=[]
        while len(tokens)<steps:
            counts=self.counts(events)
            # Generation excludes the unknown category because it has no decoder.
            event=rng.choices(self.vocabulary,weights=[counts[e]+self.alpha for e in self.vocabulary])[0]
            pitch,duration=event; duration=min(duration,steps-len(tokens))
            tokens.extend([0]*duration if pitch == -1 else [pitch]+[1]*(duration-1))
            events.append((pitch,duration))
        return tokens


def longest_shared_run(left,right):
    """Exact grid substring length only, NOT a transposition/near-copy verdict."""
    if len(left)>4096 or len(right)>4096: raise ValueError('bounded sequences required')
    row=[0]*(len(right)+1); best=0
    for value in left:
        nxt=[0]
        for j,other in enumerate(right):
            n=row[j]+1 if value == other else 0; nxt.append(n); best=max(best,n)
        row=nxt
    return best
