import importlib.util
from pathlib import Path
import sys
import unittest
from fractions import Fraction
from mousa.optimized_feasible_generation import generate_optimized
TOOLS=Path(__file__).resolve().parents[1]/'tools'
sys.path.insert(0,str(TOOLS))
try:
    spec=importlib.util.spec_from_file_location('timing_transfer_test',TOOLS/'compare_timing_generation_transfer.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
finally:sys.path.pop(0)


class TimingGenerationTests(unittest.TestCase):
    def test_only_timing_flag_differs(self):
        models=module.make_models([[(0,3),(1,4),(2,2)]],[[60,62,64]])
        a,b=models['timing0'],models['timing1']
        self.assertFalse(a.timing_context);self.assertTrue(b.timing_context)
        self.assertEqual(a.strength,b.strength)
        self.assertEqual(a.base.counts,b.base.counts)
        for pitch in (None,60,62,64):self.assertEqual(a.pitch_weights(pitch),b.pitch_weights(pitch))
        for m in models.values():
            x=generate_optimized(m,3,target_ticks=30,trailing_rest_ticks=5,uniform_mix=Fraction(1,4))
            self.assertEqual(x,generate_optimized(m,3,target_ticks=30,trailing_rest_ticks=5,uniform_mix=Fraction(1,4)))

    def test_descriptor_denominators_and_tail(self):
        result=module.descriptors([dict(start=0,end=10,pitch=60),dict(start=800,end=900,pitch=62)],target=1000)
        self.assertEqual(result['actual_silent_tail_ticks'],100)
        self.assertEqual(result['short_gate_count'],1)
        self.assertEqual(result['last_quarter_onsets'],1)
        self.assertEqual(result['mean_abs_pitch_interval'],2)
        empty=module.descriptors([],target=1000)
        self.assertIsNone(empty['mean_abs_pitch_interval']);self.assertIsNone(empty['actual_silent_tail_ticks'])


if __name__=='__main__':unittest.main()
