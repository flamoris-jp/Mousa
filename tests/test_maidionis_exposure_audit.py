import importlib.util
from pathlib import Path
import unittest

P=Path(__file__).resolve().parents[1]/'experiments/maidionis-exposure-audit/audit.py'
spec=importlib.util.spec_from_file_location('exposure_audit',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def row(index,label=1,family='train'):
    return {'family':family,'target_index':index,'input':[1]+[3]*8,'label':label}

class ExposureAuditTests(unittest.TestCase):
    def test_exposure_multiplicity_and_unique(self):
        arm={'train':[row(0),row(1,2)],'batches':[[0]*31+[1]]*100}
        ex=m.exposures(arm)
        self.assertEqual(len(ex['sampled_3200_with_multiplicity']),3200)
        self.assertEqual(len(ex['sampled_unique_windows_only']),2)
        self.assertEqual(sum(r['label']==2 for r in ex['sampled_3200_with_multiplicity']),100)
    def test_invalid_indices_and_duplicates(self):
        for arm in [{'train':[row(0)],'batches':[[1]*32]*100},
                    {'train':[row(0),row(0)],'batches':[[0]*32]*100},
                    {'train':[row(0)],'batches':[[True]*32]*100}]:
            with self.assertRaises(ValueError):m.exposures(arm)
    def test_smoothing_and_backoff(self):
        fitted=m.fit([row(0),row(1,2)])
        p=m.predict(fitted,row(3),'unigram')
        self.assertAlmostEqual(p[1],(1+1/49)/3)
        t=m.predict(fitted,row(3),'trigram')
        self.assertAlmostEqual(t[1],(1+4*(1+4*p[1])/6)/6)
        self.assertAlmostEqual(sum(t),1)
    def test_macro_not_pooled(self):
        a=m.aggregate([{'family':'a','nll':1,'correct':1}]*3+[{'family':'b','nll':3,'correct':0}])
        self.assertEqual(a['family_macro_nll'],2)
        self.assertEqual(a['family_macro_accuracy'],.5)
    def test_test_train_overlap_rejected(self):
        arm={'condition':'x','seed':1,'train':[row(0)],'batches':[[0]*32]*100}
        with self.assertRaises(ValueError):m.audit({'test':[row(1)],'arms':[arm]}, {'runs':[{'condition':'x','seed':1}]})
    def test_mismatched_prediction_labels_rejected(self):
        arm={'condition':'x','seed':1,'train':[row(0)],'batches':[[0]*32]*100}
        run={'condition':'x','seed':1,'final_test':[{'family':'test','target_index':1,'target':4}]}
        with self.assertRaises(ValueError):m.audit({'test':[row(1,family='test')],'arms':[arm]}, {'runs':[run]})

if __name__=='__main__': unittest.main()
