from collections import Counter,defaultdict
import unittest
from pathlib import Path
import sys
from unittest.mock import patch
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.fourteen_context_model import FourteenContextModel
from mousa.bounded_context_model import BoundedContextModel
from mousa.optimized_feasible_generation import generate_optimized
with patch.object(sys,'path',[str(Path(__file__).resolve().parents[1]/'tools'),*sys.path]):
    import compare_bounded_corpus_expansion as wrapper


class BoundedCorpusTests(unittest.TestCase):
    def fixture(self,n):return [[(0,1+i%4),(2,3)] for i in range(n)],[[60+i%3,62+i%3] for i in range(n)]
    def test_old_probabilities_and_rng(self):
        for n,old_class in [(1,ContextOnsetGateModel),(12,ContextOnsetGateModel),(14,FourteenContextModel)]:
            seq,pitch=self.fixture(n);old=old_class(seq,pitch,timing_context=True,pitch_continuity=True);new=BoundedContextModel(seq,pitch,timing_context=True,pitch_continuity=True)
            for previous in (None,1,2,4,123):
                for pair in [(0,1),(2,3),(45,100)]:self.assertEqual(old.probability(pair,previous_gate=previous),new.probability(pair,previous_gate=previous))
            for seed in range(3):self.assertEqual(generate_optimized(old,seed,target_ticks=24,trailing_rest_ticks=2),generate_optimized(new,seed,target_ticks=24,trailing_rest_ticks=2))
    def test_boundaries_and_prefix(self):
        for n in (16,25,32):
            seq,pitch=self.fixture(n);m=BoundedContextModel(seq,pitch);expected=defaultdict(Counter)
            for s in seq:expected[s[0][1]][s[1][0]]+=1
            self.assertEqual(m.contexts,expected);self.assertEqual(m.intervals,Counter({2:n}));self.assertEqual(m.base.n,2*n)
            self.assertEqual(m._gate_prefix[-1],2*n);self.assertEqual(m._gate_prefix[0],sum(p[1]==1 for s in seq for p in s))
    def test_reject(self):
        for n in (0,33):
            seq,p=self.fixture(n)
            with self.assertRaises(ValueError):BoundedContextModel(seq,p)
        s,p=self.fixture(16);p[-1][-1]=True
        with self.assertRaises(ValueError):BoundedContextModel(s,p)
        with self.assertRaises(ValueError):BoundedContextModel([[(0,1)]*4000]*26,[[60]*4000]*26)
    def test_profile_restores_and_preflights(self):
        old=(wrapper.base.validate_assignment,wrapper.base.ContextOnsetGateModel)
        with self.assertRaises(RuntimeError):
            with wrapper.profile():raise RuntimeError('synthetic failure')
        self.assertEqual((wrapper.base.validate_assignment,wrapper.base.ContextOnsetGateModel),old)
        self.assertEqual(wrapper.preflight(16)['events'],32)
    def test_assignment_all_global_gates(self):
        def fixture(n):
            return {'schema_version':1,'related_evaluation_exclusions':['mutopia-580'],'diagnostic_families':{'640':['adam'],'921':['chopin']},'additions':[dict(work_id=f'w{i}',canonical_source_id=f'w{i}',family_id='f',file='x.mid',rights_evidence='x.json',review_reference='synthetic',sha256=f'{i:064x}',rights_evidence_sha256='a'*64,track=1,rights_approved=True,family_reviewed=True) for i in range(n)]}
        self.assertEqual(len(wrapper.validate_assignment(fixture(27))),27)
        for n in (0,28):
            with self.assertRaises(ValueError):wrapper.validate_assignment(fixture(n))
        for key,value in [('work_id','w0'),('canonical_source_id','w0'),('sha256','0'*64),('family_id','adam'),('canonical_source_id','mutopia-1692'),('rights_approved',False)]:
            a=fixture(11);a['additions'][-1][key]=value
            with self.assertRaises(ValueError):wrapper.validate_assignment(a)
