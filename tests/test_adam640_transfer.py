import importlib.util
from pathlib import Path
import sys
import unittest
from mousa.overlap_midi import OverlapMelody
from mousa.tick_midi import TickNote

TOOLS=Path(__file__).resolve().parents[1]/'tools'
sys.path.insert(0,str(TOOLS))
try:
    spec=importlib.util.spec_from_file_location('adam640_transfer_test',TOOLS/'evaluate_adam640_transfer.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
finally:sys.path.pop(0)


class AdamCoverageTests(unittest.TestCase):
    def test_exact_pairs_no_pitch_prediction(self):
        m=OverlapMelody((TickNote(0,120,60),TickNote(60,180,64)),200,(4,4),ppq=480)
        coverage,pairs=module.timing_coverage(m)
        self.assertEqual(pairs,[(0,96),(48,96)])
        self.assertEqual(coverage['supported_events'],2)
        self.assertEqual(m.notes[0].end,120)

    def test_nonrepresentable_explicit(self):
        m=OverlapMelody((TickNote(1,3,60),),4,(4,4),ppq=480)
        coverage,pairs=module.timing_coverage(m)
        self.assertEqual(pairs,[])
        self.assertEqual(coverage['total_events'],1)
        self.assertEqual(coverage['unsupported_events'][0]['reason'],'incompatible_PPQ384')

    def test_long_duration_not_silently_split(self):
        m=OverlapMelody((TickNote(0,33*384,60),),34*384,(4,4),ppq=384)
        coverage,pairs=module.timing_coverage(m)
        self.assertFalse(pairs)
        self.assertEqual(coverage['unsupported_events'][0]['reason'],'outside_fixed_duration_support')


if __name__=='__main__':unittest.main()
