import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

PATH = Path(__file__).resolve().parents[1] / 'experiments/maidionis-coverage-control/prepare.py'
spec = importlib.util.spec_from_file_location('coverage_prepare', PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def row(family, index):
    return {'family': family, 'target_index': index, 'input': [1, 2, 3, 4, 5, 6, 7, 8, 9], 'label': 4}


class CoverageControlTests(unittest.TestCase):
    def test_complete_schedule(self):
        batches = m.schedule(4084, 42)
        self.assertEqual(len(batches), 128)
        self.assertEqual(len(batches[-1]), 20)
        self.assertEqual(sorted(sum(batches, [])), list(range(4084)))
        self.assertEqual(batches, m.schedule(4084, 42))
        self.assertNotEqual(batches, m.schedule(4084, 43))

    def test_pairing_and_no_mutation(self):
        train = [row('train', i) for i in range(35)]
        test = [row('test', 1)]
        original = copy.deepcopy((train, test))
        data = m.build(train, test)
        self.assertEqual(len(data['arms']), 6)
        self.assertEqual((train, test), original)
        self.assertEqual(data, m.build(train, test))
        for ordered, permuted in zip(data['arms'][::2], data['arms'][1::2]):
            self.assertEqual(ordered['batches'], permuted['batches'])
            self.assertEqual(ordered['seed'], permuted['seed'])
            for a, b in zip(ordered['train'], permuted['train']):
                self.assertEqual(a['label'], b['label'])
                self.assertEqual(a['target_index'], b['target_index'])
                self.assertEqual(sorted(a['input']), sorted(b['input']))

    def test_reject_overlap(self):
        with self.assertRaisesRegex(ValueError, 'overlap'):
            m.build([row('a', 1)], [row('a', 2)])

    def test_reject_duplicate_and_invalid(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            m.validate_rows([row('a', 1), row('a', 1)])
        for key, bad in [('label', 49), ('target_index', True), ('input', [1] * 9)]:
            r = row('a', 1)
            r[key] = bad
            with self.assertRaises(ValueError):
                m.validate_rows([r])

    def test_refuse_digest_and_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            source = p / 'source.json'
            source.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'digest'):
                m.prepare(source, p / 'new')
            self.assertFalse((p / 'new').exists())
            with self.assertRaisesRegex(ValueError, 'must not exist'):
                m.prepare(source, p)
