"""Recovered MIDI representation, family-split and source-label trust tests.

These tests are not listening tests or proof of musical appeal.
"""
from collections import defaultdict
import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(os.environ["MOUSA_MAIDIONIS_ROOT"]).resolve()
MUSIC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "education" / "python" / "src"))
sys.path.insert(0, str(MUSIC))

import mido
from maidionis_education.contracts import canonical, digest
from maidionis_education.datasets import freeze, validate_dataset
from descriptor import build_digest, component_files, dataset_hooks, dataset_profiles, registry
from experiment import DATASET_ID, prepare_dataset, read_corpus
from midi_io import midi_tokens, tokens_to_notes, validate_tokens, write_midi

CORPUS = Path(os.environ["MOUSA_TRIAL_CORPUS"]).resolve()
MANIFEST = CORPUS / "manifest.json"
TIME = "2026-11-11T00:00:00Z"


def fixture_midi(path, notes, *, meters=((0, 4, 4),), extra=(), ppq=480):
    midi = mido.MidiFile(type=1, ticks_per_beat=ppq)
    meta, melody = mido.MidiTrack(), mido.MidiTrack()
    midi.tracks.extend([meta, melody])
    previous = 0
    for tick, numerator, denominator in meters:
        meta.append(mido.MetaMessage("time_signature", numerator=numerator,
                                     denominator=denominator, time=tick - previous))
        previous = tick
    events = []
    for start, end, pitch in notes:
        events.append((start, 1, mido.Message("note_on", note=pitch, velocity=80)))
        events.append((end, 0, mido.Message("note_off", note=pitch, velocity=0)))
    events.extend((tick, -1, event) for tick, event in extra)
    previous = 0
    for tick, _, event in sorted(events, key=lambda item: item[:2]):
        melody.append(event.copy(time=tick - previous))
        previous = tick
    midi.save(path)
    return path


def copied_corpus(destination):
    manifest = json.loads(MANIFEST.read_text())
    manifest["works"] = [w for w in manifest["works"] if w["status"] == "usable"]
    destination.mkdir()
    for work in manifest["works"]:
        for key in ("file", "source_page_file"):
            target = destination / work[key]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(CORPUS / work[key], target)
    path = destination / "manifest.json"
    path.write_bytes(canonical(manifest))
    return path, manifest


class MidiRepresentation(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "fixture.mid"

    def test_exact_grid_keeps_leading_rest_rearticulation_and_intervals(self):
        fixture_midi(self.path, [(240, 480, 57), (480, 600, 57), (720, 960, 64)])
        tokens, details = midi_tokens(self.path, 1)
        self.assertEqual(tokens, [0, 0, 2, 1, 2, 0, 9, 1] + [0] * 8)
        self.assertEqual(details["transposition_semitones"], 3)
        self.assertEqual(details["source_pitch_range"], [57, 64])
        self.assertEqual(details["normalized_pitch_range"], [60, 67])
        self.assertEqual(details["initial_rest_steps"], 2)
        self.assertEqual([(n.start, n.end, n.pitch) for n in tokens_to_notes(tokens)],
                         [(2, 4, 60), (4, 5, 60), (6, 8, 67)])

    def test_polyphony_and_overlapping_same_pitch_are_rejected(self):
        for notes, reason in [([(0, 480, 60), (240, 720, 64)], "polyphonic"),
                              ([(0, 480, 60), (240, 720, 60)], "overlapping instances")]:
            with self.subTest(notes=notes):
                fixture_midi(self.path, notes)
                with self.assertRaisesRegex(ValueError, reason):
                    midi_tokens(self.path, 1)

    def test_other_meter_and_later_meter_change_are_rejected(self):
        for meters in (((0, 3, 4),), ((0, 4, 4), (480, 2, 4))):
            with self.subTest(meters=meters):
                fixture_midi(self.path, [(0, 960, 60)], meters=meters)
                with self.assertRaisesRegex(ValueError, "constant 4/4"):
                    midi_tokens(self.path, 1)

    def test_missing_meter_is_explicitly_reported_as_default(self):
        fixture_midi(self.path, [(0, 480, 60)], meters=())
        _, details = midi_tokens(self.path, 1)
        self.assertTrue(details["meter_defaulted"])
        self.assertEqual(details["meter"], "4/4")

    def test_off_grid_onset_or_offset_is_not_rounded(self):
        for start, end in ((1, 480), (0, 479), (160, 480)):
            with self.subTest(start=start, end=end):
                fixture_midi(self.path, [(start, end, 60)])
                with self.assertRaisesRegex(ValueError, "off-grid timing"):
                    midi_tokens(self.path, 1)

    def test_stray_off_unterminated_note_and_zero_duration_are_rejected(self):
        cases = [([(0, 480, 60)], [(600, mido.Message("note_off", note=61))], "unmatched"),
                 ([], [(0, mido.Message("note_on", note=60, velocity=80))], "unterminated"),
                 ([], [(0, mido.Message("note_on", note=60, velocity=80)),
                       (0, mido.Message("note_off", note=60))], "non-positive")]
        for notes, extra, reason in cases:
            with self.subTest(reason=reason):
                fixture_midi(self.path, notes, extra=extra)
                with self.assertRaisesRegex(ValueError, reason):
                    midi_tokens(self.path, 1)

    def test_unrepresentable_pitch_range_pedal_bend_and_drums_are_rejected(self):
        cases = [([(0, 120, 48), (120, 240, 73)], [], "range exceeds"),
                 ([(0, 480, 60)], [(0, mido.Message("control_change", control=64, value=127))], "pedal"),
                 ([(0, 480, 60)], [(0, mido.Message("pitchwheel", pitch=100))], "pitch bends"),
                 ([], [(0, mido.Message("note_on", channel=9, note=60, velocity=80))], "drum")]
        for notes, extra, reason in cases:
            with self.subTest(reason=reason):
                fixture_midi(self.path, notes, extra=extra)
                with self.assertRaisesRegex(ValueError, reason):
                    midi_tokens(self.path, 1)

    def test_track_choice_must_be_explicit_and_integer(self):
        fixture_midi(self.path, [(0, 480, 60)])
        for track in (True, -1, 2, 1.0):
            with self.subTest(track=track):
                with self.assertRaisesRegex(ValueError, "explicit valid melody track"):
                    midi_tokens(self.path, track)

    def test_hold_requires_an_active_note_and_tokens_are_bounded_integers(self):
        for tokens in ([1], [0, 1], [2, 0, 1]):
            with self.subTest(tokens=tokens):
                with self.assertRaisesRegex(ValueError, "HOLD without"):
                    validate_tokens(tokens)
        for tokens in ([True], [-1], [27], [2.0]):
            with self.subTest(tokens=tokens):
                with self.assertRaisesRegex(ValueError, "token value"):
                    validate_tokens(tokens)
        self.assertEqual(validate_tokens([0, 2, 1, 1, 4, 1, 0]), [0, 2, 1, 1, 4, 1, 0])

    def test_export_reimport_preserves_articulation_and_all_grid_positions(self):
        tokens = [0, 2, 1, 2, 4, 1, 0, 9, 1, 0, 2, 1, 4, 0, 2, 1]
        report = write_midi(tokens, self.path, bpm=120)
        actual, details = midi_tokens(self.path, 1)
        self.assertEqual(actual, tokens)
        self.assertEqual(report["notes"], 7)
        self.assertEqual(details["transposition_semitones"], 0)
        self.assertEqual(report["seconds"], 2)
        with self.assertRaises(FileExistsError):
            write_midi(tokens, self.path)


class CorpusGrouping(unittest.TestCase):
    def test_chosen_sources_have_independently_inspected_shape_and_order(self):
        sources, reports = read_corpus(MANIFEST)
        expected = [
            ("mutopia-376", "train", 159, 656, [57, 74], 3, 16),
            ("mutopia-2247", "dev", 33, 256, [60, 72], 0, 0),
            ("mutopia-2245", "test", 46, 256, [57, 73], 3, 0),
        ]
        actual = [(r["work_id"], r["split"], r["source_note_count"], r["steps"],
                   r["source_pitch_range"], r["transposition_semitones"], r["initial_rest_steps"])
                  for r in reports]
        self.assertEqual(actual, expected)
        self.assertEqual(len(sources["works"]), 3)
        for source, report in zip(sources["works"], reports):
            self.assertEqual(report["track_index"], 1)
            self.assertEqual(report["source_ppq"], 384)
            self.assertFalse(report["meter_defaulted"])
            self.assertEqual(sum(token >= 2 for token in source["tokens"]), report["source_note_count"])
            self.assertEqual(source["work_sha256"], digest((CORPUS / report["file"]).read_bytes()))
        self.assertEqual(sources["works"][0]["tokens"][:16], [0] * 16)
        self.assertEqual(sources["works"][2]["tokens"][-8:], [0] * 8)

    def test_duplicate_catalog_work_or_same_midi_hash_cannot_enter_two_splits(self):
        for kind in ("catalog_id", "file_hash"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as td:
                path, manifest = copied_corpus(Path(td) / "corpus")
                first, second = manifest["works"][:2]
                if kind == "catalog_id":
                    second["work_id"] = first["work_id"]
                else:
                    second.update(file=first["file"], sha256=first["sha256"])
                path.write_bytes(canonical(manifest))
                with self.assertRaisesRegex(ValueError, "duplicate work or file"):
                    read_corpus(path)

    def test_transposed_variant_with_new_hash_and_id_is_still_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path, manifest = copied_corpus(Path(td) / "corpus")
            first, variant = manifest["works"][:2]
            midi = mido.MidiFile(path.parent / first["file"])
            for track in midi.tracks:
                for event in track:
                    if event.type in ("note_on", "note_off"):
                        event.note += 12
            variant_path = path.parent / "transposed.mid"
            midi.save(variant_path)
            variant.update(file=variant_path.name, sha256=digest(variant_path.read_bytes()))
            self.assertNotEqual(variant["sha256"], first["sha256"])
            self.assertNotEqual(variant["work_id"], first["work_id"])
            path.write_bytes(canonical(manifest))
            with self.assertRaisesRegex(ValueError, "duplicate normalized melody"):
                read_corpus(path)

    def test_source_bytes_and_license_evidence_are_both_hash_checked(self):
        for kind, message in (("file", "source MIDI digest"),
                              ("source_page_file", "source license evidence digest")):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as td:
                path, manifest = copied_corpus(Path(td) / "corpus")
                member = path.parent / manifest["works"][0][kind]
                member.write_bytes(member.read_bytes() + b"tamper")
                with self.assertRaisesRegex(ValueError, message):
                    read_corpus(path)

    def test_sources_hook_rejects_duplicate_work_even_if_splits_differ(self):
        sources, _ = read_corpus(MANIFEST)
        duplicate = copy.deepcopy(sources["works"][0])
        duplicate["split"] = "test"
        sources["works"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "duplicate source work"):
            dataset_hooks(sources)


class SourceLabelFreeze(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name) / "frozen"
        cls.sha, cls.sources, cls.imports, cls.rows, cls.manifest = prepare_dataset(MANIFEST, cls.root)
        cls.proofs = {p["sample_id"]: p for p in (
            json.loads(line) for line in (cls.root / "provenance.jsonl").read_text().splitlines())}
        cls.reg = registry()
        cls.hooks = dataset_hooks(cls.sources)
        cls.profiles = dataset_profiles(cls.sources)

    def original(self):
        row = copy.deepcopy(self.rows[0])
        return row, copy.deepcopy(self.proofs[row["sample_id"]])

    def freeze_one(self, root, row, proof):
        return freeze(root, [row], [proof], self.reg, self.hooks,
                      {**component_files(), "sources.json": canonical(self.sources)},
                      dataset_id=DATASET_ID, seed=42, created_at=TIME,
                      generator={"code_digest": build_digest(),
                                 "config_digest": self.profiles["generator"]["config_digest"]},
                      license_summary="Per-work Mutopia Public Domain declarations.",
                      limitations=["Focused source-label verification test."], purpose="research_fixture")

    def test_all_windows_stay_in_their_single_source_work_family_and_split(self):
        by_work, by_family = defaultdict(set), defaultdict(set)
        for row in self.rows:
            sha = row["input"]["work_sha256"]
            by_work[sha].add((row["family_fingerprint"], row["split"]))
            by_family[row["family_fingerprint"]].add(sha)
        self.assertEqual(len(self.rows), 1144)
        self.assertEqual(len(by_work), 3)
        self.assertTrue(all(len(bindings) == 1 for bindings in by_work.values()))
        self.assertTrue(all(len(works) == 1 for works in by_family.values()))
        for split, records in (("train", 648), ("dev", 248), ("test", 248)):
            self.assertEqual(self.manifest["counts"][split]["records"], records)
            self.assertEqual(self.manifest["counts"][split]["families"], 1)
        _, checked = validate_dataset(self.root, self.sha, self.reg, self.hooks)
        self.assertEqual(len(checked), len(self.rows))

    def test_unmodified_source_label_can_be_refrozen_and_validated(self):
        row, proof = self.original()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "control"
            sha = self.freeze_one(root, row, proof)
            _, checked = validate_dataset(root, sha, self.reg, self.hooks)
            self.assertEqual(checked, [row])

    def test_rewriting_target_and_all_proof_targets_cannot_forge_source_label(self):
        row, proof = self.original()
        forged = {"token": (row["target"]["token"] + 2) % 27}
        row["target"] = forged
        for key in ("proposed_target", "reviewed_target", "final_target"):
            proof[key] = copy.deepcopy(forged)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "forged"
            with self.assertRaisesRegex(ValueError, "verification/lineage"):
                self.freeze_one(root, row, proof)
            self.assertFalse(root.exists())

    def test_rehashed_input_context_or_position_still_must_match_source(self):
        for kind in ("context", "position"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as td:
                row, proof = self.original()
                if kind == "context":
                    row["input"]["tokens"][0] = (row["input"]["tokens"][0] + 2) % 27
                else:
                    row["input"]["position"] = (row["input"]["position"] + 1) % 16
                proof["source_digest"] = digest(canonical(row["input"]))
                with self.assertRaisesRegex(ValueError, "verification/lineage"):
                    self.freeze_one(Path(td) / "forged", row, proof)

    def test_changed_proof_ancestry_or_source_digest_is_rejected(self):
        for kind, reason in (("ancestry", "verification/lineage"),
                             ("source_digest", "provenance binding")):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as td:
                row, proof = self.original()
                proof[kind] = ["0" * 64] if kind == "ancestry" else "0" * 64
                with self.assertRaisesRegex(ValueError, reason):
                    self.freeze_one(Path(td) / "forged", row, proof)

    def test_individual_window_cannot_move_to_another_split(self):
        row, proof = self.original()
        row["split"] = "test" if row["split"] != "test" else "train"
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "family/split mismatch"):
                self.freeze_one(Path(td) / "forged", row, proof)

    def test_source_inventory_tamper_cannot_validate_with_original_digest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "copy"
            shutil.copytree(self.root, root)
            altered = copy.deepcopy(self.sources)
            altered["works"][0]["tokens"][8] = 2
            (root / "sources.json").write_bytes(canonical(altered))
            with self.assertRaises(ValueError):
                validate_dataset(root, self.sha, self.reg, self.hooks)


if __name__ == "__main__":
    unittest.main()
