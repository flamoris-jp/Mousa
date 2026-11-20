"""Exact-tick drum IOI prediction only; not melody, performance editing or generation.

For a seen previous-instrument context, first augment its empirical counts by
k=4 times the unsmoothed global empirical IOI distribution, then add total
uniform prior mass one. This is count shrinkage, not a fixed mixture of the two
already-smoothed predictive probabilities. Unseen/initial contexts use the
same prior-smoothed global distribution as the unigram control.
"""
from collections import Counter, defaultdict
from fractions import Fraction
import math

MAX_IOI = 30720
SUPPORT_SIZE = MAX_IOI + 1
MAX_WORKS = 20
MAX_EVENTS = 30000
MAX_WORK_EVENTS = 4096


def validate_work(work):
    if type(work) not in (tuple, list) or not 1 <= len(work) <= MAX_WORK_EVENTS:
        raise ValueError('nonempty complete performance length bound')
    for pair in work:
        if type(pair) not in (tuple, list) or len(pair) != 2:
            raise ValueError('expected IOI/instrument pair')
        dt, key = pair
        if type(dt) is not int or not 0 <= dt <= MAX_IOI:
            raise ValueError('IOI outside exact tick support; no quantization')
        if type(key) is not int or not 0 <= key <= 127:
            raise ValueError('instrument outside MIDI key support')


class DrumIOIModel:
    def __init__(self, works, *, context=False):
        if type(context) is not bool:
            raise ValueError('context must be boolean')
        if type(works) not in (tuple, list) or not 1 <= len(works) <= MAX_WORKS:
            raise ValueError('work count bound')
        if any(type(w) not in (tuple,list) for w in works) or sum(len(w) for w in works) > MAX_EVENTS:
            raise ValueError('total event bound')
        for work in works:
            validate_work(work)
        self.context = context
        self.counts = Counter(dt for work in works for dt, _ in work)
        self.n = sum(self.counts.values())
        self.contexts = defaultdict(Counter)
        for work in works:
            previous = None
            for dt, key in work:
                if previous is not None:
                    self.contexts[previous][dt] += 1
                previous = key
        self.context_totals = {key: sum(c.values()) for key, c in self.contexts.items()}
        self.work_count = len(works)

    def probability(self, dt, *, previous_instrument=None):
        if type(dt) is not int or not 0 <= dt <= MAX_IOI:
            raise ValueError('IOI outside fixed support')
        if previous_instrument is not None and (type(previous_instrument) is not int or not 0 <= previous_instrument <= 127):
            raise ValueError('invalid previous instrument')
        prior = Fraction(1, SUPPORT_SIZE)
        if not self.context or previous_instrument not in self.contexts:
            return (self.counts[dt] + prior) / (self.n + 1)
        local = self.contexts[previous_instrument]
        return (local[dt] + 4 * Fraction(self.counts[dt], self.n) + prior) / (self.context_totals[previous_instrument] + 5)

    def evaluate(self, work):
        validate_work(work)
        previous = None
        losses = []
        unseen = initial = 0
        for dt, key in work:
            initial += previous is None
            unseen += previous is not None and previous not in self.contexts
            losses.append(-math.log(float(self.probability(dt, previous_instrument=previous))))
            previous = key
        return {'events': len(work), 'sum_nll_nats': math.fsum(losses),
                'mean_nll_nats': math.fsum(losses)/len(work),
                'initial_context_events': initial, 'unseen_previous_instrument_events': unseen}
