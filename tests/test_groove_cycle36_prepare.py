import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

class GrooveCycle36Tests(unittest.TestCase):
    def test_complete_selection_nested_order_and_no_holdout(self):
        tools=Path(__file__).resolve().parents[1]/'tools'
        with patch.object(sys,'path',[str(tools),*sys.path]):
            spec=importlib.util.spec_from_file_location('groove36',tools/'groove_cycle36_prepare.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        rows=[]
        for drummer in (1,6,7):
            for i in range(9):
                rows.append({'id':f'{drummer}/{i}','drummer':f'drummer{drummer}','session':f'drummer{drummer}/'+('eval_session' if i==0 else 'session1'),'sha256':str(i).zfill(64),'metrics':{'note_on_positive':4097 if i==1 else 12}})
        chosen,excluded=m.select_training(list(reversed(rows)))
        self.assertEqual([r['id'] for r in chosen],[f'{d}/{i}' for d in (1,6) for i in range(2,8)])
        self.assertEqual(set(excluded),{'1/1','6/1'})
        self.assertEqual([r['metrics']['note_on_positive'] for r in chosen],[12]*12)
