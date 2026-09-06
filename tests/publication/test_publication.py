from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from research_os.publication import (
    PublicationError, stage_publication, preflight, freeze_publication,
    verify_publication, confirmation_text, append_event, stale_audit,
)
from support import fixture, STAMP


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_both_profiles_freeze_exact_bytes_and_second_publication(self):
        for profile in ('empirical-computational', 'mathematical-theoretical'):
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                request, _ = fixture(root, profile)
                manifest = stage_publication(root, request)
                report = preflight(root, manifest)
                self.assertEqual(report['exit_code'], 0, report)
                self.assertEqual(report, preflight(root, manifest))
                receipt = freeze_publication(root, manifest, confirmation_text(manifest), 'alice')
                self.assertEqual(receipt['manifest_sha256'], hashlib.sha256(
                    (root / 'publications/first/manifest.json').read_bytes()).hexdigest())
                self.assertEqual(verify_publication(root, 'first')['exit_code'], 0)
                for member in manifest['spec']['members']:
                    frozen = root / 'publications/first/files' / member['path']
                    self.assertEqual(frozen.read_bytes(), (root / member['path']).read_bytes())
                    self.assertEqual(hashlib.sha256(frozen.read_bytes()).hexdigest(), member['ref']['sha256'])
                before = (root / 'publications/first/manifest.json').read_bytes()
                with self.assertRaises(PublicationError):
                    freeze_publication(root, manifest, confirmation_text(manifest), 'alice')
                request['publication'] = 'second'
                second = stage_publication(root, request)
                freeze_publication(root, second, confirmation_text(second), 'alice')
                self.assertEqual(before, (root / 'publications/first/manifest.json').read_bytes())

    def test_confirmation_drift_and_identity_fail_closed(self):
        request, _ = fixture(self.root)
        manifest = stage_publication(self.root, request)
        for confirmation, principal in [('FREEZE first', 'alice'),
                                        (confirmation_text(manifest), 'bob')]:
            with self.assertRaises(PublicationError):
                freeze_publication(self.root, manifest, confirmation, principal)
        changed = copy.deepcopy(manifest)
        changed['spec']['limitations'].append('Changed after confirmation')
        with self.assertRaises(PublicationError):
            freeze_publication(self.root, changed, confirmation_text(manifest), 'alice')
        (self.root / 'result.txt').write_bytes(b'drift')
        self.assertEqual(preflight(self.root, manifest)['exit_code'], 1)
        with self.assertRaises(PublicationError):
            freeze_publication(self.root, manifest, confirmation_text(manifest), 'alice')
        self.assertFalse((self.root / 'publications/first').exists())

    def test_missing_evidence_and_multiple_primary_texts_block(self):
        request, _ = fixture(self.root)
        for mutate in (
            lambda r: r.update(evidence=[]),
            lambda r: r['members'].pop(3),
            lambda r: r['members'][0].update(role='primary-text'),
            lambda r: r['assessments'].update(human_acceptance=[]),
            lambda r: r.update(required_gates=[{'dimension': 'formal_verification',
                'subject': r['manuscript'], 'scope': 'whole_subject'}]),
        ):
            bad = copy.deepcopy(request)
            mutate(bad)
            with self.assertRaises(PublicationError):
                stage_publication(self.root, bad)

    def test_external_receipts_freeze_offline_and_missing_receipt_blocks(self):
        from support import artifact
        request, add = fixture(self.root)
        content = add('external/source.txt', b'Fixed external source.\n', 'material')
        license_ref = add('external/license.txt', b'SPDX-License-Identifier: CC0-1.0\n', 'material')
        log = add('external/retrieval.log', b'HTTP 200; fixed source retrieved.\n', 'material')
        target = {'kind': 'uri', 'uri': 'https://example.org/source.txt', 'sha256': content['sha256']}
        external = add('external/reference.json', artifact('external/reference.json', 'external-reference', {
            'target': target, 'purpose': 'Fixed cited example', 'required_scope': 'whole_subject',
            'receipt': {'retrieved_at': STAMP, 'resolved_locator': target, 'sha256': content['sha256'],
                        'content': content, 'license': license_ref, 'log': log}}))
        manuscript = json.loads((self.root / 'manuscript.json').read_bytes())
        manuscript['spec']['external_references'] = [external]
        manuscript['spec']['materials'] += [content, license_ref, log]
        # New fixed Manuscript revision needs all new Assessments, never inherited.
        request['members'][:] = [m for m in request['members'] if m['path'] not in {'manuscript.json', 'paper.pdf'}
                                 and not m['path'].endswith('_review.json')
                                 and m['path'] not in {'structural_conformance.json', 'empirical_reproducibility.json',
                                    'formal_verification.json', 'human_acceptance.json'}]
        manuscript_ref = add('manuscript.json', manuscript)
        from research_os.publication import render_pdf, manuscript_text
        primary = add('paper.pdf', render_pdf(manuscript_text(manuscript)), 'primary-text', [manuscript_ref])
        for axis in request['assessments']:
            value = json.loads((self.root / (axis + '.json')).read_bytes())
            value['spec']['subject'] = manuscript_ref
            if axis == 'independent_review':
                value['spec']['isolation_receipt']['inputs'] = [manuscript_ref]
            request['assessments'][axis] = [add(axis + '.json', value)]
        request.update(manuscript=manuscript_ref, primary_text=primary,
                       external_references=[external], materials=manuscript['spec']['materials'])
        manifest = stage_publication(self.root, request)
        freeze_publication(self.root, manifest, confirmation_text(manifest), 'alice')
        self.assertEqual(verify_publication(self.root, 'first')['exit_code'], 0)
        (self.root / 'external/license.txt').unlink()
        self.assertEqual(preflight(self.root, manifest)['exit_code'], 1)
        self.assertEqual(verify_publication(self.root, 'first')['exit_code'], 0)

    def test_events_are_outside_package_and_stale_audit_is_append_only(self):
        request, _ = fixture(self.root)
        manifest = stage_publication(self.root, request)
        freeze_publication(self.root, manifest, confirmation_text(manifest), 'alice')
        baseline = {p.relative_to(self.root / 'publications/first').as_posix(): p.read_bytes()
                    for p in (self.root / 'publications/first').rglob('*') if p.is_file()}
        for kind in ('notice', 'retract'):
            event = {'kind': kind, 'reason': 'Explicit user decision', 'issued_at': STAMP}
            result = append_event(self.root, 'first', event, 'alice', f'{kind.upper()} first')
            self.assertTrue((self.root / result['path']).is_file())
            self.assertNotIn('/publications/', str(result['path']))
            with self.assertRaises(PublicationError):
                append_event(self.root, 'first', event, 'alice', f'{kind.upper()} first')
        (self.root / 'result.txt').write_bytes(b'new upstream result')
        audit = stale_audit(self.root, 'first', issued_at=STAMP)
        self.assertEqual(audit['spec']['changes'][0]['path'], 'result.txt')
        self.assertEqual(verify_publication(self.root, 'first')['exit_code'], 0)
        after = {p.relative_to(self.root / 'publications/first').as_posix(): p.read_bytes()
                 for p in (self.root / 'publications/first').rglob('*') if p.is_file()}
        self.assertEqual(baseline, after)


if __name__ == '__main__':
    unittest.main()
