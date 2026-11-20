import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from corpus_learning_trial import MusicFeatureCounts, project_events

class CorpusLearningTests(unittest.TestCase):
    def test_projection_exact_onset(self):
        seq,n,points=project_events([(0,60),(0,64),(480,67),(960,64),(1440,60)],480)
        self.assertEqual(points[0],(0,64));self.assertEqual(n,4)
        self.assertEqual(seq['pitch_interval'],[27,21,20])
        self.assertEqual(seq['rhythm_ioi'],[12,12,12])
    def test_uniform_support(self):
        m=MusicFeatureCounts([],49,2)
        self.assertAlmostEqual(sum(m.distribution([1,2])),1)
        self.assertAlmostEqual(m.distribution([1,2])[3],1/49)
    def test_no_boundary_transition(self):
        m=MusicFeatureCounts([[0,0],[1,1]],2,1)
        self.assertNotIn(1,m.local[0][(0,)])
    def test_learns_context(self):
        seq=[0,1]*30
        m=MusicFeatureCounts([seq],2,1);u=MusicFeatureCounts([seq],2,0)
        self.assertLess(m.score(seq)['nll'],u.score(seq)['nll'])
    def test_deterministic_shuffle_preserves_marginal(self):
        a=MusicFeatureCounts([[0,1,1,2]*10],3,2,17)
        b=MusicFeatureCounts([[0,1,1,2]*10],3,2,17)
        self.assertEqual(a.local,b.local);self.assertEqual(a.marginal,{0:10,1:20,2:10})
    def test_closed_form_backoff(self):
        m=MusicFeatureCounts([[0,1,0]],2,1)
        expected=(1+4*((1+.5)/4))/(1+4)
        self.assertAlmostEqual(m.distribution([0])[1],expected)
    def test_clips(self):
        s,_,_=project_events([(0,0),(1,127),(100000,0),(100001,127)],480)
        self.assertEqual(s['pitch_interval'],[48,0,48]);self.assertTrue(all(0<=i<25 for i in s['rhythm_ioi']))


from run_corpus_learning_trial import allocate_prefixes, prepare, run, aggregate
import tempfile
import json
import hashlib

class CorpusRunnerSafetyTests(unittest.TestCase):
    def test_prefix_budget_boundaries(self):
        seqs=[[1,2,3,4],[7,8],[9,0,1]]
        result=allocate_prefixes(seqs,5)
        self.assertEqual(result,[[1,2],[7,8],[9]])
        self.assertEqual(sum(map(len,result)),5)
        self.assertEqual(allocate_prefixes(seqs,100),seqs)
    def test_metric_denominators(self):
        r=aggregate([{'n':1,'nll':2.,'nll_sum':2.,'accuracy':1.,'correct':1},
                     {'n':3,'nll':4.,'nll_sum':12.,'accuracy':0.,'correct':0}])
        self.assertEqual(r['family_macro_nll'],3.);self.assertEqual(r['pooled_nll'],3.5)
    def reject(self,mutate_split=None,mutate_plan=None,reason=""):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);src=p/'source.mid';src.write_bytes(b'not MIDI')
            rec={'family_id':'one','source_path':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
                 'split':'train','previously_seen_source_ids':[],'corpus':'pd','nested_18_family_training_subset':False}
            split={'members':[rec],'input_sha256':{},'input_paths':{}}
            if mutate_split:mutate_split(split)
            sp=p/'split.json';sp.write_text(json.dumps(split));plan=p/'plan.json';prepare(sp,plan)
            if mutate_plan:
                d=json.loads(plan.read_text());mutate_plan(d);plan.write_text(json.dumps(d))
            with self.assertRaisesRegex(ValueError,reason):run(sp,plan,p/'out')
    def test_wrong_file_hash(self):self.reject(lambda s:s['members'][0].update(sha256='0'*64),reason='source hash mismatch')
    def test_sa_rejected(self):self.reject(lambda s:s['members'][0].update(corpus='sa'),reason='unapproved license family')
    def test_old_observation_heldout_rejected(self):
        self.reject(lambda s:s['members'][0].update(split='test',previously_seen_source_ids=['old']),reason='prior observation leaked')
    def test_unknown_role_rejected(self):self.reject(lambda s:s['members'][0].update(split='maybe'),reason='split invariant')
    def test_changed_protocol(self):self.reject(mutate_plan=lambda p:p.update(max_onsets_per_family=20000),reason='protocol parameters changed')
    def test_changed_manifest(self):self.reject(mutate_plan=lambda p:p.update(split_sha256='0'*64),reason='split changed')
    def test_projection_too_short(self):
        seq,n,_=project_events([(0,60),(480,62)],480)
        self.assertLess(len(seq['pitch_interval']),3)
    def test_projection_cap(self):
        seq,n,pts=project_events([(i,60) for i in range(3000)],480)
        self.assertEqual(n,3000);self.assertEqual(len(pts),2048);self.assertEqual(len(seq['pitch_interval']),2047)

    def test_duplicate_family_rejected(self):self.reject(lambda s:s['members'].append(dict(s['members'][0])),reason='duplicate family')

if __name__=='__main__':unittest.main()
