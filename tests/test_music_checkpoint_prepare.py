import importlib.util
from pathlib import Path
import tempfile
import unittest
P=Path(__file__).resolve().parents[1]/'experiments/maidionis-music-checkpoint/prepare.py'
s=importlib.util.spec_from_file_location('music_checkpoint_prepare',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

class MusicCheckpointPrepareTests(unittest.TestCase):
    def test_token_mapping(self):
        rows=m.task_rows([0]*8+[48],[24]*8+[0],[8],'f','train')
        self.assertEqual(rows[0]['input'],[1]+[3,76]*8)
        self.assertEqual(rows[1]['input'],[2]+[3,76]*8)
        self.assertEqual([r['label'] for r in rows],[48,0])
    def test_no_target_or_future_leakage(self):
        a=m.task_rows(list(range(12)),list(range(12)),[8],'f','train')
        pitch=list(range(12));rhythm=list(range(12));pitch[8:]=[40]*4;rhythm[8:]=[20]*4
        b=m.task_rows(pitch,rhythm,[8],'f','train')
        self.assertEqual([r['input'] for r in a],[r['input'] for r in b])
        self.assertNotEqual([r['label'] for r in a],[r['label'] for r in b])
    def test_invalid_labels(self):
        for p,r in [([49]*9,[0]*9),([0]*9,[25]*9),([True]*9,[0]*9)]:
            with self.assertRaises(ValueError):m.task_rows(p,r,[8],'f','train')
    def test_invalid_windows(self):
        for indices in ([7],[9],[8,8]):
            with self.assertRaises(ValueError):m.task_rows([0]*9,[0]*9,indices,'f','train')
        with self.assertRaises(ValueError):m.task_rows([0]*9,[0]*8,[8],'f','train')
    def test_split(self):
        train=m.task_rows([0]*9,[0]*9,[8],'f','train')
        test=m.task_rows([0]*9,[0]*9,[8],'f','historical_observed')
        with self.assertRaisesRegex(ValueError,'overlap'):m.validate_split(train,test)
    def test_schedule(self):
        schedules=m.schedules(8168)
        self.assertEqual(schedules,m.schedules(8168))
        for epoch,x in enumerate(schedules):
            self.assertEqual(x['seed'],42+epoch);self.assertEqual(len(x['batches']),256)
            self.assertEqual(len(x['batches'][-1]),8)
            self.assertEqual(sorted(i for b in x['batches'] for i in b),list(range(8168)))
        self.assertNotEqual(schedules[0]['batches'],schedules[1]['batches'])
    def test_refuse_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'output must not exist'):m.prepare(None,None,None,Path(tmp))
