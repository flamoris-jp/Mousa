"""Retrospective baseline exposure audit; input/output remain outside Git."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def identity(row):
    return (row['family'], row['target_index'])

def fit(rows):
    marginal = Counter(r['label'] for r in rows)
    contexts = [defaultdict(Counter), defaultdict(Counter)]
    for r in rows:
        for n in (1, 2):
            contexts[n-1][tuple(r['input'][-n:])][r['label']] += 1
    return len(rows), marginal, contexts

def predict(fitted, row, order):
    count, marginal, contexts = fitted
    p = [(marginal[k] + 1 / 49) / (count + 1) for k in range(49)]
    if order == 'trigram':
        for n in (1, 2):
            c = contexts[n-1].get(tuple(row['input'][-n:]), {})
            z = sum(c.values())
            p = [(c.get(k, 0) + 4 * p[k]) / (z + 4) for k in range(49)]
    if not all(math.isfinite(v) and v > 0 for v in p) or abs(sum(p)-1)>1e-10:
        raise ValueError('invalid probabilities')
    return p

def aggregate(rows):
    grouped = defaultdict(list)
    for r in rows:
        grouped[r['family']].append(r)
    per = [{'family': k, 'n': len(v), 'nll': statistics.mean(r['nll'] for r in v),
            'accuracy': statistics.mean(r['correct'] for r in v)} for k,v in sorted(grouped.items())]
    return {'windows': len(rows), 'families': len(per),
            'family_macro_nll': statistics.mean(r['nll'] for r in per),
            'family_macro_accuracy': statistics.mean(r['accuracy'] for r in per), 'per_family': per}

def exposures(arm):
    rows = arm['train']
    if len({identity(r) for r in rows}) != len(rows):
        raise ValueError('duplicate training identity')
    indices = [i for batch in arm['batches'] for i in batch]
    if len(indices) != 3200 or any(type(i) is not int or i < 0 or i >= len(rows) for i in indices):
        raise ValueError('invalid recorded exposure')
    return {'all_unique_windows': rows,
            'sampled_3200_with_multiplicity': [rows[i] for i in indices],
            'sampled_unique_windows_only': [rows[i] for i in sorted(set(indices))]}

def audit(data, recorded):
    tests = data['test']
    if len({identity(r) for r in tests}) != len(tests):
        raise ValueError('duplicate test identity')
    runs = {(r['condition'],r['seed']): r for r in recorded['runs']}
    results, private = [], []
    for arm in data['arms']:
        run = runs[(arm['condition'],arm['seed'])]
        if {r['family'] for r in arm['train']} & {r['family'] for r in tests}:
            raise ValueError('train/test family overlap')
        if [identity(r) for r in run['final_test']] != [identity(r) for r in tests]:
            raise ValueError('prediction identities differ')
        if [r['target'] for r in run['final_test']] != [r['label'] for r in tests]:
            raise ValueError('prediction labels differ')
        neural = aggregate([dict(r, correct=int(r['target']==r['prediction'])) for r in run['final_test']])
        for name, rows in exposures(arm).items():
            fitted = fit(rows)
            for model in ('unigram','trigram'):
                scores = []
                for r in tests:
                    p = predict(fitted,r,model)
                    scores.append({'family': r['family'], 'target_index': r['target_index'],
                                   'nll': -math.log(p[r['label']]),
                                   'correct': int(max(range(49),key=lambda k:p[k]) == r['label'])})
                metrics = aggregate(scores)
                n_by_family = {r['family']:r['nll'] for r in neural['per_family']}
                metrics.update({'condition':arm['condition'],'seed':arm['seed'],'model':model,'exposure':name,
                    'training_observations':len(rows),'unique_training_windows':len({identity(r) for r in rows}),
                    'training_families':len({r['family'] for r in rows}),
                    'training_target_classes':len({r['label'] for r in rows}),
                    'encoder_nll':neural['family_macro_nll'],
                    'encoder_accuracy':neural['family_macro_accuracy'],
                    'count_minus_encoder_nll':metrics['family_macro_nll']-neural['family_macro_nll'],
                    'count_better_families':sum(r['nll']<n_by_family[r['family']] for r in metrics['per_family'])})
                results.append(metrics)
                private.append({'condition':arm['condition'],'seed':arm['seed'],'model':model,'exposure':name,'rows':scores})
    return results, private

def main():
    p=argparse.ArgumentParser();p.add_argument('--replay',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();plan=json.loads((HERE/'plan.json').read_text())
    if a.out.exists(): raise FileExistsError('output must be new')
    if sha(a.replay/'data.json') != plan['data_sha256']: raise ValueError('data digest mismatch')
    original=json.loads((HERE.parent/'maidionis-midi-learning/summary.json').read_text())
    if sha(a.replay/'recorded-results.json') != original['raw_result_sha256']: raise ValueError('recorded result digest mismatch')
    data=json.loads((a.replay/'data.json').read_text());recorded=json.loads((a.replay/'recorded-results.json').read_text())
    results, private=audit(data,recorded)
    result={'schema':'mousa-exposure-audit-v1','plan_sha256':sha(HERE/'plan.json'),
            'script_sha256':sha(__file__),'data_sha256':sha(a.replay/'data.json'),
            'recorded_results_sha256':sha(a.replay/'recorded-results.json'),
            'test_status':plan['test_status'],'neural_refit':False,'results':results}
    a.out.mkdir(parents=True)
    for n,d in [('summary.json',result),('predictions-private.json',private)]:
        (a.out/n).write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))

if __name__=='__main__': main()
