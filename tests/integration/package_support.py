"""Real wheel fixture used by installation tests; never modifies source provenance."""
import atexit
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
_workspace = None
_cli = None


def installed_cli(*arguments):
    global _workspace, _cli
    if _cli is None:
        _workspace = tempfile.TemporaryDirectory(prefix='research-os-wheel-test-')
        atexit.register(_workspace.cleanup)
        root = Path(_workspace.name).resolve()
        env = {**os.environ, 'UV_OFFLINE': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
        commands = [
            ['uv', 'build', '--wheel', '--out-dir', str(root/'dist'), str(ROOT)],
            ['uv', 'venv', str(root/'venv')],
        ]
        for command in commands:
            subprocess.run(command, check=True, capture_output=True, env=env)
        subprocess.run(['uv', 'pip', 'install', '--python', str(root/'venv/bin/python'),
                        str(next((root/'dist').glob('*.whl')))], check=True, capture_output=True, env=env)
        _cli = root/'venv/bin/research-os'
    env = {**os.environ, 'UV_OFFLINE': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
    env.pop('PYTHONPATH', None)
    return subprocess.run(['uv', 'run', '--no-project', str(_cli), *arguments],
                          cwd=_workspace.name, env=env, capture_output=True, text=True)
