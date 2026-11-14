import importlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
with patch.object(sys,'path',[str(Path(__file__).resolve().parents[1]/'tools'),*sys.path]):
    d=importlib.import_module('evaluate_dvorak_cycle48')
class Cycle48Tests(unittest.TestCase):
    def test_fixed_conditions(self):
        self.assertEqual(len(d.CONDITIONS),6)
        self.assertEqual({n for _,n,_ in d.CONDITIONS},{17,18})
        self.assertEqual(d.MASSES,(17,3411,3428))
    def test_supplement_fail_closed(self):
        for x in ({'exact8':1,'global_similarity':0},{'exact8':0,'global_similarity':.8},{'exact8':0,'global_similarity':None}):self.assertTrue(d.blocked(x))
        self.assertFalse(d.blocked({'exact8':0,'global_similarity':.79}))
    def test_synthetic_metric(self):
        seq=[(0,60,((0,96,80,0),)),(96,62,((0,96,80,0),)),(192,64,((0,96,80,0),))]
        m=d.WeightedGroupModel([seq],['synthetic'],masses=d.MASSES)
        r=d.timing_metrics(m,seq)
        self.assertEqual(r['later_groups'],2);self.assertAlmostEqual(r['later_mean_nll']*2,r['later_nll_sum'])
        self.assertLess(r['independent_error'],1e-12)
    def test_clearance_before_input(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'plan').write_text('{}');(p/'clearance').write_text('{}')
            with patch.object(d,'inputs',side_effect=AssertionError('no read')):
                with self.assertRaises(ValueError):d.run(p/'plan',p/'clearance',p/'out')
            self.assertFalse((p/'out').exists())
    def test_malformed_supplement_blocks(self):
        for x in ({}, {'global_similarity':0}, {'exact8':-1,'global_similarity':0}, {'exact8':True,'global_similarity':0}, {'exact8':0,'global_similarity':float('nan')}, {'exact8':0,'global_similarity':float('inf')}, {'exact8':0,'global_similarity':-0.1}, {'exact8':0,'global_similarity':1.1}):self.assertTrue(d.blocked(x))
    def test_counter_masses(self):
        seq=[(0,60,((0,96,80,0),)),(96,62,((0,96,80,0),))]
        m=d.WeightedGroupModel([seq],['synthetic'],masses=d.MASSES)
        self.assertEqual([x['numerator'] for x in d.verify_model_mass(m)],[17,3411,3428,3428])
        m.later[96]+=1
        with self.assertRaises(ValueError):d.verify_model_mass(m)
    def test_condition_guard(self):
        train={str(i):None for i in range(18)};maps={n:{k:'f' for k in list(train)[:n]} for n in (17,18)}
        cfg=dict(label='17_raw',train_ids=list(train)[:17],families=['f']*17,mode='raw',masses=list(d.MASSES))
        d.verify_config(cfg,train,maps)
        for key,value in [('train_ids',list(train)),('families',['other']*17),('masses',[18,3411,3428])]:
            with self.assertRaises(ValueError):d.verify_config({**cfg,key:value},train,maps)
    def test_all_blocked_report(self):
        p={'conditions':[{'label':x[0]} for x in d.CONDITIONS]}
        r=d.supplemental_stop(p,'hash','supplemental_failed',d.process_time())
        self.assertEqual(r['plan_sha256'],'hash');self.assertEqual(len(r['results']),6)
        self.assertFalse(r['prediction_attempted']);self.assertTrue(all(x['status']=='blocked' for x in r['results'].values()))
    def test_support_no_clipping(self):
        t=((0,96,80,0),)
        d.check_support([(65536,60,t),(12288,60,t)])
        for seq in ([(65537,60,t)],[(0,60,t),(12289,60,t)],[(0,60,t),(0,60,t)]):
            with self.assertRaises(ValueError):d.check_support(seq)
    def test_journal_fsync(self):
        with tempfile.TemporaryDirectory() as td,patch.object(d.os,'fsync') as fs:
            p=Path(td)/'journal';d.journal(p,'prediction_attempt',irreversibly_observed=True)
            self.assertTrue(json.loads(p.read_text())['irreversibly_observed']);fs.assert_called_once()
    def test_new_directory_only(self):
        with tempfile.TemporaryDirectory() as td,patch.object(d,'inputs',side_effect=AssertionError('no read')):
            with self.assertRaises(ValueError):d.prepare(Path(td))
if __name__=='__main__':unittest.main()
