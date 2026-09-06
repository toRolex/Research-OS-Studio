"""Typed handoffs over immutable ordinary-math records; no proof algorithm here.

The raw record digest, canonical record digest and domain subject digest are
separate commitments. Context is a map from complete fixed references to bytes,
not a filesystem search or a digest-only identity registry.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from research_os.validation.foundation import Issue
from research_os.validation.semantics.common import fixed_ref_key, validate_fixed_ref, validate_artifact_envelope
from research_os.validation.semantics.identity import principal_roles
from .records import canonical_digest, resolve_under
from .proof import (
    create_independent_review, validate_independent_review,
    validate_math_proof, validate_statement,
)

TYPES = {
    'math-statement-projection': ('research-os/mathematical-statement', 'semantic_digest', ()),
    'math-proof-projection': ('research-os/math-proof-run', 'run_digest', ('statement',)),
    'math-review-projection': ('research-os/independent-proof-review', 'review_digest', ('statement', 'proof')),
}


def _issues(items):
    return [Issue(i.code, i.message, getattr(i, 'location', getattr(i, 'path', ''))) for i in items]


def fixed_bytes(ref, records):
    problems = validate_fixed_ref(ref)
    if problems:
        raise ValueError('; '.join(i.code for i in problems))
    raw = (records or {}).get(fixed_ref_key(ref))
    if not isinstance(raw, bytes):
        raise ValueError('explicit fixed-reference bytes missing from validation context')
    if hashlib.sha256(raw).hexdigest() != ref['sha256']:
        raise ValueError('fixed-reference bytes digest mismatch')
    return raw


def fixed_artifact(ref, records, kind):
    value = json.loads(fixed_bytes(ref, records))
    if not isinstance(value, dict) or value.get('type') != {'name': kind, 'version': '1.0.0'}:
        raise ValueError('wrong typed dependency: ' + kind + '@1.0.0')
    expected = ref['target']
    local = {'kind': 'git', 'path': expected.get('path')}
    if value.get('target') != expected and not (
        expected.get('kind') == 'git' and 'repository' not in expected and value.get('target') == local
    ):
        raise ValueError('Artifact target differs from fixed-reference locator')
    return value


def _revision(record):
    if 'revision' in record:
        return record['revision']
    if isinstance(record.get('statement'), dict):
        return record['statement'].get('revision')
    if isinstance(record.get('subject'), dict):
        return record['subject'].get('statement_revision')
    return None


def project_record(raw, *, kind, target, record_ref, project_ref, workstream_ref, inputs=None):
    """Author a projection; validation still requires explicit pinned context."""
    if kind not in TYPES:
        raise ValueError('unsupported math projection type')
    contract, subject_field, roles = TYPES[kind]
    record = json.loads(raw)
    if not isinstance(record, dict) or record.get('contract') != {'name': contract, 'version': '1.0.0'}:
        raise ValueError('record contract/version mismatch')
    for ref in (record_ref, project_ref, workstream_ref, *(inputs or {}).values()):
        if validate_fixed_ref(ref):
            raise ValueError('projection requires complete fixed references')
    if hashlib.sha256(raw).hexdigest() != record_ref['sha256']:
        raise ValueError('record bytes digest mismatch')
    if set(inputs or {}) != set(roles):
        raise ValueError('projection input roles mismatch')
    return {
        'contract': {'name': 'research-os/artifact', 'version': '1.1.0'},
        'target': target, 'type': {'name': kind, 'version': '1.0.0'},
        'spec': {'project': project_ref, 'workstream': workstream_ref,
                 'record': record_ref, 'record_digest': canonical_digest(record),
                 'subject_digest': record[subject_field], 'revision': _revision(record), 'inputs': inputs or {}},
        'provenance': [{'activity': 'ordinary-math-record-projection',
                        'inputs': [record_ref, project_ref, workstream_ref, *((inputs or {})[role] for role in roles)]}],
    }


def _review_tree(root, projections, records):
    """Rehydrate exact, already pinned record bytes, never mutable source files."""
    paths, digests = [], []
    aliases = set()
    for value in projections:
        ref = value['spec']['record']
        target = ref['target']
        if target['kind'] != 'git' or 'repository' in target:
            raise ValueError('ordinary review records require local fixed Git targets')
        path = target['path']
        parts = path.casefold().split('/')
        alias = '/'.join(parts)
        if any(alias == other or alias.startswith(other + '/') or other.startswith(alias + '/') for other in aliases):
            raise ValueError('review input paths alias or overlap')
        aliases.add(alias)
        destination = resolve_under(root, path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(fixed_bytes(ref, records))
        paths.append(path)
        digests.append(ref['sha256'])
    return paths, digests


def validate_projection(value, *, project=None, project_digest=None, records=None):
    """Validate provenance, identity, typed chain and the unchanged leaf validators."""
    from research_os.contracts import validate_artifact
    try:
        kind = value['type']['name']
        contract, subject_field, roles = TYPES[kind]
        envelope_issues = _issues(validate_artifact_envelope(value, kind))
        if envelope_issues:
            return envelope_issues
        spec = value['spec']
        if set(spec) != {'project', 'workstream', 'record', 'record_digest', 'subject_digest', 'revision', 'inputs'}:
            raise ValueError('math projection fields must match contract')
        if not isinstance(spec['inputs'], dict) or set(spec['inputs']) != set(roles):
            raise ValueError('math projection input roles mismatch')
        if project is None or project_digest is None or records is None:
            return [Issue('context.required', 'math projection requires fixed Project and record bytes', '/spec')]
        project_ref = spec['project']
        pinned_project = fixed_artifact(project_ref, records, 'project')
        if (project_ref['sha256'] != project_digest or project.get('target') != project_ref['target']
                or canonical_digest({**pinned_project, 'target': project_ref['target']}) != canonical_digest(project)):
            raise ValueError('math projection Project context mismatch')
        problems = validate_artifact(pinned_project)
        workstream = fixed_artifact(spec['workstream'], records, 'workstream')
        problems += validate_artifact(workstream)
        if workstream['spec']['project'] != project_ref:
            raise ValueError('math projection cross-Project Workstream')
        record = json.loads(fixed_bytes(spec['record'], records))
        if not isinstance(record, dict) or record.get('contract') != {'name': contract, 'version': '1.0.0'}:
            raise ValueError('record contract/version mismatch')
        if (canonical_digest(record) != spec['record_digest'] or record.get(subject_field) != spec['subject_digest']
                or type(spec['revision']) is not int or spec['revision'] != _revision(record)):
            raise ValueError('record or subject semantic digest mismatch')
        expected_provenance = [{'activity': 'ordinary-math-record-projection',
                                'inputs': [spec['record'], project_ref, spec['workstream'], *(spec['inputs'][role] for role in roles)]}]
        if value.get('provenance') != expected_provenance:
            raise ValueError('math projection provenance must bind all fixed inputs')
        projections, inputs = {}, {}
        for role in roles:
            expected = 'math-' + role + '-projection'
            dependency = fixed_artifact(spec['inputs'][role], records, expected)
            problems += validate_artifact(dependency, project=project, project_digest=project_digest, records=records)
            if dependency['spec']['project'] != project_ref or dependency['spec']['workstream'] != spec['workstream']:
                raise ValueError('math typed input Project/Workstream mismatch')
            projections[role] = dependency
            inputs[role] = json.loads(fixed_bytes(dependency['spec']['record'], records))
        if problems:
            return problems
        if kind == 'math-statement-projection':
            problems += _issues(validate_statement(record))
            if record.get('confirmation') is not None and 'user' not in principal_roles(project, record['confirmation']['principal']):
                raise ValueError('confirmed statement requires Project user principal')
        elif kind == 'math-proof-projection':
            problems += _issues(validate_math_proof(record, statement=inputs['statement']))
            if not principal_roles(project, record['actor_principal']):
                raise ValueError('proof actor is not bound to Project')
        else:
            if projections['proof']['spec']['inputs']['statement'] != spec['inputs']['statement']:
                raise ValueError('review and proof must bind the same typed statement')
            if 'reviewer' not in principal_roles(project, record['reviewer_principal']):
                raise ValueError('reviewer requires Project reviewer role')
            with tempfile.TemporaryDirectory(prefix='research-os-review-') as directory:
                root = Path(directory)
                _review_tree(root, [projections['statement'], projections['proof']], records)
                problems += [Issue(i.code, i.message.replace(str(root), '<fixed-review-context>'), i.location)
                             for i in validate_independent_review(record, project_root=root, **inputs)]
        return problems
    except (ValueError, TypeError, KeyError, AttributeError, OSError) as exc:
        return [Issue('math.projection', str(exc), '/spec')]


def create_typed_review(*, statement_ref, proof_ref, records, project, project_digest, **review):
    """Consume typed handoffs; return the ordinary record for user-controlled pinning.

    This checks mechanical isolation only, never human acceptance or actual host
    isolation. The caller subsequently fixes these bytes and projects the review.
    """
    from research_os.contracts import validate_artifact
    statement = fixed_artifact(statement_ref, records, 'math-statement-projection')
    proof = fixed_artifact(proof_ref, records, 'math-proof-projection')
    for value in (statement, proof):
        problems = validate_artifact(value, project=project, project_digest=project_digest, records=records)
        if problems:
            raise ValueError('; '.join(i.code + ': ' + i.message for i in problems))
    if (proof['spec']['inputs']['statement'] != statement_ref
            or statement['spec']['project'] != proof['spec']['project']
            or statement['spec']['workstream'] != proof['spec']['workstream']):
        raise ValueError('typed review inputs do not form one fixed math handoff')
    if 'reviewer' not in principal_roles(project, review.get('reviewer_principal')):
        raise ValueError('reviewer requires Project reviewer role')
    with tempfile.TemporaryDirectory(prefix='research-os-review-') as directory:
        root = Path(directory)
        paths, digests = _review_tree(root, [statement, proof], records)
        return create_independent_review(
            project_root=root, statement=json.loads(fixed_bytes(statement['spec']['record'], records)),
            proof=json.loads(fixed_bytes(proof['spec']['record'], records)),
            input_paths=paths, input_digests=digests, **review,
        )
