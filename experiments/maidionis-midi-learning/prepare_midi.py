"""Freeze bounded native-Core MIDI diagnostic inputs; keep dataset private."""
import argparse,hashlib,json,sys,importlib.util
from pathlib import Path
from datetime import datetime,timezone

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):
 with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--split',type=Path,required=True);ap.add_argument('--extractor',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(exist_ok=True)
 s=json.loads(a.split.read_text());assert sha(a.split)=='a08f7201e846e09c91e79036c74fefe687e8c431e353f33163d6c935cfbad517'
 seed='mousa-maidionis-midi-v1';rank=lambda r:hashlib.sha256((seed+':'+r['family_id']).encode()).hexdigest()
 train=sorted([r for r in s['members'] if r['split']=='train'],key=rank)[:128];test=sorted([r for r in s['members'] if r['split']=='test'],key=rank)[:16]
 assert len(train)==128 and len(test)==16;assert not ({r['family_id'] for r in train}&{r['family_id'] for r in test})
 plan={'id':seed,'frozen_utc':datetime.now(timezone.utc).isoformat(),'upstream_commit':'c288e92979d5005742a1bc3f86b389eadbc873d3','split_sha256':sha(a.split),'extractor_sha256':sha(a.extractor),'prepare_sha256':sha(Path(__file__)),'input_evidence_sha256':s['input_sha256'],'model':'actual Maidionis encoder','seeds':[42,43,44],'steps':100,'batch_size':32,'learning_rate':0.0003,'weight_decay':0,'dropout_milli':0,'max_grad_norm':1,'cpu_threads':1,'context':8,'vocabulary':51,'controls':[1],'output_width':49,'maximum_onsets':2048,'max_windows_per_family':32,'window_selection':'evenly spaced integer floor indices across eligible targets, no replacement','family_ranking':'SHA256(mousa-maidionis-midi-v1:familyID), nested first18/first128 originalTRAIN; first16 originalTEST','train18_families':[r['family_id'] for r in train[:18]],'train128_families':[r['family_id'] for r in train],'test_families':[r['family_id'] for r in test],'freshness':'All selected test families already observed in Cycle53; regression/diagnostic only, never fresh test. Original validation/test roles preserved; no test tuning.','conditions':['train18_ordered','train128_ordered','train18_context_permuted','train128_context_permuted'],'selection':'final100 steps only, identical initialization/compute across amounts, no selection on test','controls_description':'uniform and additive smoothed unigram/trigram trained on same selected window targets and their histories; shuffled context leaves label unchanged','projection':'highest non-drum pitch at each exact onset across tracks, first2048onsets; semitone differences clipped[-24,24]+24; ignores duration, velocity, lower voices, tempo and instrumentation; not annotated melody','token_mapping':'padding0,CLS1, interval class0..48 mapped to input2..50; target0..48','metrics':'per-family NLL and accuracy, family-macro primary; pooled secondary; initial/final train/test; finite gradient and parameter update','limitations':['dataset amount confounded repertoire; equal steps differs exposure per window','small already-observed16-family test','no quality or generation claims','no SA','private extracted inputs and attribution sidecar, no corpus or weights publication']}
 write(a.out/'midi-plan.json',plan)
 for k,h in s['input_sha256'].items():assert sha(s['input_paths'][k])==h,(k,'evidence mismatch')
 allows={c:json.loads(Path(s['input_paths'][c+'_allowlist']).read_text()) for c in ['pd','by']};rights={c:{r['mutopia_id']:r for r in json.loads(Path(s['input_paths'][c+'_rights']).read_text())['records']} for c in ['pd','by']}
 spec=importlib.util.spec_from_file_location('extractor',a.extractor);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 rows={};ledger=[];private=[]
 for r in train+test:
  assert r['corpus'] in ['pd','by'];assert 'ShareAlike' not in r['license']
  candidates=[f for f in allows[r['corpus']]['files'] if f['path']==r['midi_relative_path'] and f['sha256']==r['sha256']];assert len(candidates)==1 and candidates[0]['eligible_for_note_event_training']
  assert rights[r['corpus']][r['selected_source_id']]['rights_eligible']
  assert sha(r['source_path'])==r['sha256']
  features,total,_=mod.read_projection(Path(r['source_path']),r['sha256'],2048);seq=features['pitch_interval'];n=len(seq)-8;assert n>0,(r['family_id'],'too few intervals')
  count=min(32,n);indices=[8] if count==1 else [8+i*(n-1)//(count-1) for i in range(count)];assert len(set(indices))==count
  rows[r['family_id']]=[{'family':r['family_id'],'target_index':i,'input':[1]+[v+2 for v in seq[i-8:i]],'target':seq[i]} for i in indices]
  ledger.append({k:r[k] for k in ['family_id','source_ids','selected_source_id','corpus','split','sha256','license','license_version','license_url','source_page','attribution','source_asset_hashes'] }|{'onsets_total':total,'intervals_used':len(seq),'windows':count,'modification_notice':plan['projection'],'observed_test_before_this_run':r['split']=='test'})
  private.append({'family':r['family_id'],'source_path':r['source_path']})
 dataset={key:[v for r in members for v in rows[r['family_id']]] for key,members in [('train18',train[:18]),('train128',train),('test',test)]}
 write(a.out/'midi-dataset-private.json',dataset);write(a.out/'midi-attribution.json',{'note':'Source attribution, no raw MIDI or token sequences. Preserve original notices in source assets.','sources':ledger});write(a.out/'midi-private-paths.json',private)
 write(a.out/'midi-preparation-audit.json',{'all_rights_allowlist_source_hash_checks':True,'no_sa':True,'split_family_disjoint':True,'counts':{k:len(v) for k,v in dataset.items()},'family_counts':{'train18':18,'train128':128,'test':16},'files':{p.name:sha(p) for p in a.out.glob('midi-*.json')}})
 print(json.dumps({'counts':{k:len(v) for k,v in dataset.items()},'files_sha256':{p.name:sha(p) for p in a.out.glob('midi-*.json')}}))
if __name__=='__main__':main()
