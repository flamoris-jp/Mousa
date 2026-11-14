import importlib.util
from pathlib import Path
import sys
import unittest
TOOLS=Path(__file__).resolve().parents[1]/'tools';sys.path.insert(0,str(TOOLS))
try:
    spec=importlib.util.spec_from_file_location('augment_test',TOOLS/'compare_cornelius_augmentation.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
finally:sys.path.pop(0)

class AugmentationRolesTests(unittest.TestCase):
    def test_related_family_excluded_and_observed_targets_fixed(self):
        good={'related_evaluation_exclusions':['mutopia-580'],'diagnostic_ids':['mutopia-640','mutopia-921'],'source_sha256':m.EXTRA_SHA}
        m.validate_roles(good)
        for replacement in ({'related_evaluation_exclusions':[]},{'diagnostic_ids':['mutopia-580','mutopia-921']},{'source_sha256':'bad'}):
            with self.assertRaises(ValueError):m.validate_roles(dict(good,**replacement))
