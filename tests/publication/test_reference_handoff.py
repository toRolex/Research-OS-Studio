"""Reference output handoff; this is not a claim of full workflow/Lean E2E."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from research_os.publication import confirmation_text, freeze_publication, stage_publication, verify_publication
from support import fixture

ROOT = Path(__file__).resolve().parents[2]


class ReferenceHandoffTests(unittest.TestCase):
    def test_actual_computational_output_bytes_and_math_records_are_preserved(self):
        for profile in ('empirical-computational', 'mathematical-theoretical'):
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                sources = {}
                if profile == 'empirical-computational':
                    with tempfile.TemporaryDirectory() as run_dir:
                        run = Path(run_dir)
                        for name in ('experiment.py', 'data.json'):
                            data = (ROOT / 'reference-projects/computational' / name).read_bytes()
                            (run / name).write_bytes(data)
                            sources['inputs/' + name] = data
                        subprocess.run([sys.executable, str(run / 'experiment.py')], check=True)
                        sources['inputs/result.json'] = (run / 'result.json').read_bytes()
                        self.assertEqual(json.loads(sources['inputs/result.json'])['algorithm'], 'constant-mean-baseline')
                else:
                    for path in (ROOT / 'reference-projects/mathematical').rglob('*'):
                        if path.is_file() and path.name != 'README.md' and '.lake' not in path.parts:
                            name = path.relative_to(ROOT / 'reference-projects/mathematical').as_posix()
                            sources['inputs/' + name] = path.read_bytes()
                    proof = json.loads(sources['inputs/proof.json'])
                    self.assertNotEqual(proof['run_digest'], hashlib.sha256(sources['inputs/proof.json']).hexdigest())
                request, _ = fixture(root, profile, source_materials=sources)
                manifest = stage_publication(root, request)
                freeze_publication(root, manifest, confirmation_text(manifest), 'alice')
                self.assertEqual(verify_publication(root, 'first')['exit_code'], 0)
                for name, data in sources.items():
                    self.assertEqual((root / 'publications/first/files' / name).read_bytes(), data)
