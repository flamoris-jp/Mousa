"""Conservative annotation-only preparation. No audio, fitting or publication."""
import argparse, bisect, collections, csv, hashlib, json, math, re, unicodedata
from pathlib import Path
Q = ['maj', 'min', 'dim', 'aug', '7', 'maj7', 'min7', 'hdim7']
EPS = 1e-8

def sha(b): return hashlib.sha256(b).hexdigest()
def norm(s): return ''.join(c for c in unicodedata.normalize('NFKD', s).casefold() if c.isalnum())
def write(p, d): p.write_text(json.dumps(d, indent=2, ensure_ascii=False)+'\n')
def pc(s):
    m = re.fullmatch(r'([A-G])((?:#{1,2}|b{1,2})?)', s or '')
    return None if not m else ({'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}[m[1]]+m[2].count('#')-m[2].count('b'))%12

def context(text):
    state = {'tonic':None, 'metre':None}; pending = {}; out = []
    for line in text.splitlines():
        if not line.strip(): continue
        if line.startswith('#'):
            m = re.match(r'#\s*(tonic|metre):\s*(.*)', line)
            if m: pending[m[1]] = m[2].strip()
            continue
        t, body = line.split(None, 1); t = float(t)
        state.update(pending); pending = {}
        out.append({'time':t, **state, 'inline_meter':bool(re.search(r'\(\d+/\d+\)',body))})
    if any(b['time'] < a['time']-EPS for a,b in zip(out,out[1:])): raise ValueError('salami_time_reversal')
    return out

def events(lab, salami):
    ctx = context(salami); times = [c['time'] for c in ctx]; raw=[]; last=None
    for line in lab.splitlines():
        if not line.strip(): continue
        a,b,label = line.split(); a=float(a); b=float(b)
        if not math.isfinite(a+b) or a<0 or b<=a: raise ValueError('nonpositive_or_invalid_time')
        if last is not None and a<last-EPS: raise ValueError('overlap')
        j=bisect.bisect_right(times,a+EPS)-1
        c=ctx[j] if j>=0 else {'tonic':None,'metre':None,'inline_meter':True}
        tonic=pc(c['tonic']); meter=c['metre']; validmeter=bool(re.fullmatch(r'[1-9]\d*/[1-9]\d*',meter or ''))
        # Any context change or uncertain inline-meter region inside an event is a barrier.
        crossing=any(a+EPS<x['time']<b-EPS and (x['tonic']!=c['tonic'] or x['metre']!=meter or x['inline_meter'] or c['inline_meter']) for x in ctx[j+1:])
        m=re.fullmatch(r'([A-G](?:#{1,2}|b{1,2})?):([A-Za-z0-9]+)(?:/([b#]*\d+))?',label)
        target=None
        if m and m[2] in Q and tonic is not None and validmeter and not c['inline_meter'] and not crossing:
            target=((pc(m[1])-tonic)%12)*8+Q.index(m[2])
        item={'start':a,'end':b,'raw':label,'bass':m[3] if m else None,'tonic':c['tonic'],'metre':meter,'label':target,'source_lines':[len(raw)],'gap_before':last is not None and a-last>EPS,'uncertain_context':c['inline_meter'] or crossing}
        raw.append(item); last=b
    merged=[]
    for idx,e in enumerate(raw):
        e['source_lines']=[idx]
        if merged and not e['gap_before'] and e['raw']==merged[-1]['raw'] and e['tonic']==merged[-1]['tonic'] and e['metre']==merged[-1]['metre'] and e['label']==merged[-1]['label'] and e['uncertain_context']==merged[-1]['uncertain_context'] and abs(e['start']-merged[-1]['end'])<=EPS:
            merged[-1]['end']=e['end']; merged[-1]['source_lines']+=e['source_lines']
        else: merged.append(dict(e))
    return merged

def windows(es):
    hist=[]; prev=None
    for i,e in enumerate(es):
        if e['gap_before'] or prev is not None and (e['tonic'],e['metre'])!=(prev['tonic'],prev['metre']): hist=[]
        if e['label'] is None: hist=[]
        else:
            if len(hist)>=2: yield i,[1,hist[-2]['label']+2,hist[-1]['label']+2],e['label']
            hist.append(e)
        prev=e

def prepare(root, out, protocol):
    prot=json.loads(protocol.read_text()); ph=sha(protocol.read_bytes())
    assert prot['quality_order']==Q and type(prot['context']) is int and prot['context']==2
    assert prot['task_id']=='mousa.relative-chord-events.annotated.experimental.v1'
    assert prot['training_schema']=='mousa.annotated-event-training.experimental.v1'
    assert prot['family_cap']==16
    out.mkdir(parents=True,exist_ok=False)
    for name,k in [('billboard-2.0-salami_chords.tar.xz','salami'),('billboard-2.0.1-lab.tar.xz','lab'),('billboard-2.0-index.csv','index')]: assert sha((root/name).read_bytes())==prot['sources'][k+'_sha256']
    prov=json.loads((root/'provenance.json').read_text()); lp=json.loads((root/'lab-provenance.json').read_text())
    for base,inv in [('annotations',prov['archive_inventory']),('lab',lp['inventory'])]:
        for r in inv: assert sha((root/base/r['path']).read_bytes())==r['sha256']
    index={int(r['id']):r for r in csv.DictReader((root/'billboard-2.0-index.csv').open())}
    files={int(f.parent.name):f for f in (root/'annotations').rglob('salami_chords.txt')}; labs={int(f.parent.name):f for f in (root/'lab').rglob('full.lab')}; assert files.keys()==labs.keys()
    parent={i:i for i in files}
    def find(i):
        while parent[i]!=i: parent[i]=parent[parent[i]]; i=parent[i]
        return i
    keys={}
    for i,f in sorted(files.items()):
        h=dict(re.findall(r'^#\s*(title|artist):\s*(.*)$',f.read_text(),re.M)); aliases=[(h['title'],h['artist']),(index[i]['title'],index[i]['artist'])]
        kk=[('sha',sha(f.read_bytes()))]
        for t,a in aliases:
            if norm(t): kk.extend([('title',norm(t)),('ta',norm(t),norm(a))])
        for k in kk:
            if k in keys: parent[find(i)]=find(keys[k])
            else: keys[k]=i
    groups=collections.defaultdict(list)
    for i in files: groups[find(i)].append(i)
    families={'billboard-family:'+sha(','.join(map(str,sorted(v))).encode())[:24]:sorted(v) for v in groups.values()}
    ranked=sorted(families,key=lambda f:sha(('20261117-billboard:'+f).encode())); n=math.ceil(len(ranked)*.2)
    split={f:('test' if i<n else 'train') for i,f in enumerate(ranked)}
    write(out/'frozen-split.json',{'protocol_sha256':ph,'families':families,'assignments':split,'phase':'before tokenization'})
    data={'schema':prot['training_schema'],'task_id':prot['task_id'],'train':[],'test':[]}; records=[]; exclusions=[]; identities=[]; (out/'events').mkdir()
    for family in sorted(families):
        sid=min(families[family]); group=split[family]
        try: es=events(labs[sid].read_text(),files[sid].read_text())
        except ValueError as e: exclusions.append({'family':family,'slot_id':sid,'reason':str(e)}); continue
        write(out/'events'/f'{sid}.json',es)
        ws=list(windows(es)); chosen=sorted(sorted(ws,key=lambda w:sha(f'20261117-billboard:{family}:{w[0]}'.encode()))[:16])
        for i,inp,label in chosen:
            assert i>=2 and inp==[1,es[i-2]['label']+2,es[i-1]['label']+2] and label==es[i]['label']
            data[group].append({'family':family,'index':i,'input':inp,'label':label}); identities.append({'family':family,'slot_id':sid,'index':i,'split':group,'source_line_indices':[es[k]['source_lines'] for k in range(i-2,i+1)]})
        records.append({'family':family,'slot_id':sid,'split':group,'salami_sha256':sha(files[sid].read_bytes()),'lab_sha256':sha(labs[sid].read_bytes()),'event_count':len(es),'eligible_windows':len(ws),'selected_windows':len(chosen),'metadata':index[sid]})
    counts={g+'_windows':len(data[g]) for g in ('train','test')}; counts.update({g+'_families':len({r['family'] for r in data[g]}) for g in ('train','test')})
    counts['gate_pass']=all(counts[k]>=v for k,v in prot['minimum_gate'].items()); counts['total_families']=len(families)
    write(out/'training.json',data);write(out/'counts.json',counts);write(out/'exclusions.json',exclusions);write(out/'provenance.json',{'protocol_sha256':ph,'prepare_sha256':sha(Path(__file__).read_bytes()),'records':records,'window_identities':identities,'all_windows_source_alignment_checked':True,'prior_exposure':prot['evaluation_claim']});print(json.dumps(counts));print('training_sha256',sha((out/'training.json').read_bytes()))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--protocol',type=Path,default=Path(__file__).with_name('protocol.json'));a=p.parse_args();prepare(a.root,a.out,a.protocol)
