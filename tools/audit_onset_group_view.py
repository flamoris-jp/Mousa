"""Descriptive lossless note-group audit on the existing14 training works."""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from compare_fourteen_approved_expansion import nine_addition_validation
from compare_approved_expansion import read_inputs,digest
from mousa.onset_groups import group_notes,restore_notes

ASSIGNMENT='datasets/research-cycle32-fourteen-work-assignment.json'
TRACKED=[ASSIGNMENT,'src/mousa/onset_groups.py','tools/audit_onset_group_view.py','tests/test_onset_groups.py']


def prepare(root,output):
    if output.exists():raise ValueError('new plan destination required')
    plan={'scope':'Descriptive existing14 training works; no fitting, unseen score or melody labels.',
          'operation':'Group every selected note by exact original onset, retaining input index and all note fields. Restore exact input order.',
          'limits':'Note-only view. Original metadata, channel-event order and MIDI bytes remain outside view. No voice assignment or chord-function inference.',
          'metrics':['note_count','onset_group_count','multi_note_onset_groups','largest_onset_group','exact_note_state_roundtrip'],
          'frozen_hashes':{p:digest(root/p) for p in TRACKED}}
    output.mkdir(parents=True);(output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')


def audit(root,corpus,extra,source_root,targets,plan_dir,output):
    if output.exists():raise ValueError('new report destination required')
    plan=json.loads((plan_dir/'plan.json').read_text())
    for p,h in plan['frozen_hashes'].items():
        if digest(root/p)!=h:raise ValueError('frozen artifact changed')
    assignment=json.loads((root/ASSIGNMENT).read_text())
    with nine_addition_validation():base,added,_,_,_=read_inputs(root,corpus,extra,source_root,assignment,targets)
    rows=[]
    for work,m in {**base,**added}.items():
        groups=group_notes(m.notes,m.total_ticks);back=restore_notes(groups,m.total_ticks)
        original=json.dumps([asdict(n) for n in m.notes],sort_keys=True).encode()
        restored=json.dumps([asdict(n) for n in back],sort_keys=True).encode()
        if original!=restored:raise AssertionError('selected-note information loss')
        rows.append({'work_id':work,'notes':len(back),'onset_groups':len(groups),'multi_note_onset_groups':sum(len(g.members)>1 for g in groups),
          'largest_onset_group':max((len(g.members) for g in groups),default=0),'selected_note_state_sha256':hashlib.sha256(original).hexdigest(),
          'exact_note_state_roundtrip':True,'timeline_ticks_in_unchanged_original':m.total_ticks})
    report={'plan_sha256':digest(plan_dir/'plan.json'),'works':rows,'notes':sum(x['notes'] for x in rows),'groups':sum(x['onset_groups'] for x in rows),
            'all_exact_note_state_roundtrip':True,'limitations':plan['limits'],'model_fits':0,'generated_media':0}
    output.mkdir(parents=True);(output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',choices=['prepare','audit'],required=True);p.add_argument('--plan-dir',type=Path,required=True)
    for k in ('corpus','extra','source-root','adam','chopin','output'):p.add_argument('--'+k,type=Path)
    a=p.parse_args();root=Path(__file__).resolve().parents[1]
    if a.stage=='prepare':prepare(root,a.plan_dir)
    else:
        if any(getattr(a,k) is None for k in ('corpus','extra','source_root','adam','chopin','output')):p.error('audit requires source and output paths')
        print(json.dumps(audit(root,a.corpus,a.extra,a.source_root,{'640':a.adam,'921':a.chopin},a.plan_dir,a.output),indent=2))
