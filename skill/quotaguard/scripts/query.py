"""Portable quota sensing and time-aware pacing; standard library only."""
from __future__ import annotations
import argparse
import json
import math
import os
from pathlib import Path
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent / 'vendor'))
from quotaguard.quota.reader import QuotaReader

REFERENCE = 12.0

def level_for(rate):
    if rate is None:
        return 'UNKNOWN'
    if rate < 6:
        return 'TIGHT'
    if rate < 12:
        return 'CONSERVATIVE'
    if rate < 18:
        return 'COMFORTABLE'
    return 'ABUNDANT'

def describe(status, now=None):
    now = time.time() if now is None else now
    result = status.to_dict()
    result['evaluated_at'] = datetime.fromtimestamp(now, timezone.utc).isoformat()
    for name in ('five_hour', 'weekly'):
        window = result[name]
        if window is not None:
            reset = window['resets_at']
            seconds = None if reset is None else max(0, math.ceil(reset - now))
            window['seconds_until_reset'] = seconds
            try:
                window['reset_time_local'] = None if reset is None else datetime.fromtimestamp(reset).astimezone().isoformat()
            except (OverflowError, OSError, ValueError):
                window['reset_time_local'] = None
    window = result['five_hour']
    rate = None
    hours = None
    if window and window['window_minutes'] == 300 and window['resets_at'] is not None:
        seconds = window['resets_at'] - now
        if seconds > 0:
            hours = seconds / 3600
            rate = window['remaining_percent'] / hours
    reasons = []
    if status.source != 'app_server':
        reasons.append('Not a live reading; do not treat a log snapshot as current.')
    if hours is None:
        reasons.append('A future reset for a 300-minute window is required for pacing.')
    if window and window['remaining_percent'] == 0:
        reasons.append('The current window has no remaining quota; a high future budget cannot restore it.')
    if hours is not None and hours < 0.25:
        reasons.append('Reset is close: the ratio can be large while absolute quota stays small.')
    weekly = result['weekly']
    if weekly and weekly['remaining_percent'] < 20:
        reasons.append('Weekly quota is low; a high five-hour rate does not override it.')
    result['pacing'] = {
        'remaining_hours': hours,
        'percentage_points_per_hour': rate,
        'reference': REFERENCE,
        'level': level_for(rate) if status.source == 'app_server' else 'UNKNOWN',
        'cautions': reasons,
    }
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', choices=['app-server', 'session', 'auto'], default='app-server')
    args = parser.parse_args()
    # The Windows npm shim cannot be launched as a native executable.
    if os.name == 'nt' and not os.environ.get('QUOTAGUARD_CODEX_COMMAND'):
        appdata = os.environ.get('APPDATA')
        if appdata:
            base = Path(appdata) / 'npm/node_modules/@openai/codex/node_modules/@openai'
            binaries = sorted(base.glob('codex-win32-*/vendor/*/bin/codex.exe'))
            if binaries:
                os.environ['QUOTAGUARD_CODEX_COMMAND'] = str(binaries[0])
    result = describe(QuotaReader().read(args.source))
    print(json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
