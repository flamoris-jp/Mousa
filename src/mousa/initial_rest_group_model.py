"""Separate finite initial-rest support; synthetic research profile.

Only the first-onset distribution expands. Later IOIs and gates retain the
frozen 12288-tick bounds. No source notes, silence or EOT are rewritten.
Default first_limit preserves the old model; expanded prior changes first
probabilities even for previously supported values. Generation conditions on
remaining target duration and does not represent the unconditioned first law.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from math import log
from mousa.group_onset_model import (
    GroupOnsetModel, LIMIT, _validate as old_validate, observations, generate,
)

MAX_INITIAL = 1 << 24


def validate(seq, first_limit):
    if type(first_limit) is not int or not LIMIT <= first_limit <= MAX_INITIAL:
        raise ValueError('initial support must be integer12288..16777216')
    if type(seq) is not list or not 1 <= len(seq) <= 4096:
        raise ValueError('bounded nonempty group sequence required')
    first = seq[0]
    if type(first) is not tuple or len(first) != 3:
        raise ValueError('delta/anchor/template required')
    if type(first[0]) is not int or not 0 <= first[0] <= first_limit:
        raise ValueError('initial delta outside declared support')
    # Validation-only surrogate checks all original template/note fields and
    # later deltas. Never passed to fitting, evaluation, generation or storage.
    old_validate([(0, first[1], first[2])] + seq[1:])


class InitialRestGroupModel(GroupOnsetModel):
    def __init__(self, sequences, *, context=False, first_limit=LIMIT):
        if type(sequences) is not list or not 1 <= len(sequences) <= 32 or type(context) is not bool:
            raise ValueError('bounded works and boolean arm required')
        if type(first_limit) is not int or not LIMIT <= first_limit <= MAX_INITIAL:
            raise ValueError('initial support must be integer12288..16777216')
        if any(type(s) is not list for s in sequences):
            raise ValueError('group work lists required')
        if sum(len(s) for s in sequences) > 100000:
            raise ValueError('aggregate group bound')
        for seq in sequences:
            validate(seq, first_limit)
        if sum(len(t) for seq in sequences for _, _, t in seq) > 100000:
            raise ValueError('aggregate note bound')
        self.first_limit = first_limit
        self.first = Counter(); self.later = Counter(); self.local = defaultdict(Counter)
        self.templates = Counter(); self.anchors = Counter(); self.context = context; self.cache = {}
        for seq in sequences:
            previous = None
            for delta, anchor, template in seq:
                if previous is None:
                    self.first[delta] += 1
                else:
                    self.later[delta] += 1
                    self.local[previous][delta] += 1
                self.templates[template] += 1; self.anchors[anchor] += 1
                previous = len(template)
        self.template_occurrences = sum(self.templates.values())
        self.ineligible_occurrences = sum(n for t, n in self.templates.items() if len(t) > 3)

    def parameters(self, previous_count):
        if previous_count is not None:
            return super().parameters(previous_count)
        if None not in self.cache:
            size = self.first_limit + 1
            self.cache[None] = (0, {d: c * size + 1 for d, c in self.first.items()}, 1)
        return self.cache[None]

    def probability(self, delta, previous_count=None):
        lo, weights, default = self.parameters(previous_count)
        upper = self.first_limit if previous_count is None else LIMIT
        if type(delta) is not int or not lo <= delta <= upper:
            raise ValueError('delta outside stage support')
        total = sum(weights.values()) + (upper - lo + 1 - len(weights)) * default
        return Fraction(weights.get(delta, default), total)

    def evaluate(self, seq):
        validate(seq, self.first_limit)
        previous = None; loss = 0.
        for delta, _, template in seq:
            loss -= log(self.probability(delta, previous)); previous = len(template)
        return dict(groups=len(seq), nll_per_group_delta=loss / len(seq),
                    outcome='distinct-onset delta only; teacher-forced previous cardinality',
                    template_pitch_gate_likelihood_included=False)

    def sample_delta(self, rng, previous_count, remaining):
        # This sampler is only for the existing bounded generation target.
        if type(remaining) is not int or not 0 <= remaining <= 9216:
            raise ValueError('remaining output support must be0..9216')
        lo, weights, default = self.parameters(previous_count)
        upper = self.first_limit if previous_count is None else LIMIT
        hi = min(upper, remaining - 1)
        if hi < lo:
            return None
        total = (hi - lo + 1) * default + sum(w - default for d, w in weights.items() if lo <= d <= hi)
        draw = rng.randrange(total)
        for delta in range(lo, hi + 1):
            weight = weights.get(delta, default)
            if draw < weight:
                return delta
            draw -= weight
        raise AssertionError('bounded initial-rest draw')
