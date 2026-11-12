import copy
import hashlib
import json
import unittest
from test_semantic_evidence import fictional_record
from mousa.synthetic_evidence_binding import bind


def bound_fixture(kind='observed-source'):
    record=fictional_record(kind,'bound-toy')
    source=b'Invented symbolic fixture source, not a real work or listener.'
    artifact=json.dumps(dict(synthetic=True,ppq=384,total_ticks=768,notes=[
        dict(start=0,end=96,pitch=60),dict(start=48,end=192,pitch=64),dict(start=300,end=500,pitch=67)])).encode()
    record['source']['sha256']=hashlib.sha256(source).hexdigest()
    record['artifact']['sha256']=hashlib.sha256(artifact).hexdigest()
    return record,source,artifact


class SyntheticBindingTests(unittest.TestCase):
    def test_hash_binding_union_and_boundary(self):
        r,s,a=bound_fixture();original=copy.deepcopy(r)
        result=bind(r,s,a)
        self.assertEqual(result['measurements'],dict(scope_ticks=384,sounding_ticks=276,rest_ticks=108,onsets_in_scope=3,distinct_sounding_pitches=3))
        self.assertEqual(r,original);self.assertFalse(result['training_eligible'])
        r['segment'].update(start_tick=96,end_tick=300)
        result=bind(r,s,a)
        self.assertEqual(result['measurements']['onsets_in_scope'],0)
        self.assertEqual(result['measurements']['sounding_ticks'],96)

    def test_tampered_bytes_or_scope_fail(self):
        r,s,a=bound_fixture()
        for source,artifact in ((s+b'x',a),(s,a+b' ')):
            with self.assertRaisesRegex(ValueError,'digest mismatch'):bind(r,source,artifact)
        r['segment']['ppq']=480
        with self.assertRaisesRegex(ValueError,'scope/clock'):bind(r,s,a)

    def test_bound_hypotheses_and_fictional_reports_are_not_truth_or_consent(self):
        for kind in ('observed-source','human-report','hypothesis'):
            r,s,a=bound_fixture(kind);r['review']['state']='approved'
            result=bind(r,s,a)
            for field in ('wording_verified','origin_or_actor_verified','consent_verified','training_eligible'):
                self.assertFalse(result[field])

    def test_malformed_rehashed_fixture_still_rejected(self):
        r,s,a=bound_fixture();data=json.loads(a);data['notes'][0]['pitch']=True
        a=json.dumps(data).encode();r['artifact']['sha256']=hashlib.sha256(a).hexdigest()
        with self.assertRaisesRegex(ValueError,'note fields'):bind(r,s,a)
