"""Shared-candidate non-tonal ending-proxy selection; no appeal labels."""
import argparse
from collections import Counter
from datetime import datetime,timezone
import json
from pathlib import Path
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.settling_ending import generate_group
from mousa.overlap_midi import read_midi,write_midi,OverlapMelody
from mousa.tick_midi import TickNote
from mousa.research_intake import validate_manifest
from compare_context_onset_gate import digest,metrics,summarize
from compare_onset_gate_models import pairs,phrases,similarity


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('corpus','source','output','frozen-plan'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[1]
    if a.output.exists():raise ValueError('new output required')
    frozen=json.loads(a.frozen_plan.read_text())
    for path in ('src/mousa/optimized_feasible_generation.py','src/mousa/context_onset_gate.py',
                 'src/mousa/feasible_context_generation.py','src/mousa/onset_gate_model.py',
                 'datasets/research-exploratory-multifamily-20261112.json'):
        if digest(root/path)!=frozen['code_sha256'][path]:raise ValueError('frozen input changed')
    tracked=['src/mousa/settling_ending.py','tools/compare_settling_ending.py','src/mousa/optimized_feasible_generation.py',
        'src/mousa/context_onset_gate.py','src/mousa/onset_gate_model.py','src/mousa/overlap_midi.py',
        'tools/compare_context_onset_gate.py','tools/compare_onset_gate_models.py',
        'datasets/research-exploratory-multifamily-20261112.json','datasets/research-brahms580-rights-20261112.json']
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='Cycle16 exploratory proxy-based selection, not freshvalidation or tonal cadence',
        train_ids=['mutopia-376','mutopia-888','mutopia-889','mutopia-789'],reserved_never_load=[583],
        source580='Previously observed, source/copy screen only; no new fit or predictive score',
        generator='Frozen optimized timing/pitchcontext strength4,uniformmix.25,trailingrest<=384,target9216,max256notes,poly<=3',
        groups=10,candidates_per_group=4,seeds='group*4+offset,groups0..9,offset0..3; all40 generated irrespectiveeligibility',
        ending_proxy='Atleast2onsets; lastgeneratedonset>=target-1152; lastgate>=384; abs lastonsetpitchinterval<=2; lastnote end>=allother ends',
        interpretation='Generic settling proxy, key-free but not learned harmonic/tonal cadence. Onset interval acrosspolyphony is notvoiceleading.',
        baseline='first complete copy-safe candidate',selection='first complete copy-safe proxyeligible candidate; noextra retries',
        budget='Both analysed on same4candidatepool; first-success baseline could practically use fewer generations. Report candidatepositions andfailures.',
        source_screen='exact8onset pitchinterval or wholeinterval similarity>=.80 blocks',
        copy_guard='old4plus580,generatedandcanonicalonsetorders; notperceptual/legalclearance',
        metrics=['lastgate','finalinterval','unique/repeat/leaps','notes/overlap/rest','eligibilityreason','complete/copyfail/groupmissing'],
        aggregation='Allgroups retained; completeonly means andmatchedsuccessfulgroup paired means with denominators',
        selection_bias='Improving the chosen proxy is expected byconstruction; examine variety/cost/failures, noappealclaim',
        no_tuning_after_results=True,frozen_plan_sha256=digest(a.frozen_plan),code_sha256={n:digest(root/n) for n in tracked})
    a.output.mkdir(parents=True);(a.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    manifest=json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text());validate_manifest(manifest,a.corpus)
    seqs=[];pss=[];source_hashes={}
    for w in manifest['works']:
        if w['work_id'] not in plan['train_ids']:continue
        m=read_midi(a.corpus/w['file'],w['track_index']);seqs.append(pairs(m));pss.append([n.pitch for n in m.notes])
        source_hashes[w['work_id']]=digest(a.corpus/w['file'])
    if len(seqs)!=4:raise ValueError('missing training source')
    expected='dcd5efac22b5e91b7c87685058784396adb9ec5d69915764265ad68158dbb6e1'
    if digest(a.source)!=expected:raise ValueError('580hash mismatch')
    rights=json.loads((root/'datasets/research-brahms580-rights-20261112.json').read_text())
    if rights['encoding_rights']['status']!='PD-dedication-supported':raise ValueError('rights evidence missing')
    test=read_midi(a.source,1);testp=[n.pitch for n in test.notes];screens=[]
    for source in pss:
        match=len(phrases(source)&phrases(testp));near=similarity(source,testp)
        screens.append(dict(matches=match,similarity=near))
        if match or (near is not None and near>=.80):raise ValueError('source screen blocks')
    before=dict(plan_sha256=digest(a.output/'plan.json'),train_hashes=source_hashes,test_sha256=expected,
                training_events=sum(map(len,seqs)),source_screen=screens)
    (a.output/'before-generation.json').write_text(json.dumps(before,indent=2)+'\n')
    model=ContextOnsetGateModel(seqs,pss,timing_context=True,pitch_continuity=True,strength=4)
    groups=[]
    for group in range(10):
        result=generate_group(model,group,source_pitches=pss+[testp])
        for row in result['candidates']:
            ns=row.pop('notes');row['metrics']=metrics(ns,9216)
            row['metrics'].update(last_gate_ticks=row['ending']['last_gate_ticks'],final_abs_interval=row['ending']['final_abs_interval'])
            if row['status']=='complete':
                notes=tuple(sorted((TickNote(n['start'],n['end'],n['pitch'],80,0) for n in ns),key=lambda n:(n.start,n.end,n.pitch)))
                events=[]
                for i,n in enumerate(ns):events.extend(((n['start'],1,i,'note_on',n['pitch'],80),(n['end'],0,i,'note_off',n['pitch'],0)))
                stream=((0,'program',0,0),)+tuple((t,k,p,v) for t,_,i,k,p,v in sorted(events))
                melody=OverlapMelody(notes,9216,(6,8),ppq=384,channel_events=stream)
                path=a.output/f'candidate-{row["seed"]}.mid';write_midi(melody,path)
                if read_midi(path,1)!=melody:raise ValueError('MIDI roundtrip mismatch')
                row.update(midi_sha256=digest(path),exact_roundtrip=True)
        groups.append(result)
    complete_groups=[g for g in groups if g['selected_seed'] is not None and g['baseline_seed'] is not None]
    summary={};matched={}
    for method in ('baseline','selected'):
        rows=[next(c for c in g['candidates'] if c['seed']==g[method+'_seed']) for g in groups if g[method+'_seed'] is not None]
        means,den=summarize(rows);summary[method]=dict(means=means,metric_denominators=den,count=len(rows))
        rows=[next(c for c in g['candidates'] if c['seed']==g[method+'_seed']) for g in complete_groups]
        means,den=summarize(rows);matched[method]=dict(means=means,metric_denominators=den,count=len(rows))
    report=dict(plan=plan,before_generation=before,groups=groups,summary=summary,
        matched_groups=dict(groups=[g['group'] for g in complete_groups],summary=matched),
        candidate_statuses=dict(Counter(c['status'] for g in groups for c in g['candidates'])),
        proxy_failure_reasons=dict(Counter(reason for g in groups for c in g['candidates'] for reason in c['ending']['reasons'])),
        selected_group_failures=sum(g['selected_seed'] is None for g in groups),
        original_unchanged=digest(a.source)==expected,
        limitations=['No invented tonic/key, no tonal cadence or appeal inference.',
            'Selection explicitly favors longsmallstep endings; objective changes are expected.',
            'Four-candidate search costs morethan first-success baseline in practical use.',
            'Matchedgroup means are selected-success conditioned; missinggroups retained.',
            'All40candidateMIDIs retained, notonly selected ones; noaudio or corpus redistribution.'])
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('summary','matched_groups','candidate_statuses','proxy_failure_reasons','selected_group_failures')},indent=2))


if __name__=='__main__':main()
