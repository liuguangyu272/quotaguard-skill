import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('query', ROOT / 'skill/quotaguard/scripts/query.py')
query = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(query)
from quotaguard.quota.models import QuotaStatus, QuotaWindow

def sample(remaining, hours, weekly=80, source='app_server'):
    return QuotaStatus(QuotaWindow(100 - remaining, 300, int(10000 + hours * 3600)),
                       QuotaWindow(100 - weekly, 10080, 700000), source)

class ReleaseTests(unittest.TestCase):
    def test_same_quota_different_time(self):
        slow = query.describe(sample(10, 2), 10000)['pacing']
        soon = query.describe(sample(10, .25), 10000)['pacing']
        self.assertEqual((slow['percentage_points_per_hour'], slow['level']), (5, 'TIGHT'))
        self.assertEqual((soon['percentage_points_per_hour'], soon['level']), (40, 'ABUNDANT'))

    def test_boundaries(self):
        for rate, expected in [(0,'TIGHT'),(5.999,'TIGHT'),(6,'CONSERVATIVE'),(11.999,'CONSERVATIVE'),(12,'COMFORTABLE'),(17.999,'COMFORTABLE'),(18,'ABUNDANT')]:
            with self.subTest(rate=rate):
                self.assertEqual(query.level_for(rate), expected)

    def test_weekly_caution_survives_high_rate(self):
        result = query.describe(sample(50, 1, weekly=5), 10000)
        self.assertEqual(result['pacing']['level'], 'ABUNDANT')
        self.assertTrue(any('Weekly' in x for x in result['pacing']['cautions']))

    def test_expired_missing_and_nonstandard(self):
        for w in [None, QuotaWindow(20,300,None), QuotaWindow(20,300,10000), QuotaWindow(20,60,20000)]:
            result = query.describe(QuotaStatus(w,None,'app_server'),10000)
            self.assertIsNone(result['pacing']['percentage_points_per_hour'])
            self.assertEqual(result['pacing']['level'],'UNKNOWN')

    def test_stale_snapshot_is_never_live_advice(self):
        result = query.describe(sample(50,1,source='session_jsonl'),10000)
        self.assertEqual(result['pacing']['level'],'UNKNOWN')

    def test_zero_and_near_reset(self):
        result = query.describe(sample(0,.01),10000)
        self.assertEqual(result['pacing']['percentage_points_per_hour'],0)
        self.assertGreaterEqual(len(result['pacing']['cautions']),2)

    def test_installer_is_portable_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='quota skill ') as folder:
            args = [sys.executable,str(ROOT/'install.py'),'--dest',folder]
            first = subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stderr)
            script = Path(folder)/'quotaguard/scripts/query.py'
            help_result = subprocess.run([sys.executable,str(script),'--help'],capture_output=True,text=True,cwd=folder)
            self.assertEqual(help_result.returncode,0,help_result.stderr)
            self.assertNotEqual(subprocess.run(args,capture_output=True).returncode,0)

if __name__ == '__main__':
    unittest.main()
