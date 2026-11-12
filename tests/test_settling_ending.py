from unittest.mock import patch
import unittest
from mousa.settling_ending import ending_features,select_candidates,generate_group


class SettlingTests(unittest.TestCase):
    def notes(self):return [dict(start=0,end=400,pitch=60),dict(start=8100,end=9000,pitch=62)]

    def test_proxy_not_tonality(self):
        n=self.notes();f=ending_features(n)
        self.assertTrue(f['eligible']);self.assertEqual(f['last_gate_ticks'],900)
        self.assertTrue(ending_features([{**x,'pitch':x['pitch']+7} for x in n])['eligible'])

    def test_exact_thresholds_and_failures(self):
        n=[dict(start=0,end=100,pitch=60),dict(start=8064,end=8448,pitch=62)]
        self.assertTrue(ending_features(n)['eligible'])
        for change,reason in (({'start':8063},'last_onset_outside_final_three_quarters'),
                              ({'end':8447},'last_gate_shorter_than_quarter'),
                              ({'pitch':63},'final_onset_interval_above_two_semitones')):
            self.assertIn(reason,ending_features([n[0],{**n[1],**change}])['reasons'])
        self.assertIn('earlier_note_outlasts_last_onset',ending_features([{**n[0],'end':9000},n[1]])['reasons'])
        self.assertFalse(ending_features([])['eligible'])
        self.assertFalse(ending_features(n[:1])['eligible'])

    def test_selection_budget_and_failures_retained(self):
        rows=[dict(seed=i,status='complete',ending=dict(eligible=i==2)) for i in range(4)]
        result=select_candidates(rows);self.assertEqual(result['baseline_seed'],0);self.assertEqual(result['selected_seed'],2)
        rows[2]['status']='copy_guard_blocked'
        self.assertEqual(select_candidates(rows)['selected_status'],'no_eligible_candidate')
        self.assertEqual(len(rows),4)

    def test_all_four_fixed_seeds_no_early_stopping(self):
        notes=self.notes();result=dict(status='complete',notes=notes,rejections=0)
        with patch('mousa.settling_ending.generate_optimized',return_value=result) as mock:
            group=generate_group(object(),3)
        self.assertEqual([c.args[1] for c in mock.call_args_list],[12,13,14,15])
        self.assertEqual(group['baseline_seed'],12);self.assertEqual(group['selected_seed'],12)
        self.assertEqual(notes,self.notes())

    def test_copy_guard_precedes_selection(self):
        notes=[dict(start=i*100,end=i*100+80,pitch=60+i) for i in range(8)]
        with patch('mousa.settling_ending.generate_optimized',return_value=dict(status='complete',notes=notes,rejections=0)):
            group=generate_group(object(),0,source_pitches=[list(range(60,68))])
        self.assertTrue(all(r['status']=='copy_guard_blocked' for r in group['candidates']))
        self.assertIsNone(group['baseline_seed'])

    def test_bad_inputs(self):
        with self.assertRaises(ValueError):generate_group(object(),True)
        with self.assertRaises(ValueError):generate_group(object(),0,source_pitches=[[True]])
        with self.assertRaises(ValueError):ending_features([dict(start=2,end=1,pitch=60)])
        with self.assertRaises(ValueError):select_candidates([])


if __name__=='__main__':unittest.main()
