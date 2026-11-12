"""Lossless selected-note onset view, not voice or melody ground truth.

Source indices preserve the exact input tuple order as well as all TickNote
fields. Metadata, control/channel-event order and MIDI bytes remain in the
original object/file, not in this note-only view. No quantization or gate change.
"""
from dataclasses import dataclass
from mousa.tick_midi import TickNote


@dataclass(frozen=True)
class IndexedNote:
    source_index: int
    note: TickNote


@dataclass(frozen=True)
class OnsetGroup:
    onset: int
    members: tuple[IndexedNote, ...]


def _note(note, total_ticks):
    if not isinstance(note, TickNote):
        raise ValueError('TickNote required')
    values = (note.start, note.end, note.pitch, note.velocity, note.release_velocity)
    if any(type(v) is not int for v in values):
        raise ValueError('integer note fields required')
    if not 0 <= note.start < note.end <= total_ticks or not 0 <= note.pitch <= 127:
        raise ValueError('note outside timeline or pitch range')
    if not 1 <= note.velocity <= 127 or not 0 <= note.release_velocity <= 127:
        raise ValueError('invalid velocities')


def _timeline(total_ticks):
    if type(total_ticks) is not int or not 1 <= total_ticks <= 32767 * 1024:
        raise ValueError('bounded positive timeline required')


def group_notes(notes, total_ticks):
    _timeline(total_ticks)
    if not isinstance(notes, (tuple, list)) or len(notes) > 4096:
        raise ValueError('bounded note sequence required')
    by_onset = {}
    for index, note in enumerate(notes):
        _note(note, total_ticks)
        by_onset.setdefault(note.start, []).append(IndexedNote(index, note))
    return tuple(OnsetGroup(onset, tuple(members)) for onset, members in sorted(by_onset.items()))


def restore_notes(groups, total_ticks):
    _timeline(total_ticks)
    if not isinstance(groups, (tuple, list)) or len(groups) > 4096:
        raise ValueError('bounded group sequence required')
    indexed = {}; previous = -1
    for group in groups:
        if not isinstance(group, OnsetGroup) or type(group.onset) is not int or group.onset <= previous:
            raise ValueError('strictly ordered onset groups required')
        if type(group.members) is not tuple or not group.members:
            raise ValueError('nonempty immutable group required')
        previous = group.onset
        for member in group.members:
            if not isinstance(member, IndexedNote) or type(member.source_index) is not int or not 0 <= member.source_index < 4096:
                raise ValueError('bounded original index required')
            if member.source_index in indexed:
                raise ValueError('duplicate source index')
            _note(member.note, total_ticks)
            if member.note.start != group.onset:
                raise ValueError('group onset mismatch')
            indexed[member.source_index] = member.note
    if set(indexed) != set(range(len(indexed))):
        raise ValueError('missing source index')
    return tuple(indexed[i] for i in range(len(indexed)))
