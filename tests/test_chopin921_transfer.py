"""Admission regressions use synthetic files; never score the reserved source."""
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
    spec = importlib.util.spec_from_file_location('chopin_transfer_test', TOOLS / 'evaluate_chopin921_transfer.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
finally:
    sys.path.pop(0)


class ChopinAdmissionTests(unittest.TestCase):
    def test_invalid_clearance_and_local_screen_fail_before_read_or_fit(self):
        valid = dict(status='cleared', source_sha256=module.EXPECTED,
                     flagged=False, screen_threshold=.80)
        cases = [('absent', {}, False, []),
                 ('flagged', dict(valid, flagged=True), False, []),
                 ('wrong_source', dict(valid, source_sha256='other'), False, []),
                 ('wrong_threshold', dict(valid, screen_threshold=.81), False, []),
                 ('missing_flag', {k:v for k,v in valid.items() if k!='flagged'}, False, []),
                 ('local_match', valid, True, []),
                 ('unsupported', valid, False, [dict(reason='incompatible_PPQ384')])]
        for label, decision, flagged, unsupported in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                plan_dir = root / 'plan'; plan_dir.mkdir()
                source = root / 'synthetic.mid'; source.write_bytes(b'not real MIDI')
                plan = dict(code_sha256={}, source=dict(sha256=module.digest(source)))
                (plan_dir / 'plan.json').write_text(json.dumps(plan))
                screen = dict(plan_sha256=module.digest(plan_dir/'plan.json'),
                              any_flagged=flagged, coverage=dict(unsupported_events=unsupported))
                (plan_dir / 'prescore-screen.json').write_text(json.dumps(screen))
                clearance = root / 'clearance.json'; clearance.write_text(json.dumps(decision))
                output = root / 'output'
                with patch.object(module, 'read_midi') as reader, \
                     patch.object(module, 'OnsetGateModel') as joint, \
                     patch.object(module, 'ContextOnsetGateModel') as context:
                    with self.assertRaises(ValueError):
                        module.score(root, root, source, plan_dir, output, clearance)
                    reader.assert_not_called(); joint.assert_not_called(); context.assert_not_called()
                    self.assertFalse(output.exists())

    def test_plan_or_dependency_change_fails_before_clearance(self):
        for changed in ('plan', 'dependency', 'source'):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp); plan_dir = root/'plan'; plan_dir.mkdir()
                source = root/'source'; source.write_bytes(b'synthetic')
                dependency = root/'dependency'; dependency.write_bytes(b'frozen')
                plan = dict(code_sha256={'dependency':module.digest(dependency)},
                            source=dict(sha256=module.digest(source)))
                (plan_dir/'plan.json').write_text(json.dumps(plan))
                (plan_dir/'prescore-screen.json').write_text(json.dumps(
                    dict(plan_sha256=module.digest(plan_dir/'plan.json'))))
                if changed == 'plan':
                    (plan_dir/'plan.json').write_text(json.dumps(dict(plan, changed=True)))
                elif changed == 'dependency': dependency.write_bytes(b'changed')
                else: source.write_bytes(b'changed')
                with patch.object(module, 'OnsetGateModel') as model:
                    with self.assertRaises(ValueError):
                        module.score(root, root, source, plan_dir, root/'output', root/'missing_clearance')
                    model.assert_not_called()


if __name__ == '__main__': unittest.main()
