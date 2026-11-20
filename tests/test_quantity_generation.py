import importlib.util
from pathlib import Path
import sys
import unittest
TOOLS=Path(__file__).resolve().parents[1]/'tools';sys.path.insert(0,str(TOOLS))
try:
    spec=importlib.util.spec_from_file_location('quantity_generation_test',TOOLS/'compare_quantity_generation.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
finally:sys.path.pop(0)


class QuantityGenerationTests(unittest.TestCase):
    def test_all_single_families_plusfull_fixed(self):
        specs=module.generation_specs()
        self.assertEqual([name for name,works in specs],['family0','family1','family2','full'])
        self.assertEqual([len(works) for name,works in specs],[1,2,1,4])
        self.assertEqual(sum(len(range(5)) for _ in specs),20)
        for _,works in specs:
            self.assertEqual('mutopia-888' in works,'mutopia-889' in works)
            self.assertFalse({'mutopia-580','mutopia-640'}&set(works))

    def test_skip_budget_rows_not_in_success_summary(self):
        rows=[dict(status='skipped_cpu_budget',seed=0),dict(status='complete',metrics={'notes':4,'interval':None})]
        means,den=module.summarize(rows)
        self.assertEqual(means,{'notes':4,'interval':None});self.assertEqual(den,{'notes':1,'interval':0})


if __name__=='__main__':unittest.main()
