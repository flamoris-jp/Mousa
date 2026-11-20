"""Aggregate observed evaluation without turning descriptors into quality claims."""
import argparse,json,hashlib
from collections import Counter
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
d=json.loads(a.data.read_text());r=json.loads((a.model/'results.json').read_text());mf=json.loads((a.model/'manifest.json').read_text())
s=[]
for task,name in enumerate(['degree','ioi','duration','rest','accent','phrase']):
    train=[x['label'] for x in d['train'] if x['task']==task];test=[x['label'] for x in d['test'] if x['task']==task];major=Counter(train).most_common(1)[0][0]
    item={'task':name,'train_windows':len(train),'evaluation_windows':len(test),'train_label_counts':dict(Counter(train)),'evaluation_label_counts':dict(Counter(test)),'training_majority_label':major,'majority_evaluation_accuracy':test.count(major)/len(test)}
    for key in ['initial_test','final_test']:
        rows=[x for x in r[key] if x['task']==task]
        item[key]={'nll':sum(x['nll'] for x in rows)/len(rows),'accuracy':sum(x['prediction']==x['target'] for x in rows)/len(rows)}
    s.append(item)
out={'schema':'mousa.rhythm-results.experimental.v1','steps':mf['steps'],'cpu_seconds':r['cpu_seconds'],'embedding_delta_l1':r['embedding_delta_l1'],'reload_logits_exact':r['reload_logits_exact'],'transfer_tensor_count':len(r['transfer']['copied_parameters']),'data_sha256':mf['data_sha256'],'weights_sha256':mf['weights_sha256'],'observed_not_fresh':True,'metrics':s,'human_listening':False,'musical_quality_claim':False}
a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
