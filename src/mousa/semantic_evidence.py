"""Synthetic evidence-schema prototype, deliberately NOT an authorization service.

All accepted records must declare fictional provenance. No record can become a
training label here, regardless of review strings. Counts describe submitted
records, not independent listeners, consent, truth, or musical quality.
"""
from collections import Counter
import re

KINDS = ('observed-source', 'human-report', 'hypothesis')
STATES = ('missing', 'pending', 'rejected', 'approved')


def _fields(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        raise ValueError('schema_fields')


def _text(value, limit=2000):
    if type(value) is not str or not value.strip() or len(value) > limit:
        raise ValueError('text')


def validate(record):
    """Validate a fictional record; return no inferred labels or permissions."""
    _fields(record, ('id', 'source', 'artifact', 'segment', 'evidence', 'provenance', 'review', 'permitted_use'))
    _text(record['id'], 128)
    for name in ('source', 'artifact'):
        _fields(record[name], ('sha256', 'kind'))
        if type(record[name]['sha256']) is not str or not re.fullmatch('[0-9a-f]{64}', record[name]['sha256']):
            raise ValueError('digest')
        if record[name]['kind'] != 'synthetic':
            raise ValueError('synthetic_only')
    s = record['segment']
    _fields(s, ('track', 'start_tick', 'end_tick', 'ppq', 'artifact_total_ticks', 'render_ref'))
    if any(type(s[k]) is not int for k in ('track', 'start_tick', 'end_tick', 'ppq', 'artifact_total_ticks')):
        raise ValueError('segment_integer')
    if not (0 <= s['track'] < 256 and 1 <= s['ppq'] <= 32767 and
            0 <= s['start_tick'] < s['end_tick'] <= s['artifact_total_ticks'] <= 1024*s['ppq']):
        raise ValueError('segment_bounds')
    if s['render_ref'] is not None:
        _text(s['render_ref'], 256)
    e = record['evidence']
    _fields(e, ('kind', 'perspective', 'wording', 'language', 'proposed_tag'))
    if e['kind'] not in KINDS:
        raise ValueError('evidence_kind')
    perspectives = {'observed-source': ('source-marking', 'symbolic-measurement'),
                    'human-report': ('intent', 'perception', 'desired-change', 'cannot-judge'),
                    'hypothesis': ('interpretation',)}
    if e['perspective'] not in perspectives[e['kind']]:
        raise ValueError('evidence_perspective')
    _text(e['wording']); _text(e['language'], 32)
    if e['proposed_tag'] is not None:
        _text(e['proposed_tag'], 128)
    p = record['provenance']
    _fields(p, ('fictional', 'actor_role', 'reference'))
    if p['fictional'] is not True:
        raise ValueError('synthetic_only')
    expected = {'observed-source': 'synthetic-observer', 'human-report': 'fictional-listener', 'hypothesis': 'synthetic-researcher'}
    if p['actor_role'] != expected[e['kind']]:
        raise ValueError('evidence_provenance')
    _text(p['reference'], 256)
    if e['kind'] == 'human-report' and s['render_ref'] is None:
        raise ValueError('missing_audition_scope')
    r = record['review']
    _fields(r, ('state', 'reference'))
    if r['state'] not in STATES:
        raise ValueError('review_state')
    if r['reference'] is not None:
        _text(r['reference'], 256)
    if record['permitted_use'] not in ('none', 'synthetic-schema-test'):
        raise ValueError('unsupported_use')


def training_eligible(record):
    """Fail closed: authorization is deliberately unavailable in this prototype."""
    validate(record)
    return False


def summarize(records):
    """Bounded descriptive counts, including invalid records; no content output."""
    if type(records) not in (list, tuple) or len(records) > 1000:
        raise ValueError('batch_bound')
    kinds, reviews, reasons = Counter(), Counter(), Counter()
    ids = set(); accepted = 0
    for record in records:
        try:
            validate(record)
            if record['id'] in ids:
                raise ValueError('duplicate_id')
        except ValueError as exc:
            reasons[str(exc)] += 1
            continue
        ids.add(record['id']); accepted += 1
        kinds[record['evidence']['kind']] += 1
        reviews[record['review']['state']] += 1
    return dict(submitted=len(records), accepted=accepted, rejected=len(records)-accepted,
                evidence_counts=dict(kinds), review_counts=dict(reviews), rejection_counts=dict(reasons),
                training_eligible=0, actual_human_reports=0,
                interpretation='Synthetic schema counts only; not semantic accuracy, consent, independent listeners or appeal.')
