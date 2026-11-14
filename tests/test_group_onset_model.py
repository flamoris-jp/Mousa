import unittest,random
from fractions import Fraction
from mousa.group_onset_model import GroupOnsetModel,generate,observations,LIMIT
from mousa.tick_midi import TickNote

class GroupTests(unittest.TestCase):
    def fixture(self):
        one=((0,2,80,7),);two=((0,3,90,5),(4,1,70,9))
        return [[(0,60,one),(2,62,two),(3,60,one)],[(1,65,two),(4,60,one)]]
    def test_support_and_normalization(self):
        for arm in (False,True):
            m=GroupOnsetModel(self.fixture(),context=arm)
            for prev in (None,1,2,3):
                lo=0 if prev is None else 1
                self.assertEqual(sum((m.probability(d,prev) for d in range(lo,LIMIT+1)),Fraction(0)),1)
                if prev is not None:
                    with self.assertRaises(ValueError):m.probability(0,prev)
            self.assertEqual(m.first,{0:1,1:1});self.assertEqual(m.later,{2:1,3:1,4:1})
            self.assertEqual(m.local,{1:{2:1},2:{3:1,4:1}})
    def test_context_formula(self):
        raw=GroupOnsetModel(self.fixture());ctx=GroupOnsetModel(self.fixture(),context=True)
        for d in (1,2,3,4,123):
            self.assertEqual(ctx.probability(d,2),(Fraction(int(d in (3,4)))+4*raw.probability(d,2))/6)
            self.assertEqual(ctx.probability(d,99),raw.probability(d,99))
        self.assertEqual(ctx.probability(0),raw.probability(0))
    def test_template_fields_and_generation(self):
        n=[TickNote(3,8,64,90,12),TickNote(3,5,60,70,8),TickNote(9,12,61,50,7)]
        obs=observations(n,20);self.assertEqual(obs[0],(3,60,((4,5,90,12),(0,2,70,8))))
        for arm in (False,True):
            m=GroupOnsetModel(self.fixture(),context=arm);g=generate(m,4,target=24,tail=3)
            self.assertEqual(g,generate(m,4,target=24,tail=3))
            self.assertTrue(all(b['onset']>a['onset'] for a,b in zip(g['groups'],g['groups'][1:])))
            for group in g['groups']:
                self.assertIn(group['template'],m.templates)
            for note in g['notes']:
                self.assertTrue(0<=note['start']<note['end']<=24)
                active=[n for n in g['notes'] if n['start']<=note['start']<n['end']]
                self.assertLessEqual(len(active),3);self.assertEqual(len(active),len({n['pitch'] for n in active}))
    def test_large_templates_not_removed_from_fit(self):
        t=tuple((i,2,80,0) for i in range(4));m=GroupOnsetModel([[(0,60,t),(2,60,t)]])
        self.assertEqual(m.template_occurrences,2);self.assertEqual(m.ineligible_occurrences,2)
        self.assertEqual(generate(m,0)['status'],'blocked');self.assertEqual(m.later,{2:1})
    def test_bounds_and_distinct_onsets(self):
        s=self.fixture();s[0][1]=(0,*s[0][1][1:])
        with self.assertRaises(ValueError):GroupOnsetModel(s)
        with self.assertRaises(ValueError):GroupOnsetModel(self.fixture()*17)
        with self.assertRaises(ValueError):generate(GroupOnsetModel(self.fixture()),0,tail=9216)
        self.assertIsNone(GroupOnsetModel(self.fixture()).sample_delta(random.Random(0),1,1))

    def test_explicit_input_and_cpu_failure(self):
        with self.assertRaises(ValueError):GroupOnsetModel([None])
        with self.assertRaises(ValueError):GroupOnsetModel([7])
        m=GroupOnsetModel(self.fixture())
        self.assertEqual(generate(m,0,cpu_deadline=0)['status'],'cpu_budget_exhausted')
        for bad in (True,float('nan'),-1):
            with self.assertRaises(ValueError):generate(m,0,cpu_deadline=bad)
