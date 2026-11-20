"""Read-only technical diagnostics, not dataset admission or model evaluation."""
import argparse
import hashlib
import json
from pathlib import Path
import mido
from mousa.variable_meter_midi import read_midi,write_midi


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--sha256',required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('new output required')
    digest=hashlib.sha256(a.source.read_bytes()).hexdigest()
    if digest!=a.sha256:raise ValueError('source digest differs')
    a.output.mkdir(parents=True);rows=[]
    for i,track in enumerate(mido.MidiFile(a.source).tracks):
        if not any(e.type=='note_on' and e.velocity>0 for e in track):continue
        row=dict(track_index=i)
        try:
            melody=read_midi(a.source,i);out=a.output/f'track-{i}.mid';write_midi(melody,out)
            if read_midi(out,1)!=melody:raise AssertionError('modeled state mismatch')
            row.update(status='technical_pass_not_rights_admission',notes=len(melody.notes),roundtrip=True,
                meter_map=[vars(x) for x in melody.meter_map],output_sha256=hashlib.sha256(out.read_bytes()).hexdigest())
        except ValueError as e:row.update(status='rejected',reason=str(e))
        rows.append(row)
    assert hashlib.sha256(a.source.read_bytes()).hexdigest()==digest
    root=Path(__file__).resolve().parents[1]
    report=dict(source_sha256=digest,original_unchanged=True,tracks=rows,model_fit=False,model_score=False,
        code_sha256={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ['src/mousa/variable_meter_midi.py','tools/probe_variable_meter_intake.py']})
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(rows))
if __name__=='__main__':main()
