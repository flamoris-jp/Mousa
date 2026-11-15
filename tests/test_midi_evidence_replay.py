"""Private corpus is unnecessary for rejection and historical-pin checks."""

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile


EXPERIMENT = Path(__file__).resolve().parents[1] / "experiments/maidionis-midi-learning"
SPEC = importlib.util.spec_from_file_location("midi_replay", EXPERIMENT / "replay_evidence.py")
REPLAY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPLAY)


class EvidenceReplayTests(unittest.TestCase):
    def test_historical_code_and_plan_pins(self):
        plan = json.loads((EXPERIMENT / "plan.json").read_text())
        audit = json.loads((EXPERIMENT / "native-freeze-audit.json").read_text())
        for name, expected in [
            ("plan.json", audit["plan_sha256"]),
            ("midi_diagnostic.cpp", plan["native_harness_sha256"]),
            ("freeze_native_frozen.py", plan["freeze_script_sha256"]),
            ("prepare_midi.py", plan["prepare_sha256"]),
        ]:
            self.assertEqual(hashlib.sha256((EXPERIMENT / name).read_bytes()).hexdigest(), expected)

    def test_reject_modified_archive_without_creating_output(self):
        with tempfile.TemporaryDirectory() as root:
            archive = Path(root) / "modified.zip"
            archive.write_bytes(b"not the frozen evidence")
            output = Path(root) / "output"
            with self.assertRaisesRegex(ValueError, "archive SHA-256"):
                REPLAY.replay(archive, output)
            self.assertFalse(output.exists())

    def test_reject_duplicate_zip_member(self):
        stream = io.BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(stream, "w") as archive:
                archive.writestr("plan.json", "first")
                archive.writestr("plan.json", "second")
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "duplicate.zip"
            path.write_bytes(stream.getvalue())
            with patch.object(REPLAY, "ARCHIVE_SHA256", REPLAY.digest(stream.getvalue())):
                with self.assertRaisesRegex(ValueError, "duplicate archive member"):
                    REPLAY.load_evidence(path)

    def test_reject_oversized_archive(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "oversized.zip"
            path.write_bytes(b"12345")
            with patch.object(REPLAY, "MAX_ARCHIVE_BYTES", 4):
                with self.assertRaisesRegex(ValueError, "archive too large"):
                    REPLAY.load_evidence(path)

    def test_refuse_existing_output(self):
        with tempfile.TemporaryDirectory() as root:
            sentinel = Path(root) / "data.json"
            sentinel.write_text("keep existing evidence")
            with self.assertRaises(FileExistsError):
                REPLAY.replay(Path(root) / "missing.zip", Path(root))
            self.assertEqual(sentinel.read_text(), "keep existing evidence")


if __name__ == "__main__":
    unittest.main()
