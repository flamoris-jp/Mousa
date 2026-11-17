import importlib.util,sys
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]/'experiments/maidionis-progression-corpus'
sys.path.insert(0,str(ROOT));spec=importlib.util.spec_from_file_location('progression_prepare',ROOT/'prepare.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class PrepareTests(unittest.TestCase):
    def test_null_break(self):
        bars=[{'measure_index':i,'label':None if i==9 else i%14} for i in range(20)]
        rows=list(m.windows(bars));self.assertEqual([r[0] for r in rows],[8,18,19]);self.assertEqual(rows[1][1],[1]+[i%14+2 for i in range(10,18)])
    def test_context2_and_invalid_contexts(self):
        bars=[{'measure_index':i,'label':None if i==3 else i%14} for i in range(8)]
        rows=list(m.windows(bars,2));self.assertEqual([r[0] for r in rows],[2,6,7]);self.assertEqual(rows[1][1],[1,6,7])
        for value in (1,3,True,'2'):
            with self.assertRaises(ValueError):list(m.windows(bars,value))
    def test_work_normalization(self):
        self.assertEqual(m.work_key('scores/Schubert,_Franz/Op.1/1_Name,_D.118'),m.work_key('scores/Schubert,_Franz/Other/2_Other,_D.118'))
        self.assertEqual(m.work_key('scores/Brahms,_Johannes/Op.1/1_Mädchen'),m.work_key('scores/Brahms,_Johannes/Op.2/2_Madchen'))
    def test_union_closure(self):
        rows=[{'family_id':'a','sha256':'x','work_key':'one'},{'family_id':'b','sha256':'x','work_key':'two'},{'family_id':'c','sha256':'y','work_key':'two'}]
        mapping,groups,links=m.close_families(rows);self.assertEqual(len(groups),1);self.assertEqual(len(set(mapping.values())),1)
    def test_frozen_split(self):
        a=m.split_families([str(i) for i in range(22)]);b=m.split_families([str(i) for i in reversed(range(22))]);self.assertEqual(a,b);self.assertEqual(list(a.values()).count('test'),5)
