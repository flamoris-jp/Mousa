"""Optional clock contexts for research; position is not a quality judgment.

Counts reset at each song start, assumed to be its supplied metrical origin.
Anacrusis alignment is the caller's responsibility. Phrase position means a
fixed number of bars, not an inferred musical phrase. Evaluation retains the
base 3,328-event support; generation-only rest masks do not alter its NLL.
"""
from collections import Counter, defaultdict
import math
import random
from types import SimpleNamespace

from mousa.factorized_baseline import FixedEventModel, PITCHES, DURATIONS, onset_phrases
from mousa.melodic_event_model import MelodicEventModel


def _bar_steps(meter):
    if type(meter) is not tuple or any(type(x) is not int for x in meter) or meter not in ((4, 4), (6, 8)):
        raise ValueError('explicit 4/4 or 6/8 meter required')
    return 16 if meter == (4, 4) else 12


class PositionEventModel:
    """Wrap the melodic control, optionally conditioning counts on grid time.

    songs: list of (meter_tuple, event_sequence[, origin_steps]). origin_steps
    is the grid offset of the first event inside its bar, not a detected pickup.
    It also shifts the fixed phrase clock, without establishing phrase origin.
    Backoff is exact position +
    previous event, position unigram, then the unchanged melodic control.
    Meter is part of each position key, so 6/8 and 4/4 counts never collide.
    Turning both position flags off reproduces control probabilities exactly.

    position_strength=k shrinks event COUNTS before base factorization:
    w=n/(n+k); counts=w*positional_counts+(1-w)*control_counts.
    This is not a mixture of joint probabilities, nor independent mixing of
    output marginals. Effective count mass changes and base smoothing remains.
    k=0 retains hard backoff; k tending to infinity recovers smoothed control.
    No held-out data are used for estimating these counters.
    """
    def __init__(self, songs, *, meter_position=False, phrase_position=False,
                 phrase_bars=4, relative=False, duration_prior='typed', prior_mass=1.,
                 position_strength=0.):
        if type(meter_position) is not bool or type(phrase_position) is not bool:
            raise ValueError('position switches must be bool')
        if type(phrase_bars) is not int or not 1 <= phrase_bars <= 32:
            raise ValueError('phrase_bars must be 1..32')
        if type(songs) is not list or not 1 <= len(songs) <= 12:
            raise ValueError('bounded song list required')
        if (type(position_strength) not in (int, float)
                or not math.isfinite(position_strength) or position_strength < 0):
            raise ValueError('position_strength must be finite and nonnegative')
        self.position_strength = position_strength
        normalized = []
        for song in songs:
            if not isinstance(song, (tuple, list)) or len(song) not in (2, 3):
                raise ValueError('song must contain meter, events, optional origin')
            meter, sequence = song[:2]
            origin = song[2] if len(song) == 3 else 0
            self._validate_origin(meter, origin)
            FixedEventModel.validate(sequence)
            normalized.append((meter, sequence, origin))
        self.control = MelodicEventModel([s for _, s, _ in normalized], relative=relative,
                                        duration_prior=duration_prior, prior_mass=prior_mass)
        self.meter_position, self.phrase_position = meter_position, phrase_position
        self.phrase_bars = phrase_bars
        self.position_counts = defaultdict(Counter)
        self.transition_counts = defaultdict(Counter)
        for meter, sequence, origin in normalized:
            encoded, _ = self.control.encode(sequence)
            elapsed = 0
            for i, event in enumerate(encoded):
                key = self.position_key(meter, elapsed, origin_steps=origin)
                self.position_counts[key][event] += 1
                if i:
                    self.transition_counts[(key, encoded[i - 1])][event] += 1
                elapsed += sequence[i][1]

    @staticmethod
    def _validate_origin(meter, origin_steps):
        bar = _bar_steps(meter)
        if type(origin_steps) is not int or not 0 <= origin_steps < bar:
            raise ValueError('origin_steps must be an integer within the bar')
        return bar

    def position_key(self, meter, elapsed, *, origin_steps=0):
        bar = self._validate_origin(meter, origin_steps)
        if type(elapsed) is not int or elapsed < 0:
            raise ValueError('nonnegative integer clock required')
        elapsed += origin_steps
        return (meter, elapsed % bar if self.meter_position else None,
                (elapsed // bar) % self.phrase_bars if self.phrase_position else None)

    def context(self, history, *, meter, origin_steps=0):
        self._validate_origin(meter, origin_steps)
        if history:
            FixedEventModel.validate(history)
        fallback, last = self.control.context(history)
        if not (self.meter_position or self.phrase_position):
            return fallback, last
        encoded, _ = self.control.encode(history)
        key = self.position_key(meter, sum(d for _, d in history), origin_steps=origin_steps)
        counts = self.transition_counts.get((key, encoded[-1])) if encoded else None
        counts = counts or self.position_counts.get(key)
        if not counts:
            return fallback, last
        if self.position_strength == 0:
            return counts, last
        n = sum(counts.values())
        w = n / (n + self.position_strength)
        pooled = Counter({event: w * counts[event] + (1 - w) * fallback[event]
                          for event in sorted(counts.keys() | fallback.keys())})
        return pooled, last

    def distributions(self, history, *, meter, origin_steps=0):
        # Reuse the control's exact smoothing and valid-pitch normalization.
        view = SimpleNamespace(context=lambda h: self.context(h, meter=meter, origin_steps=origin_steps),
                               relative=self.control.relative,
                               prior_mass=self.control.prior_mass,
                               duration_prior=self.control.duration_prior,
                               duration_global=self.control.duration_global)
        return MelodicEventModel.distributions(view, history)

    def evaluate(self, sequence, *, meter, origin_steps=0):
        self._validate_origin(meter, origin_steps)
        view = SimpleNamespace(distributions=lambda h: self.distributions(h, meter=meter, origin_steps=origin_steps))
        return MelodicEventModel.evaluate(view, sequence)

    def generate(self, seed, *, meter, steps=128, source_grids=(), guard=True,
                 max_rest_run=None, max_attempts=64, origin_steps=0):
        """Bounded rejection with an optional explicit maximum consecutive rest.

        Mask invalid rest durations BEFORE sampling, then renormalize the joint
        distribution. Final-event clipping matches the control, not its NLL.
        Exhausted copy rejection returns partial output with status='blocked'.
        This narrow 8-onset guard is not proof of originality or legal clearance.
        """
        self._validate_origin(meter, origin_steps)
        if (type(seed) is not int or type(steps) is not int or not 1 <= steps <= 4096
                or type(guard) is not bool or type(max_attempts) is not int
                or not 1 <= max_attempts <= 64):
            raise ValueError('invalid bounded generation settings')
        if max_rest_run is not None and (type(max_rest_run) is not int or not 0 <= max_rest_run <= 4096):
            raise ValueError('max_rest_run must be None or 0..4096')
        if not isinstance(source_grids, (list, tuple)) or len(source_grids) > 12:
            raise ValueError('bounded source list required')
        forbidden = {phrase for source in source_grids for phrase in onset_phrases(source)}
        rng = random.Random(seed)
        history, tokens = [], []
        rejections = rest_run = 0
        while len(tokens) < steps:
            ps, ds = self.distributions(history, meter=meter, origin_steps=origin_steps)
            remaining = steps - len(tokens)
            allowed = {rest: [d for d in DURATIONS if not rest or max_rest_run is None
                             or rest_run + min(d, remaining) <= max_rest_run]
                       for rest in (False, True)}
            masses = {rest: sum(ds[rest][d] for d in allowed[rest]) for rest in (False, True)}
            for _ in range(max_attempts):
                pitch = rng.choices(PITCHES, weights=[ps[p] * masses[p == -1] for p in PITCHES])[0]
                duration = min(rng.choices(allowed[pitch == -1],
                                          weights=[ds[pitch == -1][d] for d in allowed[pitch == -1]])[0], remaining)
                addition = [0] * duration if pitch == -1 else [pitch] + [1] * (duration - 1)
                candidate = tokens + addition
                if guard and any(p in forbidden for p in onset_phrases(candidate)):
                    rejections += 1
                    continue
                tokens = candidate
                history.append((pitch, duration))
                rest_run = rest_run + duration if pitch == -1 else 0
                break
            else:
                return dict(status='blocked', tokens=tokens, rejections=rejections,
                            reason='bounded phrase-copy rejection exhausted', max_rest_run=max_rest_run)
        return dict(status='complete', tokens=tokens, rejections=rejections,
                    max_rest_run=max_rest_run,
                    matching_8_note_phrases=sum(p in forbidden for p in onset_phrases(tokens)))
