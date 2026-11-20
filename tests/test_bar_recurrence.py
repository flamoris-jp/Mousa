import importlib.util
from pathlib import Path
import sys
import unittest
TOOLS=Path(__file__).resolve().parents[1]/'tools';sys.path.insert(0,str(TOOLS))
try:
    spec=importlib.util.spec_from_file_location('bar_recurrence_test',TOOLS/'analyze_bar_recurrence.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
finally:sys.path.pop(0)


class BarRecurrenceTests(unittest.TestCase):
    def bars(self,patterns):
        return [dict(start=i*1152+j*384,end=i*1152+j*384+300,pitch=p) for i,bar in enumerate(patterns) for j,p in enumerate(bar)]

    def test_samepitch_rate_distinct_motif_recurrence(self):
        repeated=self.bars([[60,62,64],[65,67,69],[60,62,64],[65,67,69]])
        varied=self.bars([[60,62,64],[65,66,69],[60,63,64],[65,67,71]])
        a,b=module.analyze_notes(repeated),module.analyze_notes(varied)
        self.assertEqual(a['adjacent_same_pitch_fraction'],b['adjacent_same_pitch_fraction'])
        self.assertEqual(a['all_nonempty_pairs']['full_exact_rate'],1)
        self.assertLess(b['all_nonempty_pairs']['full_exact_rate'],1)

    def test_transposition_invariance_but_rhythm_sensitive(self):
        notes=self.bars([[60,62],[67,69]])
        result=module.analyze_notes(notes)
        self.assertEqual(result['all_nonempty_pairs']['full_exact_count'],1)
        notes[-1]['end']+=1
        result=module.analyze_notes(notes)
        self.assertEqual(result['all_nonempty_pairs']['full_exact_count'],0)
        self.assertEqual(result['all_nonempty_pairs']['relative_pitch_exact_count'],1)

    def test_empty_bars_not_recurrence(self):
        r=module.analyze_notes([])
        self.assertEqual(r['empty_bars'],8)
        self.assertEqual(r['all_nonempty_pairs']['eligible_pairs'],0)
        self.assertIsNone(r['all_nonempty_pairs']['full_exact_rate'])
        self.assertIsNone(r['adjacent_same_pitch_fraction'])

    def test_boundary_gate_not_clipped(self):
        notes=[dict(start=1000,end=1300,pitch=60),dict(start=2152,end=2452,pitch=62)]
        r=module.analyze_notes(notes)
        self.assertEqual(r['cross_bar_sounding_gates'],2)
        self.assertEqual(r['bar_onset_counts'][:3],[1,1,0])
        self.assertEqual(r['all_nonempty_pairs']['rhythm_exact_count'],1)
        self.assertEqual(notes[0]['end'],1300)

    def test_similarity_and_invalid(self):
        self.assertEqual(module.edit_similarity([0,2,4],[0,2,4]),1)
        self.assertAlmostEqual(module.edit_similarity([0,2,4],[0,3,4]),2/3)
        with self.assertRaises(ValueError):module.analyze_notes([dict(start=9216,end=9217,pitch=60)])
        with self.assertRaises(ValueError):module.analyze_notes([dict(start=True,end=3,pitch=60)])


if __name__=='__main__':unittest.main()
