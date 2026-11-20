import importlib.util
from pathlib import Path
import unittest
s=importlib.util.spec_from_file_location('prep',Path(__file__).resolve().parents[1]/'experiments/maidionis-annotated-events/prepare.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
S='# tonic: C\n# metre: 4/4\n0\tA, | C:maj |\n20\tend\n'
class PrepareTests(unittest.TestCase):
 def test_codec_and_bass(self):
  e=m.events('0 1 C:maj/3\n1 2 D:min\n2 3 G:7',S);self.assertEqual([x['label'] for x in e],[0,17,60]);self.assertEqual(e[0]['bass'],'3');self.assertEqual(list(m.windows(e)),[(2,[1,2,19],60)])
 def test_bad_time(self):
  for lab in ['0 0 C:maj','2 1 C:maj','0 2 C:maj\n1 3 D:min','nan 2 C:maj']:
   with self.assertRaises(ValueError):m.events(lab,S)
 def test_breaks(self):
  for middle in ['N','X','C:maj9','C:maj(9)']:
   e=m.events(f'0 1 C:maj\n1 2 {middle}\n2 3 D:min\n3 4 G:7',S);self.assertEqual(list(m.windows(e)),[])
  self.assertEqual(list(m.windows(m.events('0 1 C:maj\n2 3 D:min\n3 4 G:7',S))),[])
 def test_coalesce_exact(self):
  e=m.events('0 1 C:maj\n1 2 C:maj\n2 3 C:maj/3',S);self.assertEqual(len(e),2);self.assertEqual(e[0]['source_lines'],[0,1])
 def test_context(self):
  s='# tonic: C\n# metre: 4/4\n0 A\n# tonic: D\n2 B\n10 end'
  self.assertEqual(list(m.windows(m.events('0 1 C:maj\n1 2 D:min\n2 3 G:7',s))),[])
  self.assertIsNone(m.events('0 3 C:maj',s)[0]['label'])
 def test_inline_and_unknown(self):
  for s in [S.replace('4/4','?'),S.replace('tonic: C','tonic: ?'),S.replace('| C:maj |','| (2/4) C:maj |')]:self.assertIsNone(m.events('0 1 C:maj',s)[0]['label'])

 def test_mixed_accidentals_rejected(self):
  for root in ['C#b','Db#','G#b']:
   self.assertIsNone(m.pc(root))
   self.assertIsNone(m.events(f'0 1 {root}:maj',S)[0]['label'])
   self.assertIsNone(m.events('0 1 C:maj',S.replace('tonic: C','tonic: '+root))[0]['label'])
  self.assertEqual(m.pc('C##'),2)
  self.assertEqual(m.pc('Dbb'),0)
 def test_protocol_contract_rejected_before_intake(self):
  import json,tempfile
  proto=json.loads(Path(m.__file__).with_name('protocol.json').read_text())
  for field,value in [('context',True),('context',8),('quality_order',list(reversed(m.Q))),('task_id','other'),('training_schema','other')]:
   with tempfile.TemporaryDirectory() as td:
    root=Path(td);p=root/'protocol.json';p.write_text(json.dumps({**proto,field:value}))
    with self.assertRaises(AssertionError):m.prepare(root,root/'out',p)
    self.assertFalse((root/'out').exists())
