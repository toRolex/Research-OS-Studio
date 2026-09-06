"""CLI repository admission and dynamic validator integration."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from research_os.core import rebuild_catalog, validate_repository, validate_ports
from research_os.contracts import artifact_report, validate_artifact
from research_os.validation.foundation import validate_validation_report

ROOT = Path(__file__).resolve().parents[2]


class RepositoryIntegrationTests(unittest.TestCase):
    def test_catalog_rebuild_is_complete_and_byte_deterministic(self):
        first = rebuild_catalog(ROOT)
        self.assertEqual(first, rebuild_catalog(ROOT))
        workflows = [item['id'] for item in first['skills'] if item['kind'] == 'workflow']
        disciplines = [item['id'] for item in first['skills'] if item['kind'] == 'discipline']
        self.assertEqual(len(workflows), 15)
        self.assertEqual(
            disciplines,
            [
                'citation-reference-audit',
                'environment-check',
                'experiment-audit',
                'independent-proof-review',
                'publication-claim-audit',
                'statistical-check',
                'training-health-check',
                'trusted-statement-comparison',
            ],
        )
        self.assertEqual(first, json.loads((ROOT/'core/catalog.json').read_bytes()))

    def test_missing_disciplines_ports_and_skill_notes_are_blockers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT/'core', root/'core')
            for skill in (root/'core/skills').iterdir():
                if skill.name not in {item['id'] for item in rebuild_catalog(ROOT)['skills'] if item['kind']=='workflow'}:
                    shutil.rmtree(skill)
            note = root/'core/skills/research-charter/references/integration-implementation-notes.md'
            note.parent.mkdir(exist_ok=True)
            note.write_text('Not canonical skill content')
            (root/'core/catalog.json').write_text(json.dumps(rebuild_catalog(root)))
            result = validate_repository(root)
            self.assertEqual(result['exit_code'], 1)
            codes = {item['code'] for item in result['issues']}
            self.assertTrue({'catalog.discipline.missing','ports.not_accepted','core.implementation_notes'} <= codes)
            self.assertEqual(validate_validation_report(result['report']), [])

    def test_repository_binds_every_discipline_to_exact_port_product_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / 'core', root / 'core')
            shutil.copytree(ROOT / 'ports/products', root / 'ports/products')
            product = root / 'ports/products/statistical-check/SKILL.md'
            product.write_bytes(product.read_bytes() + b'\nport drift\n')
            with patch(
                'research_os.core.validate_ports',
                return_value={'status': 'pass', 'verdict': 'pass', 'exit_code': 0, 'issues': []},
            ):
                result = validate_repository(root)
            self.assertEqual(result['exit_code'], 1)
            self.assertIn('ports.catalog_binding', {item['code'] for item in result['issues']})

    def test_ports_module_missing_is_fail_not_blocked(self):
        with patch('research_os.core.importlib.import_module', side_effect=ModuleNotFoundError('ports missing')):
            result = validate_ports(ROOT)
        self.assertEqual(result['exit_code'], 1)
        self.assertEqual(result['status'], 'fail')

    def test_registry_rejects_unknown_type_and_records_real_validator(self):
        artifact = {'contract': {'name':'research-os/artifact','version':'1.1.0'},
                    'target': {'kind':'git','path':'claim.json'},
                    'type': {'name':'claim','version':'1.0.0'}, 'spec': {}}
        raw = json.dumps(artifact).encode()
        report = artifact_report(artifact, 'claim.json', raw)
        self.assertEqual(report['verdict'],'fail')
        self.assertNotIn('type.validator_contract', {item['code'] for item in report['issues']})
        self.assertEqual(report['subject']['sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(report['evidence'][1]['data']['name'], 'claim')
        self.assertEqual(validate_validation_report(report), [])
        artifact['type']['name'] = 'not-implemented'
        self.assertIn('type.unsupported', {item.code for item in validate_artifact(artifact)})

    def test_assessment_does_not_pass_without_project_identity_context(self):
        artifact = {'contract': {'name':'research-os/artifact','version':'1.1.0'},
                    'target': {'kind':'git','path':'assessment.json'},
                    'type': {'name':'assessment','version':'1.0.0'}, 'spec': {}}
        self.assertIn('assessment.project_context_required', {item.code for item in validate_artifact(artifact)})


if __name__ == '__main__':
    unittest.main()
