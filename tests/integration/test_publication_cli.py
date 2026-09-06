"""Current staged Publication CLI, not the removed one-member tracer."""
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.test_walking_skeleton import run_cli, report, write_json
from tests.publication.support import fixture
from research_os.publication import stage_publication, confirmation_text


class PublicationCLIIntegrationTests(unittest.TestCase):
    def test_explicit_final_digest_freeze_is_non_overwriting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request, _ = fixture(root)
            manifest = stage_publication(root, request)
            write_json(root / 'stage.json', manifest)
            args = ('freeze-publication', '--project', str(root), '--manifest', 'stage.json',
                    '--principal', 'alice', '--confirm', confirmation_text(manifest))
            result = run_cli(*args)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            frozen = root/'publications/first/manifest.json'
            before = frozen.read_bytes()
            repeated = run_cli(*args)
            self.assertEqual(repeated.returncode, 1, repeated.stdout)
            self.assertEqual(frozen.read_bytes(), before)
            self.assertEqual(json.loads(before), manifest)

    def test_assessment_cli_requires_verified_explicit_context(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request, _ = fixture(root)
            write_json(root/'context.json', {'project':request['project'], 'evidence':request['evidence']})
            absent = run_cli('validate','--project',str(root),'human_acceptance.json')
            self.assertEqual(absent.returncode,1,absent.stdout)
            supplied = run_cli('validate','--project',str(root),'human_acceptance.json','--context','context.json')
            self.assertEqual(supplied.returncode,0,supplied.stdout+supplied.stderr)
            context = json.loads((root/'context.json').read_bytes())
            context['project']['sha256']='0'*64
            write_json(root/'context.json',context)
            self.assertEqual(run_cli('validate','--project',str(root),'human_acceptance.json','--context','context.json').returncode,1)

    def test_wrong_confirmation_or_member_drift_does_not_freeze(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request, _ = fixture(root)
            manifest = stage_publication(root, request)
            write_json(root/'stage.json', manifest)
            args = ('freeze-publication','--project',str(root),'--manifest','stage.json',
                    '--principal','alice','--confirm')
            self.assertEqual(run_cli(*args, 'FREEZE first').returncode, 1)
            (root/'result.txt').write_text('drift')
            self.assertEqual(run_cli(*args, confirmation_text(manifest)).returncode, 1)
            self.assertFalse((root/'publications/first').exists())
