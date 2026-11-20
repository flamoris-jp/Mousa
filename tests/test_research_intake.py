import copy
import hashlib
from pathlib import Path
import tempfile
import unittest
from mousa.research_intake import validate_manifest, SCHEMA, RIGHTS


class ResearchIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        data = b'MThd' + b'original structural fixture'
        (self.root/'fixture.mid').write_bytes(data)
        self.work = dict(work_id='original-test', title='Fixture', author='Test generator',
            source_url='https://example.org/fixture', license='original test fixture', terms='unit tests only',
            acquired_at='2026-11-12T09:00:00Z', sha256=hashlib.sha256(data).hexdigest(),
            family_id='family-a', duplicate_group='group-a', source_kind='midi', file='fixture.mid',
            review_state='approved', training_allowed=True, split='train',
            rights={k:dict(training_allowed=True,basis='Original structural unit-test fixture, not an actual corpus',
                          evidence_url='https://example.org/fixture',reviewed_on='2026-11-12') for k in RIGHTS})
        self.manifest=dict(schema_version=SCHEMA, works=[self.work])

    def check(self): return validate_manifest(self.manifest,self.root)
    def reject(self):
        with self.assertRaises((ValueError,FileNotFoundError)): self.check()
    def test_valid_preflight(self): self.assertEqual(self.check()['counts']['train'],1)
    def test_pending_is_quarantined(self):
        self.work.update(review_state='pending',training_allowed=False,split=None)
        self.assertEqual(self.check()['counts']['quarantined'],1)
    def test_pending_cannot_train(self): self.work['review_state']='pending'; self.reject()
    def test_unknown_rights_rejected(self): self.work['rights']['midi_encoding']['training_allowed']=False; self.reject()
    def test_no_evidence_rejected(self): del self.work['rights']['composition']['evidence_url']; self.reject()
    def test_hash_tampering_rejected(self): (self.root/'fixture.mid').write_bytes(b'MThd altered'); self.reject()
    def test_source_path_escape_rejected(self): self.work['file']='../fixture.mid'; self.reject()
    def test_symlink_rejected(self):
        (self.root/'alias.mid').symlink_to(self.root/'fixture.mid'); self.work['file']='alias.mid'; self.reject()
    def test_same_bytes_rejected(self):
        w=copy.deepcopy(self.work); w['work_id']='other'; self.manifest['works'].append(w); self.reject()
    def test_cross_split_groups_rejected(self):
        for group in ('family_id','duplicate_group'):
            with self.subTest(group=group):
                w=copy.deepcopy(self.work); w.update(work_id='other',file='other.mid',split='test',family_id='b',duplicate_group='b')
                w[group]=self.work[group]; data=b'MThd second original fixture'; (self.root/'other.mid').write_bytes(data)
                w['sha256']=hashlib.sha256(data).hexdigest(); self.manifest['works']=[self.work,w]; self.reject()
    def test_stem_candidates_not_silently_accepted(self): self.work['source_kind']='audio_analyzer'; self.reject()
    def test_naive_timestamp_rejected(self): self.work['acquired_at']='2026-11-12T09:00:00'; self.reject()
    def test_header_is_not_full_parser(self):
        self.assertEqual(self.check()['counts']['train'],1)  # deliberately not valid SMF; parser remains separate
    def test_missing_author_rejected(self): del self.work['author']; self.reject()
    def test_bool_permission_not_integer(self): self.work['training_allowed']=1; self.reject()
