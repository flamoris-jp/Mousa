"""Prepare matched arms from already-reviewed prior experiment, no source expansion."""
import argparse,hashlib,json
from pathlib import Path
PIN='9c3f2e95b00d60ad4f464a40836b823209d589411ce48bcb7be31ac4d8131851'
TASK='mousa.rhythm-first-comparison.experimental.v1'

def prepare(source):
    result={}
    for arm in ('independent','rhythm_first'):
        d={'schema':'mousa.rhythm-first-training.experimental.v1','task_id':TASK,'arm':arm}
        for split in ('train','test'):
            rows=source[split];lookup={(r['family'],r['target_index'],r['task']):r for r in rows};converted=[]
            if len(lookup)!=len(rows):raise ValueError('duplicate rows')
            for r in rows:
                x=list(r['input']);suffix=[0,0,0]
                if arm=='rhythm_first' and r['task']!=0:
                    for pos in range(3,51,6):x[pos]=183  # no unknown pitches in whole rhythm pass
                if arm=='rhythm_first' and r['task']==0:
                    labels=[lookup[(r['family'],r['target_index'],t)]['label'] for t in (1,2,3)]
                    if labels[1]>labels[0] or labels[2]!=labels[0]-labels[1]:raise ValueError('current relation')
                    suffix=[v+o for v,o in zip(labels,(311,359,407))]
                converted.append({**r,'input':x+suffix})
            d[split]=converted
        result[arm]=d
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    raw=a.source.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PIN:raise ValueError('prior input digest')
    data=prepare(json.loads(raw));a.out.mkdir(exist_ok=False,parents=True)
    receipt={'prior_data_sha256':PIN,'arms':{}}
    for arm,d in data.items():
        raw=(json.dumps(d,sort_keys=True,indent=2)+'\n').encode();(a.out/(arm+'.json')).write_bytes(raw);receipt['arms'][arm]=hashlib.sha256(raw).hexdigest()
    (a.out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__':main()
