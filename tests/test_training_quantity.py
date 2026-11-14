import importlib.util
from pathlib import Path
import sys
import unittest
TOOLS=Path(__file__).resolve().parents[1]/'tools'
sys.path.insert(0,str(TOOLS))
try:
    spec=importlib.util.spec_from_file_location('quantity_test',TOOLS/'compare_training_quantity.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
finally:sys.path.pop(0)

class QuantityPlanTests(unittest.TestCase):
    def test_all_subsets_and_family_siblings_kept_together(self):
        rows=module.subsets()
        self.assertEqual([sum(row[0]==n for row in rows) for n in (1,2,3)],[3,3,1])
        for count,indexes,works in rows:
            self.assertEqual(count,len(indexes)); self.assertEqual(len(works),len(set(works)))
            self.assertEqual('mutopia-888' in works,'mutopia-889' in works)
            self.assertNotIn('mutopia-580',works);self.assertNotIn('mutopia-640',works)
        self.assertEqual(len(rows[-1][2]),4)
