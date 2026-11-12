import importlib.util
from pathlib import Path
import sys
import unittest
TOOLS=Path(__file__).resolve().parents[1]/'tools'
sys.path.insert(0,str(TOOLS))
try:
    spec=importlib.util.spec_from_file_location('seed_robustness_test',TOOLS/'compare_new_seed_robustness.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
finally:sys.path.pop(0)

class RobustnessTests(unittest.TestCase):
    def test_seed_audit_only_explicit_fields(self):
        self.assertEqual(m.used_seeds({'notes':100,'a':[{'seed':101},{'seeds':[1,102,True]}]}),{101,1,102})

    def test_interaction_and_success_intersection(self):
        cells={k:{'outputs':[dict(seed=100,status='complete',metrics={x:v for x in m.METRICS}),dict(seed=101,status='blocked')]} for k,v in zip(m.CELLS,[1,3,4,9])}
        result=m.contrasts(cells)
        self.assertEqual(result['common_complete_seeds'],[100])
        self.assertEqual(result['metrics']['notes']['mean'],3)
        cells[m.CELLS[0]]['outputs'][0]['metrics']['notes']=None
        self.assertIsNone(m.contrasts(cells)['metrics']['notes']['mean'])
        cells[m.CELLS[0]]['outputs']=[]
        self.assertEqual(m.contrasts(cells)['common_complete_seeds'],[])

if __name__=='__main__':unittest.main()
