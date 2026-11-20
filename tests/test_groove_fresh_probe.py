import importlib.util
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
try:
    spec=importlib.util.spec_from_file_location('fresh_probe',ROOT/'tools/groove_fresh_recording_probe.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
finally:sys.path.pop(0)

class FreshProbeTests(unittest.TestCase):
    def test_fixed_selection_excludes_known_hashes_reserved_and_caps(self):
        rows=[]
        for drummer in ('drummer7','drummer8','drummer9','drummer10'):
            for i in range(6):rows.append(dict(id=f'{drummer}/{i}',sha256=str(i),drummer=drummer,session=f'{drummer}/session',metrics={'note_on_positive':4097 if i==5 else 10}))
        known=[dict(id='another-id',sha256='0')]
        rows.append(dict(id='eval',sha256='00',drummer='drummer7',session='drummer7/eval_session',metrics={'note_on_positive':10}))
        expected=[f'{d}/{i}' for d in ('drummer7','drummer8','drummer9','drummer10') for i in (1,2)]
        self.assertEqual([x['id'] for x in m.select(rows,known)],expected)
        self.assertEqual(m.select(rows,known),m.select(list(reversed(rows)),known))

    def test_strong_duplicate_and_weak_pattern_are_not_same(self):
        a=m.features([(i*120,36+i%2) for i in range(10)])
        b=m.features([(i*240,36+i%2) for i in range(10)])
        self.assertTrue(m.compare(a,b)['strong_unresolved'])
        c=m.features([(i*120,36+i%2) for i in range(8)]+[(960,50),(1080,51)])
        r=m.compare(a,c)
        self.assertGreater(r['shared_unique_windows'],0)
        self.assertFalse(r['strong_unresolved'])
