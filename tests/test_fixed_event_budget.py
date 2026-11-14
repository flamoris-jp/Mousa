import importlib.util
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
TOOLS=Path(__file__).resolve().parents[1]/'tools'
sys.path.insert(0,str(TOOLS))
try:
    spec=importlib.util.spec_from_file_location('budget_test',TOOLS/'compare_fixed_event_budget.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
finally:sys.path.pop(0)

class FixedEventBudgetTests(unittest.TestCase):
    def test_total_budget_and_inseparable_family(self):
        for allocation in module.ALLOCATIONS.values():
            self.assertEqual(sum(allocation.values()),60)
            self.assertEqual('mutopia-888' in allocation,'mutopia-889' in allocation)
        self.assertEqual(len(module.ALLOCATIONS),4)

    def test_original_prefix_and_no_replacement(self):
        notes=[SimpleNamespace(start=96+i*48,end=120+i*48,pitch=60+i) for i in range(5)]
        melody=SimpleNamespace(notes=notes,ppq=384)
        seqs,pitches=module.prefixes({'a':melody},{'a':3})
        self.assertEqual(seqs,[[(96,24),(48,24),(48,24)]])
        self.assertEqual(pitches,[[60,61,62]])
        self.assertEqual(len(melody.notes),5)
        with self.assertRaises(ValueError):module.prefixes({'a':melody},{'a':6})
