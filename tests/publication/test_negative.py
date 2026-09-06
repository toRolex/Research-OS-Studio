from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from research_os.publication import (
    PublicationError, append_event, confirmation_text, freeze_publication,
    preflight, stage_publication, stale_audit, verify_publication,
)
from support import artifact, fixture, STAMP


class NegativePublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.request, self.add = fixture(self.root)

    def reject(self, request):
        with self.assertRaises(PublicationError):
            stage_publication(self.root, request)

    def test_actual_manuscript_author_cannot_self_review_with_false_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request, _ = fixture(root, author='bob')
            with self.assertRaises(PublicationError):
                stage_publication(root, request)

    def test_conflict_cannot_be_hidden_by_favorable_gate(self):
        axis = 'empirical_reproducibility'
        value = json.loads((self.root / (axis + '.json')).read_bytes())
        value['target']['path'] = 'conflict.json'
        value['spec']['verdict'] = 'inconclusive'
        value['spec']['scope'] = ['/body']
        ref = self.add('conflict.json', value)
        self.request['assessments'][axis].append(ref)
        self.reject(self.request)
        self.request['assessments'][axis].pop()
        self.reject(self.request)  # unlisted Assessment cannot hide conflict

    def test_required_gate_rejects_wrong_scope_old_revision_and_nonpass(self):
        axis = 'empirical_reproducibility'
        original = json.loads((self.root / (axis + '.json')).read_bytes())
        for change in ({'verdict': 'inconclusive'}, {'verdict': 'fail'},
                       {'verdict': 'not_applicable'}, {'scope': ['/body']},
                       {'validity': 'expired', 'validity_reason': 'Expired'},
                       {'subject': self.request['claims'][0]}):
            with self.subTest(change=change):
                value = copy.deepcopy(original)
                value['target']['path'] = 'new-assessment.json'
                value['spec'].update(change)
                ref = self.add('new-assessment.json', value)
                candidate = copy.deepcopy(self.request)
                candidate['members'] = [m for m in candidate['members'] if m['path'] not in {axis + '.json', 'new-assessment.json'}]
                candidate['members'].append(copy.deepcopy(self.request['members'][-1]))
                candidate['assessments'][axis] = [ref]
                self.reject(candidate)
                self.request['members'].pop()

    def test_path_aliases_symlinks_missing_and_fake_commit_block(self):
        for path in ('../escape', '/absolute', 'a/../b', '.git/config', 'a\\b', 'a//b', 'a/./b', 'bad\x00name'):
            candidate = copy.deepcopy(self.request)
            candidate['members'][0]['path'] = path
            self.reject(candidate)
        candidate = copy.deepcopy(self.request)
        candidate['members'][0]['ref']['target']['commit'] = 'a' * 40
        self.reject(candidate)
        (self.root / 'result.txt').unlink()
        self.reject(self.request)
        (self.root / 'outside.txt').write_text('fixed result: 2\n')
        (self.root / 'result.txt').symlink_to(self.root / 'outside.txt')
        self.reject(self.request)
        (self.root / 'result.txt').unlink()
        (self.root / 'result.txt').mkdir()
        self.reject(self.request)

    def test_stage_exclusive_no_destination_symlinks_or_empty_directory_overwrite(self):
        manifest = stage_publication(self.root, self.request, stage_path='staging/first.json')
        with self.assertRaises(PublicationError):
            stage_publication(self.root, self.request, stage_path='staging/first.json')
        outside = self.root / 'outside'
        outside.mkdir()
        (self.root / 'publications').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(PublicationError):
            freeze_publication(self.root, manifest, confirmation_text(manifest), 'alice')
        self.assertEqual(list(outside.iterdir()), [])
        (self.root / 'publications').unlink()
        (self.root / 'publications/first').mkdir(parents=True)
        with self.assertRaises(PublicationError):
            freeze_publication(self.root, manifest, confirmation_text(manifest), 'alice')
        self.assertEqual(list((self.root / 'publications/first').iterdir()), [])
        self.assertEqual([p.name for p in (self.root / 'publications').iterdir()], ['first'])

    def test_frozen_verification_detects_drift_extra_members_and_receipt_tampering(self):
        manifest = stage_publication(self.root, self.request)
        freeze_publication(self.root, manifest, confirmation_text(manifest), 'alice')
        extra = self.root / 'publications/first/extra.txt'
        extra.write_text('not a member')
        self.assertEqual(verify_publication(self.root, 'first')['exit_code'], 1)
        extra.unlink()
        receipt_path = self.root / 'publications/first/freeze-receipt.json'
        receipt = json.loads(receipt_path.read_bytes())
        receipt['principal'] = 'bob'
        receipt_path.write_text(json.dumps(receipt))
        self.assertEqual(verify_publication(self.root, 'first')['exit_code'], 1)

    def test_supersede_requires_real_second_publication(self):
        manifest = stage_publication(self.root, self.request)
        freeze_publication(self.root, manifest, confirmation_text(manifest), 'alice')
        event = {'kind': 'supersede', 'reason': 'New bounded publication', 'issued_at': STAMP, 'replacement': 'second'}
        with self.assertRaises(PublicationError):
            append_event(self.root, 'first', event, 'alice', 'SUPERSEDE first')
        self.request['publication'] = 'second'
        second = stage_publication(self.root, self.request)
        freeze_publication(self.root, second, confirmation_text(second), 'alice')
        result = append_event(self.root, 'first', event, 'alice', 'SUPERSEDE first')
        self.assertEqual(result['artifact']['spec']['replacement']['target'], second['target'])
        self.assertEqual(verify_publication(self.root, 'first')['exit_code'], 0)
        (self.root / 'result.txt').unlink()
        audit = stale_audit(self.root, 'first', issued_at=STAMP)
        self.assertEqual(audit['spec']['changes'][0]['observation'], 'unavailable')

    def test_event_io_failure_does_not_poison_append_only_destination(self):
        from unittest.mock import patch
        manifest = stage_publication(self.root, self.request)
        freeze_publication(self.root, manifest, confirmation_text(manifest), 'alice')
        event = {'kind': 'notice', 'reason': 'Fixed notice', 'issued_at': STAMP}
        with patch('os.fsync', side_effect=OSError('injected full disk')):
            with self.assertRaises(PublicationError):
                append_event(self.root, 'first', event, 'alice', 'NOTICE first')
        result = append_event(self.root, 'first', event, 'alice', 'NOTICE first')
        self.assertTrue((self.root / result['path']).is_file())

    def test_freeze_failure_cleanup_stays_under_anchored_parent(self):
        from unittest.mock import patch
        manifest = stage_publication(self.root, self.request)
        real_fsync = __import__('os').fsync
        outside = self.root / 'outside'
        outside.mkdir()
        moved = self.root / 'original-publications'
        fired = False
        def fail_and_swap(fd):
            nonlocal fired
            if not fired:
                fired = True
                stage_name = next((self.root / 'publications').iterdir()).name
                (outside / stage_name).mkdir()
                (outside / stage_name / 'keep.txt').write_text('must survive')
                (self.root / 'publications').rename(moved)
                (self.root / 'publications').symlink_to(outside, target_is_directory=True)
                raise OSError('injected directory replacement')
            return real_fsync(fd)
        with patch('os.fsync', side_effect=fail_and_swap):
            with self.assertRaises(PublicationError):
                freeze_publication(self.root, manifest, confirmation_text(manifest), 'alice')
        self.assertEqual(len(list(outside.glob('*/keep.txt'))), 1)
        self.assertEqual(list(moved.iterdir()), [])

    def test_independent_review_of_opaque_material_does_not_parse_json(self):
        value = json.loads((self.root / 'independent_review.json').read_bytes())
        value['target']['path'] = 'material-review.json'
        for subject in (self.request['materials'][0], self.request['primary_text']):
            value['spec']['subject'] = subject
            value['spec']['isolation_receipt']['inputs'] = [subject]
            ref = self.add('material-review.json', value)
            self.request['assessments']['independent_review'].append(ref)
            manifest = stage_publication(self.root, self.request)
            self.assertEqual(preflight(self.root, manifest)['exit_code'], 0)
            self.request['members'].pop()
            self.request['assessments']['independent_review'].pop()

    def test_event_parent_fsync_failure_after_link_rolls_back_destination(self):
        from unittest.mock import patch
        import os
        import stat
        manifest = stage_publication(self.root, self.request)
        freeze_publication(self.root, manifest, confirmation_text(manifest), 'alice')
        event = {'kind': 'notice', 'reason': 'Parent sync failure', 'issued_at': STAMP}
        real_fsync = os.fsync
        final_was_visible = []
        def fail_parent(fd):
            if stat.S_ISDIR(os.fstat(fd).st_mode):
                final_was_visible.extend((self.root / 'publication-events/first').glob('*.json'))
                raise OSError('injected parent fsync failure after link')
            return real_fsync(fd)
        with patch('os.fsync', side_effect=fail_parent):
            with self.assertRaises(PublicationError):
                append_event(self.root, 'first', event, 'alice', 'NOTICE first')
        self.assertEqual(len(final_was_visible), 1)
        self.assertEqual(list((self.root / 'publication-events/first').iterdir()), [])
        result = append_event(self.root, 'first', event, 'alice', 'NOTICE first')
        self.assertTrue((self.root / result['path']).is_file())

    def test_malformed_values_report_failure_not_uncaught_errors(self):
        manifest = stage_publication(self.root, self.request)
        for field, value in [('profile', []), ('members', [None]), ('claims', [None]),
                             ('assessments', {'a': 1}), ('required_gates', [None])]:
            candidate = copy.deepcopy(manifest)
            candidate['spec'][field] = value
            self.assertEqual(preflight(self.root, candidate)['exit_code'], 1)
        self.assertEqual(preflight(self.root, None)['exit_code'], 1)

    def test_material_json_cannot_masquerade_as_normative_evidence(self):
        for member in self.request['members']:
            if member['path'] == 'evidence.json':
                member['role'] = 'material'
        self.reject(self.request)

    def test_external_fixed_git_target_without_commit_is_rejected(self):
        # The URI profile pins content; Git always requires the real full revision.
        from research_os.publication.contracts import validate_external
        value = artifact('external.json', 'external-reference', {
            'target': {'kind': 'git', 'path': 'source.txt'}, 'purpose': 'Source',
            'required_scope': 'whole_subject', 'receipt': {
                'retrieved_at': STAMP, 'resolved_locator': {'kind': 'git', 'path': 'source.txt'},
                'sha256': self.request['materials'][0]['sha256'],
                'content': self.request['materials'][0], 'license': self.request['materials'][0],
                'log': self.request['materials'][0]}})
        records = {tuple(['git', None, self.request['materials'][0]['target']['commit'], 'result.txt', self.request['materials'][0]['sha256']]):
                   ({}, (self.root / 'result.txt').read_bytes())}
        with self.assertRaises(PublicationError):
            validate_external(value, records)


if __name__ == '__main__':
    unittest.main()
