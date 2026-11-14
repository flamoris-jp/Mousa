import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('satie47',Path(__file__).resolve().parents[1]/'tools/audit_satie37_cycle47.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Event:
    def __init__(self,velocity,time=0):
        self.type='note_on';self.velocity=velocity;self.time=time;self.channel=0;self.note=66
    def dict(self):return vars(self).copy()
class AuditTests(unittest.TestCase):
    def test_redundancy(self):
        events,removed=m.audit_track([Event(60),Event(0,10),Event(0)], [2],10,0,66)
        self.assertEqual(len(removed),1);self.assertEqual(events[-1][0],10)
    def test_fail_closed(self):
        for events,indices in [([Event(60),Event(60),Event(0)],[2]),([Event(60),Event(0,10)],[1]),([Event(0)],[]),([Event(60)],[])]:
            with self.assertRaises(ValueError):m.audit_track(events,indices,10,0,66)
    def test_wrong_location(self):
        with self.assertRaises(ValueError):m.audit_track([Event(0,11)],[0],10,0,66)
