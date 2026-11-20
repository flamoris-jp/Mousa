import copy
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import wave

from mousa import stem_intake as api


def fixture(root):
    """Original synthetic waveform/annotation fixture, not an artist's recording."""
    path=root/'tone.wav'
    with wave.open(str(path),'wb') as w:
        w.setparams((1,2,16000,0,'NONE','not compressed'))
        w.writeframes(b''.join(struct.pack('<h',int(6000*math.sin(2*math.pi*440*i/16000))) for i in range(16000)))
    source=dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),sizeBytes=path.stat().st_size,duration=1.,sampleRate=16000,channels=1)
    a=dict(format='flamoris.stem-analysis',schemaVersion=1,
       producer=dict(name='AudioAnalyzer',version='stem-analysis-0.1.0',workerSha256='0'*64,stemWorkerSha256='1'*64,
                     dependencies=dict(numpy='2.1.0',soundfile='0.13.1',librosa='0.11.0')),
       source=source,identity=dict(songId='song',familyId='composition-family',stemId='lead',role='vocals'),
       time=dict(unit='seconds',start=0.,end=.1,songOffset=4.25),
       audioFeatures=dict(format='flamoris.audio-features',schemaVersion=1,algorithm='stream-audio-1.0.0',mode='analyze',
          source=dict(sha256=source['sha256'],sizeBytes=source['sizeBytes'],mtimeUtcTicks='123'),duration=1.,sampleRate=11025,
          waveform=[dict(time=0.,min=-.2,max=.2,rms=.14)],bpm=None,beats=[],tonality=None,chords=[],preview=None),
       pitch=dict(method='librosa.pyin',settings=dict(sampleRate=16000,hopLength=160,frameLength=2048,fmin=65.4,fmax=1108.,resolution=.2,
                    voicingThreshold=.5,rmsThreshold=1e-4,channelMix='mean'),
          frames=[dict(time=i*.01,state='voiced',f0Hz=440.,midi=69.,voicingProbability=.9,rms=.14) for i in range(10)],
          notes=[dict(id='n1',start=0.,end=.1,pitch=69,medianMidi=69.,voicingProbabilityMean=.9,reviewState='pending')],reviewRequired=True),
       warnings=api.WARNINGS)
    return a,path


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); self.root=Path(self.tmp.name)
        self.a,self.wav=fixture(self.root); self.analysis=self.root/'analysis.json'; api.publish(self.analysis,self.a)
        self.receipt=self.root/'intake.json'; self.entry=api.intake(self.analysis,self.wav,self.receipt)
        self.review=self.root/'review.json'; self.r=api.review_template(self.receipt,self.review)

    def rewrite(self,path,value): path.write_bytes(api.canonical(value))

    def approve(self):
        self.r.update(decision='approved',reviewerId='synthetic-test-reviewer',rights=dict(trainingAllowed=True,evidenceId='original-test-fixture'),
                      notes=[dict(id='n1',start=.01,end=.09,pitch=69)])
        self.rewrite(self.review,self.r)

    def test_default_is_pending_and_not_training(self):
        self.assertFalse(self.entry['trainingEligible']); self.assertEqual(self.entry['state'],'pending_review')
        self.assertEqual(self.r['decision'],'pending'); self.assertFalse(self.r['rights']['trainingAllowed'])
        with self.assertRaises(ValueError): api.export_reviewed(self.receipt,self.review,self.root/'lessons.json')
        self.assertFalse((self.root/'lessons.json').exists())

    def test_reviewed_export_preserves_seconds_offsets_and_corrections(self):
        self.approve(); out=api.export_reviewed(self.receipt,self.review,self.root/'lessons.json')
        self.assertAlmostEqual(out['notes'][0]['songStartSeconds'],4.26)
        self.assertAlmostEqual(out['notes'][0]['durationSeconds'],.08)
        self.assertTrue(out['notes'][0]['corrected']); self.assertIsNone(out['preferenceLabel'])
        self.assertFalse(out['modelTrainingPerformed']); self.assertEqual(out['gapPolicy'],'unknown_not_inferred_as_rest')
        self.assertFalse(api.read_intake(self.receipt)['trainingEligible'])

    def test_hash_mismatched_wav(self):
        raw=bytearray(self.wav.read_bytes()); raw[-2]^=1; self.wav.write_bytes(raw)
        with self.assertRaises(ValueError): api.intake(self.analysis,self.wav,self.root/'bad.json')

    def test_analysis_and_feature_source_must_agree(self):
        self.a['audioFeatures']['source']['sha256']='f'*64
        with self.assertRaises(ValueError): api.validate_analysis(self.a)

    def test_unknown_fields_versions_roles_and_review_state(self):
        variants=[lambda a:a.update(command='run'),lambda a:a.update(schemaVersion=2),lambda a:a.update(schemaVersion=True),
          lambda a:a['identity'].update(role='arbitrary'),lambda a:a['pitch'].update(reviewRequired=False),
          lambda a:a['pitch']['notes'][0].update(reviewState='approved')]
        for change in variants:
            a=copy.deepcopy(self.a); change(a)
            with self.subTest(a=a['identity']),self.assertRaises(ValueError): api.validate_analysis(a)

    def test_bad_numerics(self):
        for val in (True,float('nan'),float('inf'),-1,'69'):
            a=copy.deepcopy(self.a); a['pitch']['notes'][0]['pitch']=val
            with self.subTest(val=val),self.assertRaises(ValueError): api.validate_analysis(a)

    def test_pitch_probability_is_not_accepted_below_threshold(self):
        self.a['pitch']['frames'][0]['voicingProbability']=.2
        with self.assertRaises(ValueError): api.validate_analysis(self.a)

    def test_unknown_frames_are_not_notes(self):
        f=self.a['pitch']['frames'][0]; f.update(state='unknown',f0Hz=None,midi=None)
        with self.assertRaises(ValueError): api.validate_analysis(self.a)
        self.a['pitch']['notes']=[]; api.validate_analysis(self.a)
        f['midi']=69
        with self.assertRaises(ValueError): api.validate_analysis(self.a)

    def test_timing_and_nonoverlap(self):
        for change in (lambda a:a['time'].update(unit='ticks'),lambda a:a['time'].update(end=2),
                       lambda a:a['pitch']['frames'][1].update(time=0),lambda a:a['pitch']['notes'][0].update(end=.3)):
            a=copy.deepcopy(self.a); change(a)
            with self.assertRaises(ValueError): api.validate_analysis(a)

    def test_features_only_roles(self):
        self.a['identity']['role']='drums'
        with self.assertRaises(ValueError): api.validate_analysis(self.a)
        self.a['pitch']=dict(method='not_applicable',settings=None,frames=[],notes=[],reviewRequired=True)
        api.validate_analysis(self.a)

    def test_same_work_family_group_not_stem_or_crop(self):
        self.a['identity'].update(stemId='second',songId='other-arrangement-label'); self.a['time']['songOffset']=12
        self.rewrite(self.analysis,self.a)
        another=api.intake(self.analysis,self.wav,self.root/'other.json')
        self.assertEqual(another['splitGroup'],self.entry['splitGroup'])
        self.assertNotEqual(another['analysisSha256'],self.entry['analysisSha256'])

    def test_intake_tampering_is_rejected(self):
        for change in (lambda e:e.update(trainingEligible=True),lambda e:e.update(splitGroup='another'),
                       lambda e:e['analysis']['identity'].update(songId='changed')):
            e=copy.deepcopy(self.entry); change(e); self.rewrite(self.receipt,e)
            with self.assertRaises(ValueError): api.read_intake(self.receipt)

    def test_review_must_bind_exact_analysis(self):
        self.approve(); self.r['analysisSha256']='a'*64; self.rewrite(self.review,self.r)
        with self.assertRaises(ValueError): api.export_reviewed(self.receipt,self.review,self.root/'bad.json')

    def test_rights_and_reviewer_explicit(self):
        for change in (lambda r:r['rights'].update(trainingAllowed=False),lambda r:r['rights'].update(trainingAllowed=1),
                       lambda r:r['rights'].update(evidenceId='unassigned'),lambda r:r.update(reviewerId='unassigned')):
            self.approve(); change(self.r); self.rewrite(self.review,self.r)
            with self.assertRaises(ValueError): api.export_reviewed(self.receipt,self.review,self.root/'bad.json')

    def test_review_note_selection_bounds(self):
        for notes in ([],[dict(id='unknown',start=0,end=.1,pitch=69)],
                      [dict(id='n1',start=0,end=.2,pitch=69)],
                      [dict(id='n1',start=0,end=.05,pitch=69),dict(id='n1',start=.05,end=.1,pitch=69)]):
            self.approve(); self.r['notes']=notes; self.rewrite(self.review,self.r)
            with self.assertRaises(ValueError): api.export_reviewed(self.receipt,self.review,self.root/'bad.json')

    def test_duplicate_and_nonfinite_json(self):
        p=self.root/'bad.json'
        for raw in ('{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}'):
            p.write_text(raw)
            with self.assertRaises(ValueError): api.load_json(p)

    def test_reject_symlinks_and_overwrite(self):
        link=self.root/'link.json'; link.symlink_to(self.analysis)
        with self.assertRaises(ValueError): api.load_json(link)
        before=self.receipt.read_bytes()
        with self.assertRaises(ValueError): api.publish(self.receipt,{})
        self.assertEqual(before,self.receipt.read_bytes())
        self.assertFalse(list(self.root.glob('.mousa-*')))

    def test_content_has_no_local_paths(self):
        self.assertNotIn(str(self.root),json.dumps(self.entry))


@unittest.skipUnless(os.environ.get('MOUSA_STEM_EXPORTER'),'set MOUSA_STEM_EXPORTER to run real producer integration')
class RealProducerIntegration(unittest.TestCase):
    def test_wav_to_analyzer_to_pending_to_reviewed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); _,wav=fixture(root)
            analysis=root/'analysis.json'
            subprocess.run([sys.executable,os.environ['MOUSA_STEM_EXPORTER'],'analyze','--input',str(wav),'--output',str(analysis),
                '--role','vocals','--song-id','integration','--family-id','integration-family','--stem-id','lead','--offset','2.5'],
                check=True,timeout=400)
            entry=api.intake(analysis,wav,root/'intake.json')
            self.assertFalse(entry['trainingEligible'])
            r=api.review_template(root/'intake.json',root/'pending.json')
            with self.assertRaises(ValueError): api.export_reviewed(root/'intake.json',root/'pending.json',root/'must-not-exist.json')
            notes=entry['analysis']['pitch']['notes']; self.assertTrue(notes)
            self.assertEqual({n['pitch'] for n in notes},{69})
            r.update(decision='approved',reviewerId='synthetic-fixture-test',rights=dict(trainingAllowed=True,evidenceId='original-synthetic'),
                     notes=[{k:n[k] for k in ('id','start','end','pitch')} for n in notes])
            api.publish(root/'approved.json',r)
            out=api.export_reviewed(root/'intake.json',root/'approved.json',root/'examples.json')
            self.assertEqual(out['splitGroup'],'work-family:integration-family')
            self.assertFalse(out['modelTrainingPerformed'])
            self.assertAlmostEqual(out['notes'][0]['songStartSeconds'],notes[0]['start']+2.5)


if __name__=='__main__': unittest.main()
