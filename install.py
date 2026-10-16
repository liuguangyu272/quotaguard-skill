"""Install the bundled skill without downloading code or overwriting an existing skill."""
import argparse
import os
from pathlib import Path
import shutil

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dest', type=Path, help='Parent skills directory (default: CODEX_HOME/skills)')
    args = p.parse_args()
    base = args.dest or (Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills')
    target = base.expanduser().resolve() / 'quotaguard'
    if target.exists():
        p.error(f'{target} already exists. Back up or rename it before installing.')
    source = Path(__file__).resolve().parent / 'skill' / 'quotaguard'
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    print(f'Installed: {target}')
    print('On your next turn, invoke: $quotaguard Check my quota and reset time.')

if __name__ == '__main__':
    main()
