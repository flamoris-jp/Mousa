"""Synthetic checks only: no corpus, checkpoint or fitting required."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from mousa.rhythm_learning import encode

ROOT = Path(__file__).resolve().parents[1]/'experiments/maidionis-rhythm-first'
def module(name):
    spec=importlib.util.spec_from_file_location('rf_'+name,ROOT/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class Preparation(unittest.TestCase):
    def source(self):
        history=[[65+i%2,11,8,3,2,0] for i in range(8)]
        labels=[65,5,3,2,2,0]
        return {split:[{'input':encode(history,7,12,t),'label':y,'task':t,
                        'family':split,'target_index':8} for t,y in enumerate(labels)]
                for split in ('train','test')}
    def test_only_pitch_gets_true_current_rhythm(self):
        source=self.source();before=json.dumps(source);arms=module('prepare').prepare(source)
        self.assertEqual(before,json.dumps(source))
        for split in ('train','test'):
            for a,b,orig in zip(arms['independent'][split],arms['rhythm_first'][split],source[split]):
                self.assertEqual(a['input'][:51],orig['input'])
                expected=list(orig['input'])
                if orig['task'] != 0:
                    for at in range(3,51,6):expected[at]=183
                self.assertEqual(b['input'][:51],expected)
                self.assertEqual(a['input'][51:],[0,0,0])
                self.assertEqual(b['input'][51:],[316,362,409] if orig['task']==0 else [0,0,0])
                for k in ('label','task','family','target_index'):
                    self.assertEqual(a[k],b[k]);self.assertEqual(a[k],orig[k])
    def test_duplicate_rejected(self):
        src=self.source();src['train'].append(src['train'][0])
        with self.assertRaises(ValueError):module('prepare').prepare(src)
    def test_inconsistent_current_rest_rejected(self):
        src=self.source();src['train'][3]['label']=3
        with self.assertRaises(ValueError):module('prepare').prepare(src)

class FakeProcess:
    def __init__(self):
        self.stdin=self;self.stdout=self;self.returncode=0;self.requests=[]
    def write(self,text):self.requests.append(json.loads(text))
    def flush(self):pass
    def close(self):pass
    def wait(self,timeout):return 0
    def readline(self):
        rows=[]
        for r in self.requests[-1]:
            task=r['task'];width=(192,48,48,49,4,2)[task];label=(65,47,47,0,2,0)[task]
            p=[0.0]*width;p[label]=1.0;rows.append({'probabilities':p})
        return json.dumps(rows)+'\n'

class Generation(unittest.TestCase):
    def test_actual_sampled_context_and_request_order(self):
        g=module('generate')
        for arm in ('independent','rhythm_first'):
            with self.subTest(arm=arm),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);refs=root/'refs.json';refs.write_text('{"references": [{}]}')
                gate=root/'gate.py';gate.write_text("REFERENCE_SHA='x'\ndef sha(path):return 'x'\ndef copy_screen(features,refs):return {'blocked':False}\n")
                process=FakeProcess();out=root/'out'
                argv=['generate','--binary','fake','--model','fake','--arm',arm,'--references',str(refs),'--gate',str(gate),'--out',str(out)]
                with patch('sys.argv',argv),patch.object(g.subprocess,'Popen',return_value=process),patch.object(g,'write_midi',return_value='fixture'),contextlib.redirect_stdout(io.StringIO()):g.main()
                self.assertEqual(len(process.requests),48) # 3 seeds * 8 notes * 2 queries
                for seed_index in range(3):
                    requests=process.requests[seed_index*16:(seed_index+1)*16]
                    if arm=='rhythm_first':
                        # Whole eight-bar plan must exist before the FIRST pitch request.
                        timing_requests=requests[:8];degree_requests=requests[8:]
                    else:
                        timing_requests=requests[::2];degree_requests=requests[1::2]
                    for index,(timing,degree) in enumerate(zip(timing_requests,degree_requests)):
                        self.assertEqual([r['task'] for r in timing],[1,2,3,4,5])
                        self.assertTrue(all(r['input'][51:]==[0,0,0] for r in timing))
                        self.assertEqual(len(degree),1)
                        self.assertEqual(degree[0]['task'],0)
                        self.assertEqual(degree[0]['input'][51:],[358,406,407] if arm=='rhythm_first' else [0,0,0])
                        expected_history=[183]*(8-index)+[184]*index
                        self.assertEqual(degree[0]['input'][3:51:6],expected_history)
                        for row in timing:
                            self.assertEqual(row['input'][3:51:6],[183]*8 if arm=='rhythm_first' else expected_history)
                        # Current target pitch never occurs in timing query except past emitted history.
                        self.assertEqual(degree[0]['input'][2],timing[0]['input'][2])
                for seed in (101,102,103):
                    trace=json.loads((out/f'trace-{seed}.json').read_text())
                    self.assertEqual(sum(e['labels'][1]+1 for e in trace['events']),384)
                    self.assertEqual(len(trace['events']),8)
                    self.assertTrue(all(e['labels']==[65,47,47,0,2,0] for e in trace['events']))
