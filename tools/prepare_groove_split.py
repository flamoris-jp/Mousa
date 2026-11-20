"""Read-only drum corpus split preparation. No model fit or threshold selection."""
import argparse
from collections import Counter, defaultdict
from functools import reduce
from hashlib import sha256
import io
import json
from math import gcd
from pathlib import Path
import time


def digest(data):
    return sha256(data).hexdigest()


def split_for(drummer):
    if drummer not in {f'drummer{i}' for i in range(1, 11)}:
        raise ValueError('unknown drummer')
    n = int(drummer[7:])
    return 'train' if n <= 6 else 'validation' if n <= 8 else 'test'


def features(events):
    """Events are exact ordered (absolute tick, drum instrument); no mutation."""
    if not events or len(events) > 100000:
        raise ValueError('event bound')
    previous = 0
    pairs = []
    for tick, key in events:
        if type(tick) is not int or tick < previous or type(key) is not int or not 0 <= key <= 127:
            raise ValueError('invalid onset/key')
        pairs.append((key, tick - previous))
        previous = tick
    normalized_iois = [0] + [dt for _, dt in pairs[1:]]
    divisor = reduce(gcd, normalized_iois, 0) or 1
    normalized = [(key, dt // divisor) for (key, _), dt in zip(pairs, normalized_iois)]
    # Comparison-only timing buckets; not returned as model targets.
    coarse = tuple((key, (dt + 60) // 120) for key, dt in pairs)
    windows = {}
    for i in range(max(0, len(coarse) - 7)):
        h = digest(repr(coarse[i:i + 8]).encode())
        windows.setdefault(h, i)
    return {'exact': digest(repr(events).encode()), 'normalized': digest(repr(normalized).encode()),
            'windows': windows, 'events': len(events), 'unsupported_iois': sum(dt > 30720 for _, dt in pairs)}


def compare(a, b):
    shared = a['windows'].keys() & b['windows'].keys()
    union = len(a['windows']) + len(b['windows']) - len(shared)
    jaccard = len(shared) / union if union else 0.0
    exact = a['exact'] == b['exact']
    normalized = a['normalized'] == b['normalized']
    first = min(((a['windows'][h], b['windows'][h]) for h in shared), default=None)
    return {'exact_onset_key': exact, 'tempo_offset_normalized': normalized,
            'shared_unique_windows': len(shared), 'a_unique_windows': len(a['windows']),
            'b_unique_windows': len(b['windows']), 'union_unique_windows': union,
            'jaccard': jaccard, 'containment_a': len(shared) / len(a['windows']) if a['windows'] else None,
            'containment_b': len(shared) / len(b['windows']) if b['windows'] else None,
            'first_matching_event_indices': first, 'matching_window_events': 8,
            'strong_unresolved': exact or normalized or jaccard >= .80}


def read_events(path, expected_hash):
    import mido
    raw = path.read_bytes()
    if len(raw) > 2_000_000 or digest(raw) != expected_hash:
        raise ValueError('source integrity')
    midi = mido.MidiFile(file=io.BytesIO(raw))
    if midi.ticks_per_beat != 480 or len(midi.tracks) > 64 or sum(map(len, midi.tracks)) > 250000:
        raise ValueError('MIDI profile')
    ordered = []
    for ti, track in enumerate(midi.tracks):
        tick = 0
        for mi, msg in enumerate(track):
            if type(msg.time) is not int or msg.time < 0:
                raise ValueError('MIDI time')
            tick += msg.time
            if tick > 480 * 4 * 10000:
                raise ValueError('MIDI timeline')
            if msg.type == 'note_on' and msg.velocity > 0:
                if msg.channel != 9:
                    raise ValueError('not drum channel')
                ordered.append((tick, ti, mi, msg.note))
    return [(t, k) for t, _, _, k in sorted(ordered)]


def run(root, plan_path, output):
    start = time.process_time()
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    inventory_bytes = (root / 'private-inventory.json').read_bytes()
    if digest(inventory_bytes) != plan['inventory_sha256']:
        raise ValueError('inventory hash')
    rows = json.loads(inventory_bytes)['records']
    if len(rows) > 1500 or output.exists():
        raise ValueError('row bound or existing destination')
    def budget():
        if time.process_time() - start > 90:
            raise RuntimeError('prepare CPU budget exceeded; no fit allowed')
    non_eval = [r for r in rows if r['session'].split('/')[-1] != 'eval_session']
    candidates = []
    overcap = []
    for drummer in sorted({r['drummer'] for r in rows}):
        eligible = []
        for row in non_eval:
            if row['drummer'] != drummer:
                continue
            if 1 <= row['metrics']['note_on_positive'] <= 4096:
                eligible.append(row)
            else:
                overcap.append(row['id'])
        candidates.extend(sorted(eligible, key=lambda r: (r['sha256'], r['id']))[:2])
    if sum(r['metrics']['note_on_positive'] for r in candidates) > 30000:
        raise ValueError('whole performance event budget exceeded')
    byte_groups = defaultdict(list)
    for row in non_eval:
        byte_groups[row['sha256']].append(row)
    crossing = [[r['id'] for r in group] for group in byte_groups.values()
                if len({split_for(r['drummer']) for r in group}) > 1]
    all_features = {}
    event_count = 0
    for row in rows:
        budget()
        path = (root / row['relative_path']).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError('unsafe source path')
        events = read_events(path, row['sha256'])
        event_count += len(events)
        if event_count > 500000 or len(events) != row['metrics']['note_on_positive']:
            raise ValueError('event bound or inventory count mismatch')
        all_features[row['id']] = features(events)
    hits = []
    quarantined = set()
    comparisons = 0
    for a in candidates:
        for b in non_eval:
            if split_for(a['drummer']) == split_for(b['drummer']):
                continue
            budget()
            comparisons += 1
            if comparisons > 25000:
                raise ValueError('comparison bound')
            result = compare(all_features[a['id']], all_features[b['id']])
            if result['shared_unique_windows'] or result['exact_onset_key'] or result['tempo_offset_normalized']:
                hits.append({'a': a['id'], 'b': b['id'], **result})
            if result['strong_unresolved']:
                quarantined.add(a['id'])
    selected = []
    for row in candidates:
        f = all_features[row['id']]
        status = 'quarantined_strong_unresolved' if row['id'] in quarantined else 'unsupported_ioi' if f['unsupported_iois'] else 'eligible_pending_parent_review'
        selected.append({'id': row['id'], 'drummer': row['drummer'], 'session': row['session'],
                         'proposed_split': split_for(row['drummer']), 'original_split': row['split'],
                         'sha256': row['sha256'], 'event_count': f['events'], 'status': status,
                         'unsupported_ioi_count': f['unsupported_iois']})
    report = {'plan_sha256': digest(plan_bytes), 'inventory_sha256': digest(inventory_bytes),
              'fit_performed': False, 'predictive_scores_observed': False,
              'status': 'blocked_cross_split_exact_duplicate' if crossing else 'prepared_pending_parent_review',
              'reserved_eval_count': len(rows)-len(non_eval), 'inventory_count': len(rows),
              'all_inventory_events_verified': event_count, 'candidate_count': len(candidates),
              'candidate_event_count': sum(r['event_count'] for r in selected),
              'over_event_cap_count': len(overcap), 'not_selected_non_eval_count': len(non_eval)-len(overcap)-len(candidates),
              'cross_split_byte_duplicate_groups': crossing,
              'within_split_byte_duplicate_groups': [[r['id'] for r in g] for g in byte_groups.values() if len(g)>1 and len({split_for(r['drummer']) for r in g}) == 1],
              'cross_split_comparisons': comparisons, 'weak_or_strong_pair_hits': len(hits),
              'strong_unresolved_pairs': sum(h['strong_unresolved'] for h in hits),
              'candidate_status_counts': dict(Counter(r['status'] for r in selected)), 'candidates': selected,
              'prepare_cpu_seconds': time.process_time()-start,
              'limitations': ['Candidate matches are review evidence, not proof of copied compositions.',
                             'Only selected-versus-cross-split non-eval comparisons; near-pattern independence is not established.',
                             'Original expressive timing, velocities and controls are unchanged; comparison fingerprints omit performance dimensions.',
                             'No model fit, generation, audio or musical quality assessment.']}
    output.mkdir(parents=True)
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (output/'private-pair-evidence.json').write_text(json.dumps(hits,indent=2)+'\n')
    return report


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.root,args.plan,args.output),indent=2))
