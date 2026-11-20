"""Private analytic-tone preview preserving overlapping gates, not release media."""
import argparse
from array import array
import hashlib
import json
from math import sin, pi
from pathlib import Path
import sys
import wave
from mousa.overlap_midi import read_midi


def samples(notes,total_ticks,ppq=384,tempo=500000,rate=22050):
    if not 1<=total_ticks<=384*128 or ppq!=384 or tempo!=500000 or rate!=22050:
        raise ValueError('bounded fixed preview clock required')
    if len(notes)>256:raise ValueError('note budget exceeded')
    scale=tempo/1000000/ppq
    frames=round(total_ticks*scale*rate);mix=array('d',[0.0])*frames
    for note in notes:
        if not 0<=note.start<note.end<=total_ticks or not 0<=note.pitch<=127:
            raise ValueError('invalid note bounds')
        start=round(note.start*scale*rate);end=round(note.end*scale*rate)
        length=end-start
        if length<=0:raise ValueError('note too short for preview sample rate')
        frequency=440*2**((note.pitch-69)/12)
        if frequency*2>=rate/2:raise ValueError('harmonic exceeds Nyquist')
        attack=min(round(.005*rate),max(1,length//2));release=min(round(.02*rate),max(1,length//2))
        for i in range(length):
            envelope=min(1,i/attack,(length-1-i)/release)
            phase=2*pi*frequency*i/rate
            mix[start+i]+=.12*envelope*(.8*sin(phase)+.2*sin(2*phase))
    peak=max(map(abs,mix),default=0)
    if peak>=1:raise ValueError('clipping; do not silently normalize')
    pcm=array('h',(round(value*32767) for value in mix))
    if sys.byteorder!='little':pcm.byteswap()
    return pcm.tobytes(),dict(sample_rate=rate,frames=frames,duration_seconds=frames/rate,
                             peak_linear=peak,clipped_samples=0,fixed_gain_per_note=.12)


def render(source,output):
    if output.exists():raise ValueError('new output required')
    melody=read_midi(source,1)
    if melody.tempo_map!=((0,500000),):raise ValueError('preview requires exact fixed120BPM, no tempo conversion')
    data,meta=samples(melody.notes,melody.total_ticks,melody.ppq)
    with wave.open(str(output),'wb') as stream:
        stream.setnchannels(1);stream.setsampwidth(2);stream.setframerate(22050);stream.writeframes(data)
    return dict(**meta,notes=len(melody.notes),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                wav_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                renderer='Analytic sine plus secondharmonic; fixed gain, no external recordings or soundfont',
                gates='Every note rendered independently into shared buffer; overlap and endpoint silence retained',
                quality='No human rating, not a Cantabile render or release clearance')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(render(a.source,a.output),indent=2))
