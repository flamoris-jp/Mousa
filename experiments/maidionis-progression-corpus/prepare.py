"""Frozen rights-gated preparation, no training or outside annotations."""
import argparse,hashlib,json,re,subprocess,unicodedata
from collections import Counter,defaultdict
from pathlib import Path
from extract_weak import extract,POLICY

TASK='mousa.major-progression.weak-label.experimental.v1'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(path,obj):
    with Path(path).open('x') as f:json.dump(obj,f,indent=2,sort_keys=True);f.write('\n')
def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args])
def work_key(directory):
    parts=Path(directory).parts
    if len(parts)!=4 or parts[0]!='scores':raise ValueError('score directory shape')
    composer=parts[1];title=parts[3]
    if composer=='Schubert,_Franz':
        match=re.search(r'(?:^|_)D\.(\d+[a-z]?)\b',title,re.I)
        if match:return composer+':D'+match[1].lower()
    title=re.sub(r'^\d+[a-z]?[_ .-]+','',title,flags=re.I)
    title=unicodedata.normalize('NFKD',title).casefold()
    title=''.join(c for c in title if c.isalnum())
    if not title:raise ValueError('missing work identity')
    return composer+':title:'+title

def close_families(records):
    parent={r['family_id']:r['family_id'] for r in records}
    def find(x):
        while parent[x]!=x:x=parent[x]
        return x
    links=[];seen={}
    for r in records:
        for kind,value in [('sha256',r['sha256']),('work',r['work_key'])]:
            key=(kind,value)
            if key in seen:
                a,b=find(r['family_id']),find(seen[key])
                if a!=b:parent[max(a,b)]=min(a,b);links.append({'kind':kind,'value':value,'families':[a,b]})
            else:seen[key]=r['family_id']
    groups=defaultdict(list)
    for f in parent:groups[find(f)].append(f)
    # Canonical component name stable and <=256 chars, long membership in provenance.
    family_by_original={f:'openscore-family:'+hashlib.sha256('\n'.join(sorted(fs)).encode()).hexdigest()[:24] for fs in groups.values() for f in fs}
    return family_by_original,{family_by_original[fs[0]]:sorted(fs) for fs in groups.values()},links

def split_families(families):
    ordered=sorted(families,key=lambda f:(hashlib.sha256(('20261117:'+f).encode()).hexdigest(),f))
    if len(ordered)<=5:raise ValueError('insufficient families for frozen first5test')
    return {f:'test' if i<5 else 'train' for i,f in enumerate(ordered)}

def windows(bars,context=8):
    if type(context)is not int or context not in (2,8):raise ValueError('unsupported context')
    history=[]
    for bar in bars:
        label=bar['label']
        if label is None:history=[];continue
        if type(label)is not int or not 0<=label<14:raise ValueError('weak label range')
        if len(history)==context:yield bar['measure_index'],[1]+[v+2 for v in history],label
        history=(history+[label])[-context:]

def prepare(root,allowlist,protocol_path,out):
    root=root.resolve();protocol=json.loads(protocol_path.read_text());allow=json.loads(allowlist.read_text())
    if sha(allowlist)!=protocol['rights_allowlist_sha256'] or git(root,'rev-parse','HEAD').decode().strip()!=protocol['source_commit']:raise ValueError('source or allowlist pin')
    if POLICY!=protocol['extractor_policy']:raise ValueError('extractor threshold drift')
    if 'extractor_sha256' in protocol and sha(Path(__file__).with_name('extract_weak.py'))!=protocol['extractor_sha256']:raise ValueError('extractor source pin')
    context=protocol.get('context_bars',8)
    if type(context)is not int or context not in (2,8):raise ValueError('unsupported context')
    task=TASK if context==8 else 'mousa.major-progression-local2.weak-label.experimental.v1'
    if protocol.get('task_id',task)!=task:raise ValueError('task/context mismatch')
    if allow['counts']!={'sets':22,'score_entries':198,'excluded_sets':6}:raise ValueError('allowlist counts drift')
    for name,digest in allow['metadata_sha256'].items():
        if sha(root/'data'/name)!=digest:raise ValueError('rights metadata digest')
    if b'CC0 1.0 Universal' not in (root/'LICENSE.txt').read_bytes():raise ValueError('source licence')
    # Pin exact content to committed blobs, without reading any lyrics/annotation text.
    tracked={}
    for item in git(root,'ls-tree','-r','-z',protocol['source_commit'],'--','scores').split(b'\0'):
        if not item:continue
        info,path=item.split(b'\t',1);tracked[path.decode()]=info.decode().split()[2]
    records=[];exclusions=[]
    for row in sorted(allow['scores'],key=lambda r:r['score_id']):
        if row['eligible_for_intake'] is not True:raise ValueError('ineligible member')
        rel=row['score_directory']+'/lc'+str(row['score_id'])+'.mscx';path=root/rel
        if not path.is_file():exclusions.append({'score_id':row['score_id'],'stage':'availability','reason':'missing_exact_file'});continue
        raw=path.read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if rel not in tracked or tracked[rel]!=blob:raise ValueError('source file differs from pinned git blob')
        records.append({**row,'relative_path':rel,'git_blob_sha1':blob,'sha256':hashlib.sha256(raw).hexdigest(),'work_key':work_key(row['score_directory'])})
    familymap,groups,links=close_families(records);split=split_families(groups)
    inventory_sha=hashlib.sha256(json.dumps([[r['score_id'],r['sha256']] for r in records],separators=(',',':')).encode()).hexdigest()
    if 'source_inventory_sha256' in protocol and inventory_sha!=protocol['source_inventory_sha256']:raise ValueError('frozen source inventory drift')
    if 'frozen_assignments' in protocol and split!=protocol['frozen_assignments']:raise ValueError('frozen family split drift')
    out.mkdir(exist_ok=False,parents=True)
    dump(out/'frozen-split.json',{'protocol_sha256':sha(protocol_path),'groups':groups,'assignments':split,'union_links':links,'phase':'written_before_extraction'})
    data={'schema':'mousa.progression-training.experimental.v1','task_id':task,'train':[],'test':[]};family_counts=Counter();family_offsets=Counter();summaries=[];identities=[];nulls=Counter();bar_count=0;eligible_bar_count=0
    (out/'extractions').mkdir()
    for row in sorted(records,key=lambda r:r['score_id']):
        family=familymap[row['family_id']];role=split[family]
        try:result=extract(root/row['relative_path'])
        except (ValueError,KeyError) as error:
            exclusions.append({'score_id':row['score_id'],'family':family,'split':role,'sha256':row['sha256'],'stage':'score_gate','reason':str(error)});continue
        if result['source_sha256']!=row['sha256']:raise ValueError('source mutated during extract')
        dump(out/'extractions'/(str(row['score_id'])+'.json'),result)
        count=0;available=0;offset=family_offsets[family]
        for index,x,label in windows(result['bars'],context):
            available+=1
            if family_counts[family]>=(512 if role=='train' else 128):continue
            unique_index=offset+index+context
            data[role].append({'family':family,'index':unique_index,'input':x,'label':label})
            identities.append({'family':family,'index':unique_index,'score_id':row['score_id'],'measure_index':index,'split':role})
            family_counts[family]+=1;count+=1
        family_offsets[family]+=len(result['bars'])+8
        for bar in result['bars']:
            bar_count+=1;eligible_bar_count+=bar['label'] is not None
            if bar['label'] is None:nulls[bar['reason']]+=1
        summaries.append({'score_id':row['score_id'],'family':family,'split':role,'sha256':row['sha256'],'bars':len(result['bars']),'accepted_bars':result['accepted_bars'],'available_windows':available,'selected_windows':count})
    if {r['family'] for r in data['train']} & {r['family'] for r in data['test']}:raise ValueError('family leakage')
    dump(out/'training.json',data)
    dump(out/'provenance.json',{'source_commit':protocol['source_commit'],'licence_sha256':sha(root/'LICENSE.txt'),'allowlist_sha256':sha(allowlist),'protocol_sha256':sha(protocol_path),'extractor_sha256':sha(Path(__file__).with_name('extract_weak.py')),'prepare_sha256':sha(__file__),'records':records,'family_closure':groups,'union_links':links,'window_identities':identities,'prior_exposure':'unverified historical exposure; family-unseen for this fresh fit only','no_lyrics_or_external_annotations_used':True})
    dump(out/'exclusions.json',exclusions)
    counts={'candidate_entries':len(allow['scores']),'available_exact_files':len(records),'families_before_union':len(set(r['family_id'] for r in records)),'families_after_union':len(groups),'assigned_families':dict(Counter(split.values())),'scores_passed_structure':len(summaries),'bars':bar_count,'accepted_bars':eligible_bar_count,'null_bar_reasons':dict(nulls),'rows':{k:len(data[k]) for k in ('train','test')},'scores_with_windows':{k:sum(r['split']==k and r['selected_windows']>0 for r in summaries) for k in ('train','test')},'families_with_windows':{k:len({r['family'] for r in data[k]}) for k in ('train','test')},'label_counts':{k:dict(Counter(r['label'] for r in data[k])) for k in ('train','test')},'family_window_counts':dict(family_counts),'score_summaries':summaries,'exclusion_counts':dict(Counter(r['reason'] for r in exclusions)),'training_sha256':sha(out/'training.json'),'status':'prepared_not_trained' if data['train'] and data['test'] else 'blocked_insufficient_nonempty_partitions'}
    dump(out/'counts.json',counts);return counts

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--allowlist',type=Path,required=True);p.add_argument('--protocol',type=Path,default=Path(__file__).with_name('protocol.json'));p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    print(json.dumps(prepare(a.root,a.allowlist,a.protocol,a.out),indent=2))
