"""Synthetic-only protocol, label, sampler and independently parsed MIDI tests."""
import importlib.util
import io
from pathlib import Path
import random
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('progression_audition', Path(__file__).resolve().parents[1] / 'experiments/maidionis-progression-corpus/audition.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
try:
    import mido
except ImportError:
    mido = None


class AuditionTests(unittest.TestCase):
    def test_sampling_no_reroll(self):
        rows = []
        def query(row):
            rows.append(row)
            return [0] * 13 + [1]
        labels, trace = a.generate(query, 17)
        self.assertEqual(labels, [13] * 8)
        self.assertEqual(len(rows), 8)
        self.assertEqual(rows[0]['input'], [1] + [x + 2 for x in a.CONTEXT])
        self.assertEqual(rows[-1]['input'][2:], [15] * 7)
        self.assertEqual(len(trace), 8)

    def test_probabilities_invalid(self):
        for probabilities in ([0] * 14, [1] * 14, [float('nan')] * 14, [-1] + [0] * 13):
            with self.assertRaises(ValueError): a.sample(probabilities, random.Random(1))

    def test_reproducible(self):
        query = lambda _: [1 / 14] * 14
        self.assertEqual(a.generate(query, 29), a.generate(query, 29))

    def test_match_both_windows_and_dedup(self):
        labels = a.CONTEXT
        row = {'input': [1] + [x + 2 for x in labels], 'label': 1, 'family': 'synthetic', 'index': 8}
        self.assertEqual(a.train_matches(labels, {'train': [row, row]}), [('synthetic', 0)])
        self.assertEqual(a.train_matches(labels[1:] + [1], {'train': [row]}), [('synthetic', 1)])
        self.assertEqual(a.train_matches([13] * 8, {'train': [row]}), [])

    def test_strict_task_context_mapping(self):
        for task, context in a.TASK_CONTEXTS.items():
            self.assertEqual(a.model_context({'task_id': task, 'context_length': context}), context)
            for bad in (None, True, str(context), 2 if context == 8 else 8):
                with self.assertRaises(ValueError):
                    a.model_context({'task_id': task, 'context_length': bad})
        with self.assertRaises(ValueError): a.model_context({'task_id': 'unknown', 'context_length': 2})

    def test_local2_generation_suffix_only(self):
        rows = []
        def query(row):
            rows.append(row)
            return [0] * 13 + [1]
        labels, trace = a.generate(query, 43, 2)
        self.assertEqual(labels, [13] * 8)
        self.assertEqual(rows[0]['input'], [1, 7, 5])
        self.assertEqual(rows[1]['input'], [1, 5, 15])
        self.assertEqual(rows[2]['input'], [1, 15, 15])
        self.assertTrue(all(len(r['input']) == 3 for r in rows))
        self.assertEqual(len(trace), 8)

    def test_local2_limited_diagnostic(self):
        row = {'input': [1, 2, 6], 'label': 5}
        result = a.match_diagnostic(a.CONTEXT, {'train': [row]}, 2)
        self.assertFalse(result['eight_chord_exact_check_performed'])
        self.assertNotIn('train_eight_chord_exact_matches', result)
        diag = result['limited_trigram_diagnostic']
        self.assertEqual(diag['window_count'], 6)
        self.assertEqual(diag['matched_count'], 2)
        self.assertAlmostEqual(diag['match_rate'], 1 / 3)
        with self.assertRaises(ValueError):
            a.match_diagnostic(a.CONTEXT, {'train': [{'input': [1, 2], 'label': 0}]}, 2)

    def test_output_rejects_real_git_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            self.assertTrue(a.output_in_git_worktree(root / 'new' / 'audio'))
            nested = root / 'existing'
            nested.mkdir()
            self.assertTrue(a.output_in_git_worktree(nested / 'new'))

    def test_output_accepts_placeholder_git_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / '.git').mkdir()
            self.assertFalse(a.output_in_git_worktree(root / 'new' / 'audio'))

    def test_readme_context_disclosure(self):
        self.assertIn('末尾2コード（vi-IV）のみ', a.readme(2))
        self.assertIn('直前2コードだけ', a.readme(2))
        self.assertIn('3連続コード', a.readme(2))
        self.assertIn('直前8コード', a.readme(8))
        with self.assertRaises(ValueError): a.readme(3)

    @unittest.skipIf(mido is None, 'mido optional independent parser')
    def test_midi_all_labels_and_identical_melody(self):
        melodies = []
        for labels in (a.CONTEXT, list(range(8)), list(range(6, 14))):
            raw, progression = a.render(labels)
            midi = mido.MidiFile(file=io.BytesIO(raw))
            self.assertEqual(midi.ticks_per_beat, 480)
            self.assertEqual(progression['bars'], 8)
            self.assertAlmostEqual(midi.length, 19.2)
            tick = 0
            melody = []
            active = set()
            for msg in midi.tracks[0]:
                tick += msg.time
                if msg.type == 'note_on':
                    self.assertNotIn((msg.channel, msg.note), active)
                    active.add((msg.channel, msg.note))
                    self.assertEqual(msg.velocity, 48 if msg.channel == 0 else 80)
                    self.assertIn(msg.note % 12, (0, 2, 4, 5, 7, 9, 11))
                    if msg.channel == 1: melody.append((tick, msg.note, msg.velocity))
                elif msg.type == 'note_off': active.remove((msg.channel, msg.note))
            self.assertEqual(tick, 15360)
            self.assertFalse(active)
            self.assertEqual(len(melody), 64)
            melodies.append(melody)
        self.assertEqual(melodies[0], melodies[1])
        self.assertEqual(melodies[1], melodies[2])


if __name__ == '__main__': unittest.main()
