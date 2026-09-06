from pathlib import Path
import json
import unittest

from research_os.validation.foundation.schema import LocalSchemaValidator
from research_os.publication import stage_publication
from support import fixture
import tempfile

ROOT = Path(__file__).resolve().parents[2]


class SchemaTests(unittest.TestCase):
    def test_manuscript_publication_and_external_schemas_are_offline(self):
        validator = LocalSchemaValidator(ROOT / 'core/contracts')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request, _ = fixture(root)
            manifest = stage_publication(root, request)
            for name, value in [('manuscript', json.loads((root / 'manuscript.json').read_bytes())),
                                ('publication', manifest)]:
                schema = ROOT / f'core/contracts/publication/{name}-1.0.0.schema.json'
                self.assertEqual(validator.validate_file(schema, value), [])
                value['spec']['unknown'] = True
                self.assertTrue(validator.validate_file(schema, value))

    def test_templates_declare_both_profiles_without_claiming_acceptance(self):
        profiles = set()
        for path in (ROOT / 'templates/publication').glob('*.json'):
            value = json.loads(path.read_bytes())
            profiles.add(value['profile'])
            self.assertFalse(value['assessments']['human_acceptance'])
            self.assertEqual(value['members'], [])
        self.assertEqual(profiles, {'empirical-computational', 'mathematical-theoretical'})
