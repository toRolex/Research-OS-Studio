"""Failure paths at shared application publication and reporting seams."""
import json
from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

from research_os.core import install_workflow_outputs, invoke_workflow
from research_os.contracts import artifact_report


class SharedBoundaryFailureTests(unittest.TestCase):
    def test_fsync_failure_after_link_rolls_back_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = os.fsync
            calls = 0
            def failing(fd):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError('injected directory fsync failure')
                return original(fd)
            with patch('research_os.core.os.fsync', side_effect=failing):
                with self.assertRaises(OSError):
                    install_workflow_outputs(root, {'artifact.json': b'bytes'})
            self.assertFalse((root/'artifact.json').exists())

    def test_math_overlapping_outputs_rejected_before_dict_construction(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileExistsError):
                invoke_workflow('math-proof', Path(directory), {
                    'statement_input': {'path':'missing.json','sha256':'a'*64},
                    'output':'same.json','report':'same.json',
                })
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_report_does_not_claim_type_execution_for_invalid_spec(self):
        value = {'contract':{'name':'research-os/artifact','version':'1.1.0'},
                 'target':{'kind':'git','path':'claim.json'},'type':{'name':'claim','version':'1.0.0'},'spec':None}
        result = artifact_report(value,'claim.json',json.dumps(value).encode())
        self.assertEqual([item['data']['name'] for item in result['evidence']], ['artifact-envelope'])
