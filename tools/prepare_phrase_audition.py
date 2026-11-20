"""Prepare private blinded form comparisons, not human ratings or public media."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import struct
import wave
from mousa.event_baseline import events_from_grid
from mousa.factorized_baseline import onset_phrases
from mousa.meter_midi import read_midi,to_tokens,from_tokens,write_midi
from mousa.position_event_model import PositionEventModel
from mousa.phrase_baseline import generate_phrase_form
from mousa.research_intake import validate_manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('corpus','manifest','origins','preview_module','output'):p.add_argument('--'+key.replace('_','-'),type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('new output required')
    # Pinned renderer comes from existing PR6; reject another implementation.
    expected='eaef9f3f915d3b928789d141e7ebf36f04fe12de8f82d7e352189670911fa30d'
    renderer_hash=hashlib.sha256(a.preview_module.read_bytes()).hexdigest()
    if renderer_hash != expected:raise ValueError('renderer digest differs from inspected source')
    spec=importlib.util.spec_from_file_location('private_preview',a.preview_module)
    preview=importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name]=preview;spec.loader.exec_module(preview)
    manifest=json.loads(a.manifest.read_text());validate_manifest(manifest,a.corpus)
    origins={f"mutopia-{w['id']}":w['origin_steps'] for w in json.loads(a.origins.read_text())['works']}
    songs=[];refs=[]
    for w in manifest['works']:
        m=read_midi(a.corpus/w['file'],w['track_index']);tokens=to_tokens(m,transpose_semitones=60-min(n.pitch for n in m.notes));refs.append(tokens)
        if w['split']=='train':songs.append((m.meter,events_from_grid(tokens),origins[w['work_id']]))
    model=PositionEventModel(songs,meter_position=True,relative=True,duration_prior='empirical',position_strength=1)
    config=dict(seeds=[7,17,29],order_seed=20261112,meter=[6,8],steps=96,rest_cap=12,
        model='score-origin relative empirical bar k1; cycle5 exploratory selection',
        structure='handcrafted A-Aprime-B-Adoubleprime; no learned form',
        renderer_sha256=renderer_hash,preview='analytic sine with second harmonic, no sampled audio',
        manifest_sha256=hashlib.sha256(a.manifest.read_bytes()).hexdigest(),
        origins_sha256=hashlib.sha256(a.origins.read_bytes()).hexdigest())
    a.output.mkdir(parents=True);(a.output/'plan.json').write_text(json.dumps(config,indent=2)+'\n')
    rng=random.Random(config['order_seed']);report=[];responses=[]
    for i,seed in enumerate(config['seeds'],1):
        samples=dict(direct=model.generate(seed,meter=(6,8),steps=96,source_grids=refs,max_rest_run=12),
            form=generate_phrase_form(model,seed,meter=(6,8),source_grids=refs,max_rest_run=12))
        order=list(samples);rng.shuffle(order);pair=[]
        for label,method in zip('AB',order):
            sample=samples[method];tokens=sample.pop('tokens');name=f'pair{i}-{label}'
            metadata=dict(id=name,method=method,seed=seed,**sample)
            if sample['status']=='complete':
                midi=a.output/(name+'.mid');wav=a.output/(name+'.wav')
                write_midi(from_tokens(tokens,meter=(6,8)),midi)
                if to_tokens(read_midi(midi,1,allow_empty=True))!=tokens:raise AssertionError('MIDI roundtrip')
                matches=sum(len(set(onset_phrases(tokens)) & set(onset_phrases(r))) for r in refs)
                if matches:raise AssertionError('source phrase overlap')
                preview.write_preview_wav(tokens,wav)
                with wave.open(str(wav)) as w:
                    params=w.getparams();values=struct.unpack('<'+'h'*params.nframes,w.readframes(params.nframes))
                peak=max(abs(v) for v in values);clipped=sum(abs(v)>=32767 for v in values)
                metadata.update(midi_sha256=hashlib.sha256(midi.read_bytes()).hexdigest(),
                    wav_sha256=hashlib.sha256(wav.read_bytes()).hexdigest(),peak_pcm16=peak,clipped_samples=clipped,
                    frames=params.nframes,sample_rate=params.framerate,shared_8_note_phrases=matches,
                    notes=sum(t>=2 for t in tokens),rest_steps=tokens.count(0),human_quality='not rated',originality='not cleared')
            pair.append(metadata)
        report.append(dict(pair=i,clips=pair))
        responses.append(dict(pair=i,both_listened=None,coherence_choice=None,repetition_A=None,repetition_B=None,
                              replay_choice=None,comment=None))
    (a.output/'private-method-key.json').write_text(json.dumps(dict(config=config,pairs=report),indent=2)+'\n')
    (a.output/'listener-response-template.json').write_text(json.dumps(responses,indent=2)+'\n')
    print(json.dumps([dict(pair=r['pair'],statuses=[c['status'] for c in r['clips']]) for r in report]))

if __name__=='__main__':main()
