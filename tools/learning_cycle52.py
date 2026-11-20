"""Retrospective leave-linked-family-out timing learning diagnostic.

No fresh test claim: all 18 works were previously observed and trained.
"""
from collections import Counter, defaultdict
from math import log
import random
from statistics import mean
from mousa.gate_context_group_model import GateContextGroupModel, gate_bin


def components(ids, families, links):
    if set(ids) != set(families) or len(ids) != len(set(ids)):
        raise ValueError('exact family coverage required')
    parent = {k:k for k in ids}
    def root(k):
        while parent[k] != k: k = parent[k]
        return k
    def join(a,b):
        if a not in parent or b not in parent: raise ValueError('unknown linked work')
        parent[root(b)] = root(a)
    for i,a in enumerate(ids):
        for b in ids[i+1:]:
            if families[a] == families[b]: join(a,b)
    for a,b in links: join(a,b)
    groups = defaultdict(list)
    for k in ids: groups[root(k)].append(k)
    return sorted(groups.values())


def shuffled_model(sequences, seed):
    model = GateContextGroupModel(sequences, arm='previous_max_gate_binned')
    model.local = defaultdict(Counter)
    for index,seq in enumerate(sequences):
        keys = [gate_bin(max(t[1] for t in row[2])) for row in seq[:-1]]
        random.Random(seed * 1009 + index).shuffle(keys)
        for key,row in zip(keys,seq[1:]): model.local[key][row[0]] += 1
    model.cache = {}
    return model


def score(model, seq):
    # Independent closed-form probability check against model implementation.
    losses=[]; previous=None
    for i,(delta,_,template) in enumerate(seq):
        counts=model.first if i==0 else model.later
        size=65537 if i==0 else 12288
        q=(counts[delta]+1/size)/(sum(counts.values())+1)
        local=model.local.get(previous) if model.context and i else None
        if local: q=(local[delta]+4*q)/(sum(local.values())+4)
        if abs(q-float(model.probability(delta,previous)))>1e-14:
            raise AssertionError('independent probability mismatch')
        losses.append(-log(q))
        previous=gate_bin(max(t[1] for t in template))
    return dict(first_nll=losses[0],later_nll_sum=sum(losses[1:]),
                later_count=len(losses)-1,later_mean_nll=mean(losses[1:]) if len(losses)>1 else None)


def summary(rows):
    eligible=[r for r in rows if r['later_count']]
    return dict(works=len(rows),eligible=len(eligible),later_count=sum(r['later_count'] for r in rows),
                work_macro=mean(r['later_mean_nll'] for r in eligible),
                pooled=sum(r['later_nll_sum'] for r in eligible)/sum(r['later_count'] for r in eligible))
