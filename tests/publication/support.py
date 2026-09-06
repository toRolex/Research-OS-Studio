from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


STAMP = '2026-09-06T00:00:00Z'
AXES = ('structural_conformance', 'empirical_reproducibility',
        'mathematical_argument_review', 'formal_verification',
        'independent_review', 'human_acceptance')


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE).decode().strip()


def artifact(path, name, spec, **extra):
    return dict(contract={'name': 'research-os/artifact', 'version': '1.1.0'},
                target={'kind': 'git', 'path': path},
                type={'name': name, 'version': '1.0.0'}, spec=spec, **extra)


def fixture(root: Path, profile='empirical-computational', author='alice', source_materials=None):
    git(root, 'init', '-q')
    git(root, 'config', 'user.name', 'Publication Test')
    git(root, 'config', 'user.email', 'publication@example.test')
    members = []

    def add(path, value, role='artifact', dependencies=None):
        data = value if isinstance(value, bytes) else (json.dumps(value, indent=2) + '\n').encode()
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_bytes(data)
        git(root, 'add', '--', path)
        git(root, 'commit', '-qm', 'fixture ' + path)
        ref = {'target': {'kind': 'git', 'path': path, 'commit': git(root, 'rev-parse', 'HEAD')},
               'sha256': hashlib.sha256(data).hexdigest()}
        members.append({'path': path, 'ref': ref, 'role': role,
                        'purpose': 'Fixed ' + path, 'dependencies': dependencies or []})
        return ref

    project = add('project.json', artifact('project.json', 'project', {
        'name': 'Publication fixture', 'question': 'Does the fixed example hold?',
        'boundaries': ['Reference example only'],
        'principals': [{'identity': 'alice', 'roles': ['user', 'researcher']},
                       {'identity': 'bob', 'roles': ['reviewer']},
                       {'identity': 'validator', 'roles': ['agent']}]}))
    workstream = add('workstream.json', artifact('workstream.json', 'workstream', {
        'project': project, 'name': 'Example', 'intent': 'Test a bounded assertion', 'state': 'active'}))
    claim = add('claim.json', artifact('claim.json', 'claim', {
        'project': project, 'workstream': workstream, 'statement': 'The example holds.',
        'scope': 'whole_subject', 'conditions': ['Fixed inputs'], 'limitations': ['Not universal']}))
    material = add('result.txt', b'fixed result: 2\n', 'material')
    materials = [material]
    for path, data in (source_materials or {}).items():
        materials.append(add(path, data, 'material'))
    evidence = add('evidence.json', artifact('evidence.json', 'evidence', {
        'project': project, 'workstream': workstream, 'description': 'Recorded example'},
        relations=[{'relation': 'supports', 'claim': claim, 'scope': 'whole_subject',
                    'method': 'Fixed example check', 'conditions': ['Fixed inputs']}],
        provenance=[{'activity': 'example', 'inputs': materials}]))
    manuscript = add('manuscript.json', artifact('manuscript.json', 'manuscript', {
        'profile': profile, 'project': project, 'title': 'A bounded example',
        'authors': [author], 'body': 'The example holds for the fixed inputs only.',
        'contributions': ['One reproducible example'], 'claims': [claim], 'evidence': [evidence],
        'conditions': ['Fixed inputs'], 'limitations': ['Not universal'], 'materials': materials,
        'external_references': []}))
    from research_os.publication import manuscript_text, render_pdf
    paper = json.loads((root / 'manuscript.json').read_bytes())
    primary = add('paper.pdf', render_pdf(manuscript_text(paper)), 'primary-text', [manuscript])
    assessments = {axis: [] for axis in AXES}
    required = ['structural_conformance', 'independent_review', 'human_acceptance',
                'empirical_reproducibility' if profile == 'empirical-computational' else 'mathematical_argument_review']
    for axis in AXES:
        spec = {'project': project, 'subject': manuscript, 'dimension': axis,
                'scope': 'whole_subject', 'verdict': 'pass' if axis in required else 'not_applicable',
                'method': 'Explicit fixture assessment', 'evidence': [evidence],
                'assessor': 'alice' if axis == 'human_acceptance' else 'bob',
                'assessed_at': STAMP, 'validity': 'active'}
        if axis == 'independent_review':
            spec['isolation_receipt'] = {'reviewer': 'bob', 'authors': ['alice'],
                'inputs': [manuscript], 'fresh_context': True,
                'conversation_history_access': False, 'issued_at': STAMP}
        assessments[axis].append(add(axis + '.json', artifact(axis + '.json', 'assessment', spec)))
    request = {'publication': 'first', 'profile': profile, 'created_at': STAMP,
               'project': project, 'manuscript': manuscript, 'primary_text': primary,
               'members': members, 'contributions': paper['spec']['contributions'],
               'claims': [claim], 'evidence': [evidence], 'conditions': ['Fixed inputs'],
               'limitations': ['Not universal'], 'materials': materials,
               'assessments': assessments, 'external_references': [], 'required_gates': []}
    return request, add
