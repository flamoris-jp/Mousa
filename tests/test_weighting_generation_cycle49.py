import importlib,sys,unittest,tempfile,json
from pathlib import Path
from unittest.mock import patch
with patch.object(sys,'path',[str(Path(__file__).resolve().parents[1]/'tools'),*sys.path]):d=importlib.import_module('generate_weighting_cycle49')
class Generation49Tests(unittest.TestCase):
 def test_seed_audit_scope(self):
  self.assertEqual(len(d.seed_records({'seeds':[49000,49011,42]})),2)
  self.assertEqual(d.seed_records({'value':49000}),[])
 def test_same_pitches_different_timing_not_exact(self):
  a=dict(notes=[dict(start=0,end=96,pitch=60,velocity=80)],groups=[])
  b=dict(notes=[dict(start=96,end=192,pitch=60,velocity=80)],groups=[])
  self.assertFalse(d.diversity(a,b)['exact_canonical_note_events_equal']);self.assertIsNone(d.diversity(a,b)['anchor3gram_jaccard'])
 def test_dynamics_part_of_exact_descriptor(self):
  a=dict(notes=[dict(start=0,end=96,pitch=60,velocity=80)],groups=[]);b=dict(notes=[dict(start=0,end=96,pitch=60,velocity=81)],groups=[])
  self.assertFalse(d.diversity(a,b)['exact_canonical_note_events_equal'])
 def test_empty_density(self):
  r=d.density([],{});self.assertIsNone(r['first_onset']);self.assertIsNone(r['notes_per_quarter_postfirst'])
 def test_leading_rest_denominator(self):
  r=d.density([dict(start=7872,pitch=60)],{});self.assertEqual(r['postfirst_available_ticks'],1344)
 def test_clearance_before_sources(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/'plan').write_text('{}');(p/'clearance').write_text('{}')
   with patch.object(d,'inputs',side_effect=AssertionError('no read')):
    with self.assertRaises(ValueError):d.run(p/'plan',p/'clearance',p/'out')
   self.assertFalse((p/'out').exists())
 def test_prepare_new_directory(self):
  with tempfile.TemporaryDirectory() as td,patch.object(d,'inputs',side_effect=AssertionError('no read')):
   with self.assertRaises(ValueError):d.prepare(Path(td))
if __name__=='__main__':unittest.main()
