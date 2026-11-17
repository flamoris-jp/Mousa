"""Synthetic fixture semantics. No fitting, external corpus, or native build."""
import importlib.util
from pathlib import Path
import unittest

from mousa.degrees import Degree
from mousa.harmony import PATTERNS, make_progression, vary_progression, resolve_progression, TRIADS, SEVENTHS, INTERVALS
from mousa.scales import Key, ScaleCondition, load_catalogue

ROOT = Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('harmony_mechanics_prepare',ROOT/'experiments/maidionis-harmony-mechanics/prepare.py')
prepare=importlib.util.module_from_spec(spec);spec.loader.exec_module(prepare)

class HarmonyMechanics(unittest.TestCase):
    def setUp(self):
        self.condition=ScaleCondition(load_catalogue()['major_12tet'],Key.from_name('C3'))
    def test_teacher_all_roots_match_explicit_chord_quality(self):
        for root in range(7):
            for seventh in (0,1):
                quality=(SEVENTHS if seventh else TRIADS)[root]
                allowed={self.condition.pitch_cents(root,0)+100*x for x in INTERVALS[quality]}
                for gap in (0,1):
                    for phase in range(8):
                        degree=Degree.from_label(prepare.teacher(root,seventh,phase,gap),7)
                        pitch=self.condition.pitch_cents(degree.degree,degree.period)
                        self.assertIn(pitch,allowed)
    def test_fixture_labels_and_causal_history(self):
        total=0
        for pattern in PATTERNS:
            base=make_progression(pattern,repeats=2)
            for amount in (0,.5,1):
                progression,_=vary_progression(base,self.condition,amount=amount,seed=17)
                resolved=resolve_progression(progression,self.condition)
                for gap_index in (0,1):
                    rows=prepare.sequence(progression,gap_index);history=[64]*8;index=0
                    for chord,rendered in zip(progression.chords,resolved):
                        for tick in range(0,chord.duration_ticks,240*(gap_index+1)):
                            row=rows[index];self.assertEqual(row['history'],history)
                            self.assertEqual(row['family_id'],prepare.FAMILY)
                            self.assertEqual(row['degree_count'],7)
                            self.assertEqual(row['chord_root'],chord.root.degree)
                            self.assertEqual(row['chord_seventh'],int(len(INTERVALS[chord.quality])==4))
                            self.assertEqual(row['phase'],tick//240%8)
                            degree=Degree.from_label(row['target'],7)
                            self.assertIn(round(self.condition.pitch_cents(degree.degree,degree.period)/100),rendered['midi_notes'])
                            history=history[1:]+[row['target']];index+=1
                    self.assertEqual(index,len(rows));total+=index
        self.assertEqual(total,1152)
    def test_teacher_does_not_read_history_or_target(self):
        # Current target depends on four declared controls only, not hidden labels.
        self.assertEqual(prepare.teacher(0,0,0,0),64)
        self.assertEqual(prepare.teacher(0,0,1,0),66)
        self.assertEqual(prepare.teacher(0,0,2,0),68)
        self.assertEqual(prepare.teacher(0,1,3,0),70)
        self.assertEqual(prepare.teacher(6,1,3,0),133)
    def test_one_family_train_only_protocol(self):
        import json
        protocol=json.loads((ROOT/'experiments/maidionis-harmony-mechanics/protocol.json').read_text())
        self.assertIn('train-only',protocol['training'])
        self.assertIn('no heldout',protocol['evaluation'])
        self.assertIn('no trusted chord timelines',protocol['blocker'])
