"""Report matched-arm conditional predictions and descriptive free-run results."""
import argparse,json,hashlib
from pathlib import Path
from collections import Counter
p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--fits',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
result={'schema':'mousa.rhythm-first-results.experimental.v1','oracle_timing_degree_evaluation':True,'historical_observed_not_fresh':True,'human_listening':False,'arms':{}}
checks=[]
for arm in ('independent','rhythm_first'):
    d=json.loads((a.data/(arm+'.json')).read_text());r=json.loads((a.fits/arm/'results.json').read_text());m=json.loads((a.fits/arm/'manifest.json').read_text());rows=[]
    for task,name in enumerate(['degree','ioi','duration','rest','accent','phrase']):
        train=[x['label'] for x in d['train'] if x['task']==task];test=[x['label'] for x in d['test'] if x['task']==task];major=Counter(train).most_common(1)[0][0]
        x={'task':name,'train_windows':len(train),'evaluation_windows':len(test),'majority_accuracy':test.count(major)/len(test)}
        for key in ('initial_test','final_test'):
            scores=[v for v in r[key] if v['task']==task];x[key]={'nll':sum(v['nll'] for v in scores)/len(scores),'accuracy':sum(v['prediction']==v['target'] for v in scores)/len(scores)}
        rows.append(x)
    result['arms'][arm]={'metrics':rows,'cpu_seconds':r['cpu_seconds'],'weights_sha256':m['weights_sha256'],'data_sha256':m['data_sha256'],'reload_logits_exact':r['reload_logits_exact'],'initial_parameter_inventory_sha256':r['initial_parameter_inventory_sha256'],'schedule_indices_sha256':r['schedule_indices_sha256']}
    checks.append((r['initial_parameter_inventory_sha256'],r['schedule_indices_sha256']))
assert checks[0]==checks[1]
result['matched_initial_parameters_and_training_schedule']=True
a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
