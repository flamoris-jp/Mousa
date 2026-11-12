"""No real source access: regression for skipped three-condition rows."""
import importlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

with patch.object(sys,'path',[str(Path(__file__).resolve().parents[1]/'tools'),*sys.path]):
    driver=importlib.import_module('compare_phrasewide_register_cycle44')

class Phrasewide44DriverTests(unittest.TestCase):
    def test_all_conditions_skipped_and_consumable(self):
        rows=[driver.cpu_skipped_row(seed) for seed in range(5)]
        self.assertEqual(driver.CONDITIONS,('control','nearest_octave','phrasewide'))
        for row in rows:
            self.assertEqual(set(row),{'seed','generation_status',*driver.CONDITIONS})
            self.assertTrue(all(row[k]['status']=='cpu_budget_skipped' for k in driver.CONDITIONS))
        common=[r['seed'] for r in rows if all(r[k]['status']=='complete' for k in driver.CONDITIONS)]
        self.assertEqual(common,[])
        for label in driver.CONDITIONS:
            self.assertEqual([r[label] for r in rows if r[label]['status']=='complete'],[])
            counts={s:sum(r[label]['status']==s for r in rows) for s in {r[label]['status'] for r in rows}}
            self.assertEqual(counts,{'cpu_budget_skipped':5})
        rows[0]['control']['status']='changed'
        self.assertEqual(rows[0]['phrasewide']['status'],'cpu_budget_skipped')
        self.assertEqual(rows[1]['control']['status'],'cpu_budget_skipped')

if __name__=='__main__':unittest.main()
