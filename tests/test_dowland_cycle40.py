import unittest
from mousa.gate_context_group_model import GateContextGroupModel,ARMS
from mousa.initial_rest_group_model import validate
class DowlandPreflight(unittest.TestCase):
    def test_evaluation_does_not_fit(self):
        train=[[(0,60,((0,768,127,64),)),(768,62,((0,384,127,64),))]]*17
        candidate=[(768,71,((0,576,127,64),)),(576,72,((0,192,127,64),))]
        for arm in ARMS:
            m=GateContextGroupModel(train,arm=arm);before=(dict(m.first),dict(m.later),dict(m.templates));v=m.evaluate(candidate)
            self.assertEqual(v['groups'],2);self.assertEqual(before,(dict(m.first),dict(m.later),dict(m.templates)))
    def test_outside_support_rejected(self):
        with self.assertRaises(ValueError):validate([(65537,60,((0,1,90,0),))],65536)
