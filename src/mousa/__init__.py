"""Experimental Mousa note-only MusicIR; not a MIDI parser or a trained model."""

from .music_ir import MusicIR, NoteEvent
from .scales import Key, Scale, ScaleCondition, load_catalogue

__all__ = ["MusicIR", "NoteEvent", "Key", "Scale", "ScaleCondition", "load_catalogue"]
