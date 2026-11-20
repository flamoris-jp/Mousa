"""Narrow, fail-closed redundant-off experiment; not a general MIDI repair tool."""

def audit_track(messages, expected_indices, expected_tick, channel, pitch):
    """Return absolute events and removal ledger under unique active-key semantics."""
    active = {}; events = []; removed = []; tick = 0
    for index, message in enumerate(messages):
        if not isinstance(message.time, int) or message.time < 0:
            raise ValueError('negative/non-integer delta')
        tick += message.time
        if not isinstance(tick, int) or tick < 0:
            raise ValueError('non-integer/negative time')
        data = message.dict(); data.pop('time')
        events.append((tick, data))
        if message.type not in ('note_on', 'note_off'):
            if index in expected_indices:
                raise ValueError('target is not an off')
            continue
        key = (message.channel, message.note)
        onset = message.type == 'note_on' and message.velocity > 0
        if onset:
            if key in active or index in expected_indices:
                raise ValueError('ambiguous active key or selected onset')
            active[key] = tick
        elif key in active:
            if index in expected_indices:
                raise ValueError('selected off is necessary')
            del active[key]
        else:
            if index not in expected_indices or tick != expected_tick or key != (channel, pitch):
                raise ValueError('unexpected unmatched off')
            removed.append({'index': index, 'absolute_tick': tick, 'message': data,
                            'active_key_before': False, 'active_key_after': False})
    if active or {x['index'] for x in removed} != set(expected_indices):
        raise ValueError('dangling onset or missing expected removals')
    return events, removed

def derive(source, destination, expected_sha256):
    import hashlib
    from pathlib import Path
    import mido
    source, destination = Path(source), Path(destination)
    if destination.exists() or source.resolve() == destination.resolve():
        raise ValueError('destination must be new and separate')
    if hashlib.sha256(source.read_bytes()).hexdigest() != expected_sha256:
        raise ValueError('source digest mismatch')
    midi = mido.MidiFile(source); retained = []; ledger = []
    # A channel shared by several note tracks would require a global-state audit.
    for track in midi.tracks:
        for message in track:
            if message.type == 'control_change' and message.control != 7:
                raise ValueError('unsupported controller semantics')
            if message.type in ('sysex', 'polytouch', 'aftertouch', 'pitchwheel'):
                raise ValueError('unsupported receiver state')
    channels = []
    for track in midi.tracks:
        channels.append({m.channel for m in track if m.type in ('note_on','note_off')})
    if any(channels[i] & channels[j] for i in range(len(channels)) for j in range(i)):
        raise ValueError('cross-track note-channel sharing')
    for ti, track in enumerate(midi.tracks):
        indices = [106,109] if ti == 1 else []
        events, removed = audit_track(track, indices, 13824, 0, 66)
        retained.append([e for i,e in enumerate(events) if i not in indices])
        ledger.extend(dict(track=ti, **x) for x in removed)
        replacement = mido.MidiTrack(); last = 0
        for i,(tick,data) in enumerate(events):
            if i in indices: continue
            replacement.append(track[i].copy(time=tick-last)); last=tick
        midi.tracks[ti] = replacement
    midi.save(destination)
    reread=mido.MidiFile(destination)
    if (reread.type,reread.ticks_per_beat) != (midi.type,midi.ticks_per_beat):
        raise AssertionError('header change')
    checked=[]
    for track in reread.tracks:
        events,_=audit_track(track,[],13824,0,66); checked.append(events)
    if checked != retained:
        raise AssertionError('retained absolute messages changed')
    return {'removed':ledger, 'all_retained_messages_absolute_order_fields_equal':True,
            'retained_messages':sum(map(len,retained)),
            'source_sha256':expected_sha256,
            'derived_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
            'same_original_bytes':hashlib.sha256(source.read_bytes()).hexdigest()==expected_sha256}
