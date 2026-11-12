import copy
import unittest
from mousa.semantic_evidence import validate, training_eligible, summarize


def fictional_record(kind='observed-source', identifier='toy-1'):
    """Entire record is invented; no actual listener or source is represented."""
    perspective, role, wording = {
        'observed-source': ('symbolic-measurement', 'synthetic-observer', 'Fictional example: a rest spans 384 ticks.'),
        'human-report': ('cannot-judge', 'fictional-listener', 'Fictional role-play only: I cannot judge this invented clip.'),
        'hypothesis': ('interpretation', 'synthetic-researcher', 'Synthetic hypothesis: this rest might divide two phrases.')
    }[kind]
    return dict(id=identifier, source=dict(sha256='0'*64, kind='synthetic'),
                artifact=dict(sha256='1'*64, kind='synthetic'),
                segment=dict(track=1, start_tick=0, end_tick=384, ppq=384,
                             artifact_total_ticks=768, render_ref='fictional-render-settings-120bpm'),
                evidence=dict(kind=kind, perspective=perspective, wording=wording,
                              language='en', proposed_tag=None),
                provenance=dict(fictional=True, actor_role=role, reference='invented-fixture-not-a-conversation'),
                review=dict(state='pending', reference=None), permitted_use='synthetic-schema-test')


class SemanticEvidenceTests(unittest.TestCase):
    def test_layers_and_original_unchanged(self):
        records=[fictional_record(k,k) for k in ('observed-source','human-report','hypothesis')]
        original=copy.deepcopy(records)
        for r in records:
            validate(r); self.assertFalse(training_eligible(r))
        result=summarize(records)
        self.assertEqual(result['accepted'],3)
        self.assertEqual(result['actual_human_reports'],0)
        self.assertEqual(records,original)

    def test_approved_string_not_authority(self):
        for state in ('missing','pending','rejected','approved'):
            r=fictional_record('human-report');r['review']['state']=state
            r['review']['reference']='fictional-review-string-not-verified-consent'
            self.assertFalse(training_eligible(r))
        r['permitted_use']='train'
        with self.assertRaisesRegex(ValueError,'unsupported_use'): validate(r)

    def test_invalid_boundaries_types_and_provenance(self):
        cases=[('segment','start_tick',True),('segment','end_tick',769),
               ('segment','ppq',0),('segment','end_tick',0),
               ('provenance','fictional',False),('provenance','actor_role','real-listener'),
               ('evidence','perspective','perception'),('source','sha256','not-digest'),
               ('evidence','kind','unknown'),('review','state','consented')]
        for section,key,value in cases:
            with self.subTest(section=section,key=key,value=value):
                r=fictional_record();r[section][key]=value
                with self.assertRaises(ValueError):validate(r)
        r=fictional_record('human-report');r['segment']['render_ref']=None
        with self.assertRaisesRegex(ValueError,'missing_audition_scope'):validate(r)

    def test_no_silent_promotion_or_replacement(self):
        r=fictional_record('hypothesis');r['evidence']['kind']='human-report'
        with self.assertRaises(ValueError):validate(r)
        r=fictional_record('human-report');r['evidence']['proposed_tag']='uncertain'
        original=r['evidence']['wording'];validate(r)
        self.assertEqual(r['evidence']['wording'],original)

    def test_descriptive_rejections_and_bound(self):
        r=fictional_record();bad=copy.deepcopy(r);bad['extra']='not allowed'
        result=summarize([r,r,bad,None])
        self.assertEqual(result['accepted'],1);self.assertEqual(result['rejected'],3)
        self.assertEqual(result['rejection_counts'],{'duplicate_id':1,'schema_fields':2})
        self.assertEqual(result['training_eligible'],0)
        with self.assertRaises(ValueError):summarize([r]*1001)
        self.assertEqual(summarize([])['accepted'],0)


if __name__=='__main__':unittest.main()
