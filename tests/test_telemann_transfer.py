"""Blocked independent intake must never become a predictive result."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
try:
    spec = importlib.util.spec_from_file_location('telemann_transfer_test', TOOLS / 'evaluate_telemann1692_transfer.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
finally:
    sys.path.pop(0)


class TelemannBlockedTransferTests(unittest.TestCase):
    def test_flagged_prescore_blocks_even_with_nominal_clearance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'source.mid'
            source.write_bytes(b'synthetic fixture, never parsed')
            plan = dict(source={'sha256': module.digest(source)}, code_sha256={})
            (root / 'plan.json').write_text(json.dumps(plan))
            screen = dict(plan_sha256=module.digest(root / 'plan.json'), any_flagged=True,
                          coverage={'unsupported_events': []})
            (root / 'prescore-screen.json').write_text(json.dumps(screen))
            clearance = root / 'clearance.json'
            clearance.write_text(json.dumps(dict(status='cleared', source_sha256=module.EXPECTED,
                                                flagged=False, screen_threshold=.80)))
            with patch.object(module, 'OnsetGateModel') as model:
                with self.assertRaisesRegex(ValueError, 'screen or coverage blocks'):
                    module.score(root, root, source, root, root / 'output', clearance)
                model.assert_not_called()
            self.assertFalse((root / 'output').exists())

    def test_fixed_target_and_track(self):
        self.assertEqual(module.EXPECTED, '1e874885b369855fa948121e0635921a2debc6199a6fc251d85347f6678e26af')
        self.assertEqual(len(module.TRAIN_IDS), 4)
