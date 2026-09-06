"""Direct CLI and both installed Adapter routes share exact registered checks."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from research_os.cli import load_validation_context
from research_os.contracts import build_registry, validate_artifact
from research_os.publication import stage_publication
from research_os.workflows.mathematical import create_statement_candidate, confirm_statement, run_math_proof
from research_os.workflows.mathematical.projections import project_record, create_typed_review
from research_os.validation.semantics.common import fixed_ref_key
from tests.publication.support import fixture
from tests.test_walking_skeleton import write_json
from tests.integration.package_support import installed_cli as run_cli


class UnifiedTypeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.request, self.add = fixture(self.root)
        installed = run_cli('setup-research-os', '--project', str(self.root))
        self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
        self.context_refs = []
        self.refresh_context()

    def refresh_context(self):
        write_json(self.root / 'context.json', {
            'project': self.request['project'], 'evidence': self.request['evidence'],
            'records': [m['ref'] for m in self.request['members']] + self.context_refs,
        })
        self.context = load_validation_context(self.root, 'context.json')

    def parity(self, path, code=0, context=True):
        args = ['--project', str(self.root), path]
        if context:
            args += ['--context', 'context.json']
        results = [run_cli('validate', *args),
                   *(run_cli('adapter', adapter, 'validate', *args) for adapter in ('claude-code', 'codex'))]
        reports = [json.loads(r.stdout) for r in results]
        for result, report in zip(results, reports):
            self.assertEqual(result.returncode, code, result.stdout + result.stderr)
            self.assertEqual(report, reports[0])
        return reports[0]

    def test_manuscript_and_publication_exact_registration_and_context(self):
        self.parity('manuscript.json', context=False)
        manifest = stage_publication(self.root, self.request)
        write_json(self.root / 'stage.json', manifest)
        self.parity('stage.json')
        missing = self.parity('stage.json', 1, context=False)
        self.assertIn('context.required', {i['code'] for i in missing['issues']})
        for kind, version in [('manuscript', '1.0.1'), ('invented', '1.0.0')]:
            value = json.loads((self.root / 'manuscript.json').read_bytes())
            value['type'] = {'name': kind, 'version': version}
            write_json(self.root / 'misleading-1.0.0.json', value)
            result = self.parity('misleading-1.0.0.json', 1, context=False)
            self.assertIn('type.unsupported', {i['code'] for i in result['issues']})
        self.assertEqual(len(build_registry().snapshot()['types']), len(build_registry()))

    def test_external_reference_requires_exact_receipt_bytes(self):
        from tests.publication.support import artifact, STAMP
        refs = [self.add(name, data, 'material') for name, data in (
            ('external.txt', b'external'), ('license.txt', b'permission'), ('log.txt', b'retrieval log'))]
        value = artifact('external.json', 'external-reference', {
            'target': refs[0]['target'], 'purpose': 'test receipt', 'required_scope': 'whole_subject',
            'receipt': {'retrieved_at': STAMP, 'resolved_locator': refs[0]['target'],
                        'sha256': refs[0]['sha256'], 'content': refs[0], 'license': refs[1], 'log': refs[2]}})
        write_json(self.root / 'external.json', value)
        self.refresh_context()
        self.parity('external.json')
        self.parity('external.json', 1, context=False)
        value['spec']['receipt']['license']['sha256'] = '0' * 64
        write_json(self.root / 'external.json', value)
        self.parity('external.json', 1)

    def math_chain(self):
        s = create_statement_candidate(revision=1, quantifiers=['every n'], hypotheses=[],
                                       domain='natural numbers', conclusion='n + 0 = n', rationale='definition')
        s = confirm_statement(s, principal='alice', confirmation=f"CONFIRM STATEMENT r1 {s['semantic_digest']}")
        p = run_math_proof(statement=s, actor_principal='alice', examples=[], counterexamples=[],
                           lemma_map=[{'id': 'L1', 'statement': 'identity', 'depends_on': [], 'status': 'proved'}],
                           attempts=[{'id': 'A1', 'approach': 'definition', 'argument': 'The base defining equation is n + 0 = n.',
                                      'outcome': 'candidate-proof', 'gaps': []}], max_attempts=1)
        workstream = next(m['ref'] for m in self.request['members'] if m['path'] == 'workstream.json')
        def projection(role, record, inputs):
            raw = (json.dumps(record, indent=3) + '\n').encode()
            ref = self.add(role + '-record.json', raw, 'material')
            value = project_record(raw, kind='math-' + role + '-projection',
                target={'kind': 'git', 'path': role + '-projection.json'}, record_ref=ref,
                project_ref=self.request['project'], workstream_ref=workstream, inputs=inputs)
            return self.add(role + '-projection.json', value), value
        sr, sv = projection('statement', s, {})
        pr, pv = projection('proof', p, {'statement': sr})
        self.refresh_context()
        r = create_typed_review(statement_ref=sr, proof_ref=pr,
            **{k: v for k, v in self.context.items() if k != 'evidence_by_digest'},
            reviewer_principal='bob', findings=[], verdict='pass')
        rr, rv = projection('review', r, {'statement': sr, 'proof': pr})
        self.refresh_context()
        return sv, pv, rv

    def test_math_typed_handoff_and_adversarial_bindings(self):
        statement, proof, review = self.math_chain()
        # Object-key reordering is not an input identity change.
        write_json(self.root / 'reordered.json', json.loads(json.dumps(review, sort_keys=True)))
        self.parity('reordered.json')
        for role in ('statement', 'proof', 'review'):
            self.parity(role + '-projection.json')
            self.parity(role + '-projection.json', 1, context=False)
        # Original formatting is committed separately from canonical semantic digest.
        raw_ref = statement['spec']['record']
        changed_context = copy.deepcopy(self.context)
        changed_context['records'][fixed_ref_key(raw_ref)] += b' '
        self.assertTrue(validate_artifact(statement, **changed_context))
        for label, mutate in (
            ('raw-sha', lambda v: v['spec']['record'].update(sha256='0' * 64)),
            ('semantic-sha', lambda v: v['spec'].update(subject_digest='0' * 64)),
            ('revision', lambda v: v['spec'].update(revision=True)),
            ('locator', lambda v: v['spec']['record']['target'].update(path='other.json')),
            ('workstream', lambda v: v['spec']['workstream'].update(sha256='0' * 64)),
            ('provenance', lambda v: v.update(provenance=[])),
            ('version', lambda v: v['type'].update(version='9.0.0')),
        ):
            with self.subTest(label=label):
                invalid = copy.deepcopy(review)
                mutate(invalid)
                write_json(self.root / 'invalid.json', invalid)
                self.parity('invalid.json', 1)
        self.assertFalse(json.loads(self.context['records'][fixed_ref_key(review['spec']['record'])])['human_acceptance'])

    def test_math_valid_but_cross_workstream_and_forged_review_fail(self):
        from tests.publication.support import artifact
        from research_os.workflows.mathematical.records import canonical_digest
        statement, proof, review = self.math_chain()
        other_ref = self.add('other-workstream.json', artifact('other-workstream.json', 'workstream', {
            'project': self.request['project'], 'name': 'Other', 'intent': 'Different handoff', 'state': 'active'}))
        self.refresh_context()
        invalid = copy.deepcopy(proof)
        invalid['spec']['workstream'] = other_ref
        invalid['provenance'][0]['inputs'][2] = other_ref
        write_json(self.root / 'invalid.json', invalid)
        self.parity('invalid.json', 1)
        # Even internally re-digested and pinned review records cannot grant acceptance.
        original = json.loads(self.context['records'][fixed_ref_key(review['spec']['record'])])
        for label in ('human_acceptance', 'reviewer_principal', 'receipt_path'):
            record = copy.deepcopy(original)
            if label == 'human_acceptance':
                record['human_acceptance'] = True
            elif label == 'reviewer_principal':
                record['reviewer_principal'] = 'alice'
            else:
                record['isolation_receipt']['inputs'][0]['path'] = 'substituted.json'
                record['isolation_receipt']['input_manifest_digest'] = canonical_digest(record['isolation_receipt']['inputs'])
            record['review_digest'] = canonical_digest({k: v for k, v in record.items() if k != 'review_digest'})
            raw = json.dumps(record).encode()
            ref = self.add('forged-' + label + '.json', raw, 'material')
            value = project_record(raw, kind='math-review-projection', target={'kind': 'git', 'path': 'invalid.json'},
                record_ref=ref, project_ref=review['spec']['project'], workstream_ref=review['spec']['workstream'],
                inputs=review['spec']['inputs'])
            write_json(self.root / 'invalid.json', value)
            self.refresh_context()
            self.parity('invalid.json', 1)

    def test_math_projection_schema_and_malformed_fixed_record(self):
        from research_os.validation.foundation.schema import LocalSchemaValidator
        from research_os.workflows.mathematical.projections import validate_projection
        import hashlib
        values = self.math_chain()
        contracts = Path(__file__).resolve().parents[2] / 'core/contracts'
        schema = LocalSchemaValidator(contracts)
        for value in values:
            self.assertEqual(schema.validate_file(contracts / 'mathematical/projection-1.0.0.schema.json', value), [])
        self.assertEqual(schema.validate_file(contracts / 'validation-context-1.0.0.schema.json',
                         json.loads((self.root / 'context.json').read_bytes())), [])
        for raw in (b'[]', b'null', b'"text"', b'{"contract":{"name":"research-os/mathematical-statement","version":"1.0.0"},"statement":[]}'):
            with self.subTest(raw=raw):
                value = copy.deepcopy(values[0])
                ref = value['spec']['record']
                ref['sha256'] = hashlib.sha256(raw).hexdigest()
                value['provenance'][0]['inputs'][0] = ref
                context = copy.deepcopy(self.context)
                context['records'][fixed_ref_key(ref)] = raw
                self.assertTrue(validate_projection(value, **{k: v for k, v in context.items() if k != 'evidence_by_digest'}))
                actual_ref = self.add('malformed-record.json', raw, 'material')
                value['spec']['record'] = actual_ref
                value['provenance'][0]['inputs'][0] = actual_ref
                write_json(self.root / 'invalid.json', value)
                self.refresh_context()
                self.parity('invalid.json', 1)

    def test_context_rejects_wrong_project_target_before_rebinding(self):
        project = json.loads((self.root / 'project.json').read_bytes())
        project['target']['path'] = 'not-the-selected-file.json'
        ref = self.add('wrong-project.json', project)
        write_json(self.root / 'context.json', {'project': ref, 'evidence': []})
        result = self.parity('human_acceptance.json', 1)
        self.assertIn('context.artifact', {i['code'] for i in result['issues']})
