"""Bounded, rights-pinned 4/4 rhythm/degree preparation. No fitting or reserve reads."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from mousa.degrees import degree_for_pitch
from mousa.scales import Key, ScaleCondition, load_catalogue

SPLIT_SHA = 'a08f7201e846e09c91e79036c74fefe687e8c431e353f33163d6c935cfbad517'
ATTRIBUTION_SHA = '1d944e46d4a4b29cc893a28303286cc89e1121a093678bbc913d140e7db70f43'
TASK_WIDTHS = (192, 48, 48, 49, 4, 2)
OFFSETS = (119, 311, 359, 407, 456, 460)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def encode(history, degree_count, barpos, task):
    # This mirrored codec is independently tested against the production codec.
    if len(history) != 8 or not 1 <= degree_count <= 64 or not 0 <= barpos < 48 or not 0 <= task < 6:
        raise ValueError('invalid input shape/control')
    result = [task+1, degree_count+6, barpos+71]
    for event in history:
        if len(event) != 6:
            raise ValueError('invalid event width')
        for value, width, offset in zip(event, TASK_WIDTHS, OFFSETS):
            if type(value) is not int or not 0 <= value < width:
                raise ValueError('invalid event label')
            result.append(value+offset)
        if event[0] % 64 >= degree_count:
            raise ValueError('invalid degree')
    return result


def project(path):
    """Highest onset pitch; ties earliest track. Retain chosen note's gate/velocity."""
    import mido
    midi = mido.MidiFile(path)
    if midi.type == 2 or midi.ticks_per_beat <= 0:
        raise ValueError('unsupported asynchronous/SMPTE MIDI')
    meters, keys, notes, active_errors = [], [], {}, 0
    for track_index, track in enumerate(midi.tracks):
        tick, active = 0, {}
        for message in track:
            tick += message.time
            if message.type == 'time_signature':
                meters.append((tick, message.numerator, message.denominator))
            if message.type == 'key_signature':
                keys.append((tick, message.key))
            if message.type == 'note_on' and message.velocity > 0 and message.channel != 9:
                identity = (message.channel, message.note)
                if identity in active:
                    active_errors += 1
                active[identity] = (tick, message.velocity)
            elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
                identity = (message.channel, message.note)
                if identity in active:
                    onset, velocity = active.pop(identity)
                    note = {'onset': onset, 'end': tick, 'pitch': message.note,
                            'velocity': velocity, 'track': track_index}
                    old = notes.get(onset)
                    if old is None or (note['pitch'], -track_index) > (old['pitch'], -old['track']):
                        notes[onset] = note
        active_errors += len(active)
    if active_errors:
        raise ValueError('overlapping same-key or unclosed source note')
    if not meters or min(t for t, _, _ in meters) != 0 or any((n,d) != (4,4) for _,n,d in meters):
        raise ValueError('missing/changing/non-4/4 meter')
    if not keys or min(t for t, _ in keys) != 0 or len({key for _,key in keys}) != 1:
        raise ValueError('missing/changing/conflicting key signature')
    key_name = keys[0][1]
    scale = 'natural_minor_12tet' if key_name.endswith('m') else 'major_12tet'
    condition = ScaleCondition(load_catalogue()[scale], Key.from_name(key_name.rstrip('m')+'4'))
    return midi.ticks_per_beat, [notes[t] for t in sorted(notes)][:129], condition, key_name


def event_rows(path):
    ppq, notes, condition, key_name = project(path)
    history, examples, events, rejected = [], [], [], Counter()
    errors = {'onset': [], 'ioi': [], 'duration': []}
    overlaps = 0
    for index, (note, following) in enumerate(zip(notes, notes[1:])):
        try:
            degree = degree_for_pitch(condition, note['pitch']*100).label
        except ValueError:
            history = []
            rejected['off_scale_or_register'] += 1
            continue
        ioi = Fraction((following['onset']-note['onset'])*12, ppq)
        raw_gate = Fraction((note['end']-note['onset'])*12, ppq)
        if not 0 < ioi <= 48 or raw_gate <= 0:
            history = []
            rejected['ioi_outside_4beats_or_nonpositive_gate'] += 1
            continue
        gate = min(raw_gate, ioi)
        overlaps += int(raw_gate > ioi)
        onset = Fraction(note['onset']*12, ppq)
        qi = max(1, min(48, round(ioi)))
        qg = max(1, min(qi, round(gate)))
        rest = qi-qg
        accent = sum(note['velocity'] >= threshold for threshold in (48,80,112))
        # Weak phrase cue, not a human-annotated phrase boundary.
        phrase = int(rest >= 12)
        event = [degree, qi-1, qg-1, rest, accent, phrase]
        position = round(onset) % 48
        for name, value, quantized in [('onset',onset,round(onset)),('ioi',ioi,qi),('duration',gate,qg)]:
            errors[name].append(float(abs(value-quantized)/12))
        events.append({'target_index':index,'labels':event,'barpos':position,
                       'source_onset_ticks':note['onset'],'source_pitch':note['pitch'],
                       'source_end_ticks':note['end'],'source_velocity':note['velocity']})
        if len(history) == 8:
            examples.append({'target_index':index,'barpos':position,'history':[list(e) for e in history],
                             'labels':event})
        history = (history+[event])[-8:]
    diagnostics = {'source_notes_bounded':len(notes),'accepted_events':len(events),
                   'windows':len(examples),'rejected':dict(rejected),'overlap_gates_clipped':overlaps,
                   'quantization_max_error_beats':{k:max(v,default=0) for k,v in errors.items()},
                   'quantization_changed_values':{k:sum(x>0 for x in v) for k,v in errors.items()},
                   'key_signature':key_name,'scale_id':condition.scale.scale_id,'tonic_midi':condition.key.tonic_midi,
                   'degree_count':len(condition.scale.intervals_cents),'ticks_per_beat':ppq}
    return examples, events, diagnostics


def prepare(attribution_path, split_path, out):
    if out.exists():
        raise ValueError('new output directory required')
    if sha(attribution_path) != ATTRIBUTION_SHA:
        raise ValueError('PR17 source-attribution digest mismatch')
    if sha(split_path) != SPLIT_SHA:
        raise ValueError('split digest mismatch')
    split = json.loads(split_path.read_text())
    for key, expected in split['input_sha256'].items():
        if sha(split['input_paths'][key]) != expected:
            raise ValueError('rights dependency digest mismatch: '+key)
    rights = {c:{r['mutopia_id']:r for r in json.loads(Path(split['input_paths'][c+'_rights']).read_text())['records']}
              for c in ('pd','by')}
    allowed = {c:json.loads(Path(split['input_paths'][c+'_allowlist']).read_text())['files'] for c in ('pd','by')}
    members = {r['family_id']:r for r in split['members']}
    attribution = json.loads(attribution_path.read_text())
    # Only the existing PR17 source list, never the other split/reserve raw files.
    sources = attribution['sources']
    if Counter(r['cohort'] for r in sources) != {'train':128,'historical_observed':16}:
        raise ValueError('unexpected PR17 cohort')
    if len({s['family_id'] for s in sources}) != 144:
        raise ValueError('source family repeated across cohorts')
    output = {'schema':'mousa.degree-rhythm-training.experimental.v1',
              'task_id':'mousa.degree-rhythm.experimental.v1','train':[],'test':[]}
    private = {'sources':[], 'sequences':[], 'exclusions':[]}
    totals = Counter()
    for source in sources:
        cohort = source['cohort']
        if totals[cohort] >= (8 if cohort == 'train' else 4):
            continue
        member = members[source['family_id']]
        corpus = member['corpus']
        expected_role = 'train' if cohort == 'train' else 'test'
        if corpus not in ('pd','by') or member['split'] != expected_role or source['split'] != expected_role:
            raise ValueError('corpus/cohort mismatch')
        if 'ShareAlike' in member['license'] or not rights[corpus][member['selected_source_id']]['rights_eligible']:
            raise ValueError('source rights not eligible')
        match = [f for f in allowed[corpus] if f['path']==member['midi_relative_path'] and f['sha256']==member['sha256']]
        if len(match)!=1 or not match[0]['eligible_for_note_event_training']:
            raise ValueError('exact-file admission mismatch')
        if source['source_path'] != member['source_path'] or source['sha256'] != member['sha256'] or sha(source['source_path']) != member['sha256']:
            raise ValueError('raw source identity mismatch')
        try:
            examples, events, diagnostics = event_rows(source['source_path'])
            if not examples:
                raise ValueError('no eight-prior-event contiguous window')
        except ValueError as error:
            private['exclusions'].append({'family':source['family_id'],'cohort':cohort,'reason':str(error)})
            continue
        totals[cohort] += 1
        family = source['family_id']; partition = 'train' if cohort == 'train' else 'test'
        for sample in examples:
            for task,label in enumerate(sample['labels']):
                output[partition].append({'input':encode(sample['history'],7,sample['barpos'],task),
                                          'label':label,'task':task,'family':family,
                                          'target_index':sample['target_index']})
        private['sources'].append(source | {'diagnostics':diagnostics})
        private['sequences'].append({'family':family,'cohort':cohort,'events':events,'examples':examples})
    if totals != {'train':8,'historical_observed':4}:
        raise ValueError('insufficient eligible sources: '+str(totals))
    if {r['family'] for r in output['train']} & {r['family'] for r in output['test']}:
        raise ValueError('family leakage')
    receipt = {'schema':'mousa.rhythm-preparation-receipt.v1','status':'prepared_not_fitted',
               'families':dict(totals),'task_rows':{k:len(output[k]) for k in ('train','test')},
               'attribution_sha256':sha(attribution_path),'split_sha256':SPLIT_SHA,
               'data_sha256':hashlib.sha256(encoded(output)).hexdigest(),
               'prepare_sha256':sha(__file__),'reserve_raw_files_read':0,
               'evaluation':'historical already-observed composition-family-separated diagnostic, not fresh heldout',
               'projection':'highest pitch at each onset, earliest-track tie; truncate to next onset, quantize to 1/12beat; no pitch snapping',
               'weak_labels':'rest is projected gap, not notated rest; phrase = projected quantized rest >=1beat; accent fixed velocity thresholds48/80/112',
               'bounds':'first129onsets / at most128events per file; first8train/4historical eligible in pinned source-list order; contiguous8prior-event windows only'}
    out.mkdir(parents=True,exist_ok=False)
    (out/'data.json').write_bytes(encoded(output));(out/'sources-private.json').write_bytes(encoded(private))
    (out/'preparation-receipt.json').write_bytes(encoded(receipt))
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('attribution','split','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.attribution,args.split,args.out),indent=2))
