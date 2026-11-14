import importlib,sys,unittest
from pathlib import Path
from unittest.mock import patch
with patch.object(sys,'path',[str(Path(__file__).resolve().parents[1]/'tools'),*sys.path]):d=importlib.import_module('diagnose_weighting_cycle49')
class Diagnosis49Tests(unittest.TestCase):
 def rows(self):
  return [dict(seed=s,status='complete',metrics=dict(notes=n,distinct_pitches=n,mean_abs_pitch_interval=1,above_octave_fraction=0),timeline=dict(silence_ticks=0,leading_silence_ticks=0),attempts=1) for s,n in zip(d.SEEDS,[2,3,10])]
 def test_distribution_not_mean_only(self):
  r=d.summarize(self.rows())['notes'];self.assertEqual(r,dict(n=3,mean=5,median=3,minimum=2,maximum=10))
 def test_missing_or_failed_not_dropped(self):
  with self.assertRaises(ValueError):d.summarize(self.rows()[:2])
  rows=self.rows();rows[1]['status']='blocked'
  with self.assertRaises(ValueError):d.summarize(rows)
 def test_wrong_seed_not_fresh(self):
  rows=self.rows();rows[0]['seed']=0
  with self.assertRaises(ValueError):d.summarize(rows)
if __name__=='__main__':unittest.main()
