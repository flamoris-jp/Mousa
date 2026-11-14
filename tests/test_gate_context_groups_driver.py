import unittest
import sys
from pathlib import Path
old=list(sys.path)
try:
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
    from compare_gate_context_groups import preflight
finally:sys.path[:]=old


class GateDriverTests(unittest.TestCase):
    def test_actual_count_preflight(self):
        self.assertEqual(preflight(),dict(conditions=4,works=17,real_sources_fitted=False))


if __name__=='__main__':unittest.main()
