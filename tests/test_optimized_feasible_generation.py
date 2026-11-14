from fractions import Fraction as F
from pathlib import Path
import tempfile
import importlib.util
import unittest
from unittest.mock import patch
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.feasible_context_generation import feasible_masses,_weights,generate_feasible
from mousa.optimized_feasible_generation import optimized_masses,generate_optimized


class OptimizedTests(unittest.TestCase):
    def model(self):
        return ContextOnsetGateModel([[(0,3),(1,2),(2,4)]],[[60,62,64]],timing_context=True,pitch_continuity=True)

    def test_release_mass_identical_and_exact(self):
        m=self.model();notes=[dict(start=0,end=e,pitch=p) for e,p in [(1,60),(2,62),(2,64)]]
        for alpha in (F(0),F(1,4)):
            weights=_weights(m,60,alpha)
            kwargs=dict(previous=0,previous_gate=3,notes=notes,remaining_ticks=4,pitch_weights=weights)
            masses=optimized_masses(m,**kwargs)
            self.assertEqual(masses,feasible_masses(m,**kwargs))
            exact=[]
            for dt in range(4):
                active=[n for n in notes if n['end']>dt]
                legal=[] if len(active)>=3 else [p for p in m.vocabulary if p not in {n['pitch'] for n in active}]
                exact.append(sum((m.probability((dt,g),previous_gate=3)*F(weights[m.vocabulary.index(p)],sum(weights))
                    for g in range(1,5-dt) for p in legal),F(0)))
            self.assertEqual([F(v,sum(masses)) for v in masses],[v/sum(exact) for v in exact])

    def test_exact_seed_parity(self):
        m=self.model()
        for seed in range(5):
            for alpha in (F(0),F(1,4)):
                old=generate_feasible(m,seed,feasible_mask=True,uniform_mix=alpha,target_ticks=50)
                new=generate_optimized(m,seed,uniform_mix=alpha,target_ticks=50)
                for k,v in old.items():self.assertEqual(new[k],v)

    def test_trailing_rest_stops_without_modifying_notes(self):
        m=self.model()
        with patch('mousa.optimized_feasible_generation.sample_optimized',side_effect=[(0,8,60),(8,2,62)]):
            exact=generate_optimized(m,0,target_ticks=10)
        with patch('mousa.optimized_feasible_generation.sample_optimized',return_value=(0,8,60)) as sample:
            relaxed=generate_optimized(m,0,target_ticks=10,trailing_rest_ticks=2)
        self.assertEqual(sample.call_count,1)
        self.assertEqual(relaxed['notes'],exact['notes'][:1])
        self.assertEqual(relaxed['endpoint_policy']['actual_silent_tail_ticks'],2)
        self.assertEqual(relaxed['target_ticks'],10)

    def test_gap_bound_and_no_empty_success(self):
        m=self.model()
        with patch('mousa.optimized_feasible_generation.sample_optimized',side_effect=[(0,7,60),(7,1,62)]) as sample:
            r=generate_optimized(m,0,target_ticks=10,trailing_rest_ticks=2)
        self.assertEqual(sample.call_count,2);self.assertEqual(r['endpoint_policy']['actual_silent_tail_ticks'],2)
        with patch('mousa.optimized_feasible_generation.sample_optimized',return_value=None):
            r=generate_optimized(m,0,target_ticks=10,trailing_rest_ticks=9)
        self.assertEqual(r['status'],'blocked');self.assertEqual(r['notes'],[])

    @unittest.skipUnless(importlib.util.find_spec('mido'),'optional mido unavailable')
    def test_silent_tail_midi_eot(self):
        from mousa.overlap_midi import OverlapMelody,write_midi,read_midi
        from mousa.tick_midi import TickNote
        melody=OverlapMelody((TickNote(0,8,60),),10,(6,8),ppq=384)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'tail.mid';write_midi(melody,path);self.assertEqual(read_midi(path,1),melody)

    def test_invalid_inputs(self):
        for gap in (-1,385,True,1.5):
            with self.assertRaises(ValueError):generate_optimized(self.model(),0,trailing_rest_ticks=gap)
        with self.assertRaises(ValueError):generate_optimized(self.model(),0,target_ticks=1,trailing_rest_ticks=1)


if __name__=='__main__':unittest.main()
