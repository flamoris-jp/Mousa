"""Frozen-model transfer after separately verified exact MIDI intake.

Tempo/CC7 metadata remain in the tick representation; prediction uses explicitly
projected pitch/rhythm tokens, never elapsed audio seconds. No heldout fitting.
"""
import argparse
import hashlib
import json
from pathlib import Path
from mousa.research_intake import validate_manifest
from mousa.source_similarity import interval_edit_similarity
from mousa.event_baseline import events_from_grid
from mousa.factorized_baseline import onset_phrases
from mousa.position_event_model import PositionEventModel
from mousa.meter_midi import read_midi as old_read,to_tokens as old_tokens
from mousa.tick_midi import read_midi,write_midi,to_tokens,inspect_grid_error


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def channel_signature(path, track):
    import mido
    result=[];tick=0
    for event in mido.MidiFile(path).tracks[track]:
        tick+=event.time
        if event.is_meta:continue
        # Canonicalize the two equivalent MIDI encodings of note-off only.
        if event.type=='note_on' and event.velocity==0:
            event=mido.Message('note_off',channel=event.channel,note=event.note,velocity=0)
        result.append((tick,tuple(event.bytes())))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('corpus','manifest','origins','freeze','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('new output required')
    root=Path(__file__).resolve().parents[1];freeze=json.loads(a.freeze.read_text())
    for path,sha in freeze['sha256'].items():
        if digest(root/path)!=sha:raise ValueError('frozen source/config changed: '+path)
    manifest=json.loads(a.manifest.read_text());validate_manifest(manifest,a.corpus)
    origins={f"mutopia-{w['id']}":w['origin_steps'] for w in json.loads(a.origins.read_text())['works']}
    songs=[];sources={};intake={}
    a.output.mkdir(parents=True)
    plan=dict(freeze_sha256=digest(a.freeze),manifest_sha256=digest(a.manifest),
              new_intake_code_sha256=digest(root/'src/mousa/tick_midi.py'),
              driver_sha256=digest(Path(__file__)),approximate_screen_sha256=digest(root/'src/mousa/source_similarity.py'),
              approximate_threshold=.90,minimum_intervals=16,note='No parameter selection or refitting from heldout scores.')
    (a.output/'before-scoring.json').write_text(json.dumps(plan,indent=2)+'\n')
    for w in manifest['works']:
        path=a.corpus/w['file'];original=digest(path)
        melody=read_midi(path,w['track_index']);shift=60-min(n.pitch for n in melody.notes)
        tokens=to_tokens(melody,transpose_semitones=shift);events=events_from_grid(tokens)
        output=a.output/(w['work_id']+'-selected.mid');write_midi(melody,output)
        if read_midi(output,1)!=melody:raise AssertionError('tick/tempo/volume roundtrip failed')
        if channel_signature(path,w['track_index'])!=channel_signature(output,1):raise AssertionError('channel event/order changed')
        if digest(path)!=original:raise AssertionError('original changed')
        sources[w['work_id']]=dict(tokens=tokens,events=events,work=w,meter=melody.meter)
        if w['work_id'] in freeze['train_ids']:
            old=old_read(path,w['track_index'])
            if old_tokens(old,transpose_semitones=shift)!=tokens:raise AssertionError('old training projection changed')
            songs.append((melody.meter,events,origins[w['work_id']]))
        intake[w['work_id']]=dict(source_sha256=original,projection_transposition=shift,
            notes=len(melody.notes),steps=len(tokens),events=len(events),
            grid_diagnostic=inspect_grid_error(melody),exact_tick_roundtrip=True,independent_channel_event_order_equal=True,
            projected_performance_dimensions='tempo/volume/program/velocity excluded from tokens; preserved in tick melody and original')
    if len(songs)!=len(freeze['train_ids']):raise ValueError('missing frozen training sources')
    duplicates=[]
    for i,(n,s) in enumerate(sources.items()):
        for other,t in list(sources.items())[:i]:
            shared=len(set(onset_phrases(s['tokens']))&set(onset_phrases(t['tokens'])))
            equal=s['tokens']==t['tokens'];approx=interval_edit_similarity(s['tokens'],t['tokens'])
            duplicates.append(dict(a=n,b=other,full_normalized_equal=equal,shared_8_note_phrases=shared,interval_edit=approx))
            if (shared or equal or (approx['comparable'] and approx['normalized_similarity']>=.90)) and s['work']['family_id']!=t['work']['family_id']:
                raise ValueError('cross-family similarity signal requires review before scoring')
    models={}
    configs=[dict(name='frozen-selected',**freeze['selected_model'])]
    for c in freeze['controls']:configs.append(dict(freeze['selected_model'],**c))
    for config in configs:
        config=config.copy();name=config.pop('name');model=PositionEventModel(songs,**config)
        metrics={n:model.evaluate(s['events'],meter=s['meter'],origin_steps=s['work']['origin_steps'])
                 for n,s in sources.items() if s['work'].get('evaluation_role')=='fresh_transfer_only'}
        models[name]=dict(config=config,works=metrics,
            one_correlated_family_work_mean_nll=sum(m['nll_per_event'] for m in metrics.values())/len(metrics))
    result=dict(plan=plan,intake=intake,duplicate_checks=duplicates,models=models,
        status='These works are now observed. No new training or parameter tuning performed.',
        scope='One new correlated Schubert/edition/typesetter family, not broad generalization or musical attractiveness.')
    (a.output/'report.json').write_text(json.dumps(result,indent=2,default=str)+'\n')
    print(json.dumps({n:m['one_correlated_family_work_mean_nll'] for n,m in models.items()}))

if __name__=='__main__':main()
