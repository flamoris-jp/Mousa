import importlib.util
from pathlib import Path
import tempfile
import unittest
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('weak',ROOT/'experiments/maidionis-progression-corpus/extract_weak.py')
weak=importlib.util.module_from_spec(spec);spec.loader.exec_module(weak)

class WeakChordTests(unittest.TestCase):
    def bar(self,extra='',pitches=(60,64,67),kind='whole'):
        return '<Measure><voice><KeySig><accidental>0</accidental></KeySig><TimeSig><sigN>4</sigN><sigD>4</sigD></TimeSig>'+extra+'<Chord><durationType>'+kind+'</durationType>'+''.join('<Note><pitch>'+str(p)+'</pitch></Note>' for p in pitches)+'</Chord></voice></Measure>'
    def run_xml(self,body,version='3.01',copyright='OpenScore (CC0)',part=''):
        xml='<museScore version="'+version+'"><Score><metaTag name="copyright">'+copyright+'</metaTag>'+part+'<Staff id="1">'+body+'</Staff></Score></museScore>'
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'score.mscx';p.write_text(xml);return weak.extract(p)
    def test_triad_and_seventh(self):
        for pitches,label in [((60,64,67),0),((60,64,67,71),7),((67,71,74,77),11)]:
            result=self.run_xml(self.bar(pitches=pitches));bar=result['bars'][0]
            self.assertEqual(bar['label'],label);self.assertEqual(bar['width_qb'],'4');self.assertEqual(bar['notehead_count'],len(pitches))
            self.assertEqual(sum(Fraction(x) for x in bar['pitch_duration_qb']),4*len(pitches))
    def test_null_bar_preserved_and_position_not_compressed(self):
        result=self.run_xml(self.bar()+self.bar(extra='<Tuplet/>')+self.bar())
        self.assertEqual([x['label'] for x in result['bars']],[0,None,0])
        self.assertEqual([x['measure_index'] for x in result['bars']],[0,1,2])
        self.assertEqual([x['score_start_qb'] for x in result['bars']],['0','4','8'])
    def test_annotations_and_lyrics_not_used(self):
        normal=self.run_xml(self.bar());annotated=self.run_xml(self.bar(extra='<Harmony><name>FALSE_LABEL</name></Harmony><StaffText><text>DO NOT READ</text></StaffText>'))
        self.assertEqual(normal['bars'],annotated['bars'])
    def test_spanner_reference_locations_do_not_move_cursor(self):
        references='<Spanner type="Slur"><next><location><measures>1</measures><fractions>1/4</fractions></location></next><prev><location><measures>-1</measures></location></prev></Spanner>'
        plain=self.run_xml(self.bar())
        # Both voice-level and note/chord spanners use references, not timing commands.
        inside=self.bar().replace('<durationType>whole</durationType>','<durationType>whole</durationType>'+references)
        self.assertEqual(self.run_xml(self.bar(extra=references))['bars'],plain['bars'])
        self.assertEqual(self.run_xml(inside)['bars'],plain['bars'])
        self.assertIsNone(self.run_xml(self.bar(extra='<location><fractions>1/4</fractions></location>'))['bars'][0]['label'])
    def test_volta_spanner_rejects_entire_score(self):
        for volta in ('<Spanner type="Volta"><next><location><measures>2</measures></location></next></Spanner>', '<Volta/>'):
            with self.assertRaisesRegex(ValueError,'volta_span'):
                self.run_xml(self.bar()+self.bar(extra=volta)+self.bar())
    def test_global_rejections(self):
        for kwargs in ({'version':'2.06'},{'copyright':'unknown'},{'part':'<Part><Instrument><transposeChromatic>2</transposeChromatic></Instrument></Part>'}):
            with self.assertRaises(ValueError):self.run_xml(self.bar(),**kwargs)
        with self.assertRaises(ValueError):self.run_xml(self.bar()+self.bar().replace('<accidental>0','<accidental>1'))
        with self.assertRaises(ValueError):self.run_xml(self.bar()+self.bar().replace('<sigN>4','<sigN>3'))
    def test_bar_rejections(self):
        for extra in ('<location/>','<Tuplet/>','<grace16/>','<Jump/>','<Tremolo/>'):
            self.assertIsNone(self.run_xml(self.bar(extra=extra))['bars'][0]['label'])
        self.assertIsNone(self.run_xml(self.bar(kind='half'))['bars'][0]['label'])
        self.assertIsNone(self.run_xml(self.bar().replace('<Measure>','<Measure len="1/4">'))['bars'][0]['label'])
    def test_profile_confidence(self):
        self.assertIsNone(weak.choose([0]*12,0)['label'])
        self.assertIsNone(weak.choose([1]*12,0)['label'])
        self.assertIsNone(weak.choose([1,0,0,0,1,0,0,0,0,0,0,0],0)['label'])
    def test_dotted_duration_and_explicit_check(self):
        import xml.etree.ElementTree as ET
        e=ET.fromstring('<Rest><durationType>half</durationType><dots>1</dots><duration>3/4</duration></Rest>')
        self.assertEqual(weak.duration(e,Fraction(4)),3)
        e.find('duration').text='1/2'
        with self.assertRaises(ValueError):weak.duration(e,Fraction(4))
