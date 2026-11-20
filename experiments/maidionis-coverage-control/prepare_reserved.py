"""Extract only protocol-frozen reserved evaluation rows; never train on them."""
import argparse,hashlib,json,importlib.util
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--audit',type=Path,required=True);p.add_argument('--coverage',type=Path,required=True);p.add_argument('--extractor',type=Path,required=True);p.add_argument('--raw-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 if a.out.exists():raise ValueError('output exists')
 planpath=Path(__file__).with_name('execution-plan.json');plan=json.loads(planpath.read_text())
 assert sha(a.audit)==plan['reserve_audit_sha256']
 assert sha(a.coverage)=='c83019d1ee75c9d2612bb0707d8a51927b824b93b991cb70a11ac7f89d979e75'
 assert sha(a.extractor)=='ea05cc3df8206ebab9d5488fd33f63690370897d975eb892a3bbc389d09cc1ae'
 audit=json.loads(a.audit.read_text());data=json.loads(a.coverage.read_text());selected=[f for f in audit['families'] if f['role']=='blind_test_candidate'];assert [f['family_id'] for f in selected]==plan['fresh_evaluation_family_ids']
 for row in audit['inputs'].values():assert sha(Path(row['path']))==row['sha256']
 train={r['family'] for arm in data['arms'] for r in arm['train']};old={r['family'] for r in data['test']};reserved={f['family_id'] for f in selected};assert not reserved&(train|old)
 spec=importlib.util.spec_from_file_location('extractor',a.extractor);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 records=[];rows=[]
 for f in selected:
  x=f['selected_evaluation_candidate'];assert not f['allowed_training'] and not x['eligible_for_note_event_training'];assert x['excluded_reasons']==['blind_test_candidate'];assert not f['verified_family_closure']['new_sa_ids'] and not f['verified_family_closure']['potential_prior_split_bridge'];assert all(r['rights_eligible'] for r in f['documentary_rights_records'])
  path=a.raw_root/x['path'];assert sha(path)==x['sha256']
  features,total,_=m.read_projection(path,x['sha256'],2048);seq=features['pitch_interval'];n=len(seq)-8
  record={'family':f['family_id'],'source':x,'onsets_total':total,'intervals_used':len(seq),'allowed_training':False,'status':'observed_extracted_not_scored'}
  if n<=0:record.update(status='technical_skip_no_8_context',windows=0)
  else:
   count=min(32,n);indices=[8] if count==1 else [8+i*(n-1)//(count-1) for i in range(count)];assert len(set(indices))==count
   rows.extend({'family':f['family_id'],'target_index':i,'input':[1]+[v+2 for v in seq[i-8:i]],'label':seq[i]} for i in indices);record['windows']=count
  records.append(record)
 data['test'].extend(rows);a.out.mkdir(parents=True)
 for name,value in [('data.json',data),('evaluation-admission.json',{'execution_plan_sha256':sha(planpath),'audit_sha256':sha(a.audit),'extractor_sha256':sha(a.extractor),'no_training_role_change':True,'records':records,'historical_families':sorted(old),'reserved_families':sorted(reserved),'reserve_windows':len(rows),'freshness':'Previously unscored in available records, now extracted; no future untouched claim.'})]:
  (a.out/name).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'reserve_windows':len(rows),'families':len({r['family'] for r in rows}),'data_sha256':sha(a.out/'data.json')}))
if __name__=='__main__':main()
