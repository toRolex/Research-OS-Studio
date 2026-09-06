"""Typed publication contracts and graph checks, independent of the CLI facade."""
from __future__ import annotations

from research_os.validation.semantics.assurance import (
    ASSURANCE_DIMENSIONS, find_assurance_conflicts, validate_assessment,
)
from research_os.validation.semantics.claim import validate_claim
from research_os.validation.semantics.common import (
    fixed_ref_key, validate_artifact_envelope, validate_fixed_ref,
    validate_fixed_ref_array, validate_string_array, validate_timestamp,
)
from research_os.validation.foundation.targets import validate_target
from research_os.validation.semantics.evidence import validate_evidence
from research_os.validation.semantics.identity import principal_roles
from research_os.validation.semantics.project import validate_project
from research_os.validation.semantics.scope import validate_scope
from research_os.validation.semantics.workstream import validate_workstream

from .renderer import render_pdf
from .storage import PublicationError, canonical_bytes, digest, parse_json, safe_parts

PROFILES = {'empirical-computational', 'mathematical-theoretical'}
MANUSCRIPT_FIELDS = {'profile', 'project', 'title', 'authors', 'body', 'contributions',
                     'claims', 'evidence', 'conditions', 'limitations', 'materials',
                     'external_references'}
MANIFEST_FIELDS = {'publication', 'profile', 'profile_version', 'created_at', 'project',
                   'manuscript', 'primary_text', 'members', 'contributions', 'claims',
                   'evidence', 'conditions', 'limitations', 'materials', 'assessments',
                   'external_references', 'required_gates'}
ROLES = {'artifact', 'primary-text', 'material'}


def require(condition, message):
    if not condition:
        raise PublicationError(message)


def checked(issues):
    if issues:
        raise PublicationError('; '.join(f'{item.code}: {item.message}' for item in issues))


def fields(value, expected, label):
    require(isinstance(value, dict) and set(value) == expected, label + ': fields must match contract')


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), label + ': nonempty text required')


def refs(value, label, *, nonempty=False):
    checked(validate_fixed_ref_array(value, label, nonempty=nonempty))


def strings(value, label, *, nonempty=False):
    checked(validate_string_array(value, label, nonempty=nonempty, unique=True))


def artifact(path, name, spec):
    return {'contract': {'name': 'research-os/artifact', 'version': '1.1.0'},
            'target': {'kind': 'git', 'path': path},
            'type': {'name': name, 'version': '1.0.0'}, 'spec': spec}


def validate_manuscript(value):
    checked(validate_artifact_envelope(value, 'manuscript'))
    spec = value['spec']
    fields(spec, MANUSCRIPT_FIELDS, 'Manuscript')
    require(spec['profile'] in PROFILES, 'unsupported Publication profile')
    checked(validate_fixed_ref(spec['project']))
    for field in ('title', 'body'):
        text(spec[field], field)
    for field in ('authors', 'contributions', 'conditions', 'limitations'):
        strings(spec[field], field, nonempty=field in {'authors', 'contributions'})
    for field in ('claims', 'evidence', 'materials', 'external_references'):
        refs(spec[field], field, nonempty=field in {'claims', 'evidence', 'materials'})


def validate_typed_publication(value, *, records=None):
    """Registry adapter: graph-dependent types require explicitly supplied bytes."""
    from research_os.validation.foundation import Issue
    from research_os.workflows.mathematical.projections import fixed_bytes
    try:
        kind = value['type']['name']
        if kind == 'manuscript':
            validate_manuscript(value)
        elif records is None:
            return [Issue('context.required', kind + ' requires fixed member/receipt bytes', '/spec')]
        elif kind == 'publication':
            members = value['spec']['members']
            payloads = {member['path']: fixed_bytes(member['ref'], records) for member in members}
            validate_graph(value, payloads)
        elif kind == 'external-reference':
            dependencies = value['spec']['receipt']
            selected = {fixed_ref_key(dependencies[field]): ({}, fixed_bytes(dependencies[field], records))
                        for field in ('content', 'license', 'log')}
            validate_external(value, selected)
        else:
            return [Issue('type.unsupported', 'unsupported publication type', '/type')]
        return []
    except (PublicationError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return [Issue('publication.contract', str(exc), '/spec')]


def manuscript_text(value) -> str:
    """Stable plain-text projection includes declared scientific boundaries."""
    validate_manuscript(value)
    spec = value['spec']
    sections = [spec['title'], ', '.join(spec['authors']), spec['body']]
    for field in ('contributions', 'conditions', 'limitations'):
        sections.extend([field.title(), '\n'.join(spec[field]) or '(explicitly none)'])
    for field in ('claims', 'evidence', 'materials', 'external_references'):
        sections.extend([field.replace('_', ' ').title(),
                         '\n'.join(canonical_bytes(ref).decode().strip() for ref in spec[field])
                         or '(explicitly none)'])
    return '\n\n'.join(sections) + '\n'


def dependencies(value):
    """Extract only dependencies defined by known typed contracts; never guess JSON."""
    name = value['type']['name']
    spec = value['spec']
    result = []
    for entry in value.get('provenance', []):
        result.extend(entry['inputs'])
    result.extend(value.get('assurance', []))
    if name in {'workstream', 'claim', 'evidence', 'assessment', 'manuscript'}:
        result.append(spec['project'])
    if name in {'claim', 'evidence'}:
        result.append(spec['workstream'])
    if name == 'evidence':
        result.extend(relation['claim'] for relation in value['relations'])
    if name == 'assessment':
        result.append(spec['subject'])
        result.extend(spec['evidence'])
        result.extend(spec.get('isolation_receipt', {}).get('inputs', []))
    if name == 'manuscript':
        for field in ('claims', 'evidence', 'materials', 'external_references'):
            result.extend(spec[field])
    if name.startswith('math-') and name in {'math-statement-projection', 'math-proof-projection', 'math-review-projection'}:
        result.extend([spec['project'], spec['workstream'], spec['record'], *spec['inputs'].values()])
    if name == 'external-reference':
        result.extend(spec['receipt'][field] for field in ('content', 'license', 'log'))
    return result


def covers(outer, inner):
    checked(validate_scope(outer))
    checked(validate_scope(inner))
    if outer == 'whole_subject':
        return True
    if inner == 'whole_subject':
        return False
    return all(any(item == prefix or item.startswith(prefix + '/') for prefix in outer)
               for item in inner)


def validate_external(value, records):
    checked(validate_artifact_envelope(value, 'external-reference'))
    spec = value['spec']
    fields(spec, {'target', 'purpose', 'required_scope', 'receipt'}, 'external reference')
    checked(validate_target(spec['target']))
    from research_os.validation.semantics.common import validate_target as semantic_target
    checked(semantic_target(spec['target'], fixed=True))
    text(spec['purpose'], 'external purpose')
    checked(validate_scope(spec['required_scope']))
    receipt = spec['receipt']
    fields(receipt, {'retrieved_at', 'resolved_locator', 'sha256', 'content', 'license', 'log'}, 'retrieval receipt')
    checked(validate_timestamp(receipt['retrieved_at'], '/receipt/retrieved_at'))
    checked(validate_target(receipt['resolved_locator']))
    require(receipt['resolved_locator'] == spec['target'], 'external resolved locator changed; no silent substitution')
    for field in ('content', 'license', 'log'):
        checked(validate_fixed_ref(receipt[field]))
        require(fixed_ref_key(receipt[field]) in records, 'external receipt dependency missing: ' + field)
        require(bool(records[fixed_ref_key(receipt[field])][1].strip()), 'empty receipt evidence: ' + field)
    require(receipt['sha256'] == receipt['content']['sha256'], 'external receipt content digest mismatch')
    if spec['target']['kind'] == 'uri':
        require(receipt['sha256'] == spec['target']['sha256'], 'external target digest mismatch')


def validate_graph(manifest, payloads):
    checked(validate_artifact_envelope(manifest, 'publication'))
    spec = manifest['spec']
    fields(spec, MANIFEST_FIELDS, 'Publication')
    require(spec['profile'] in PROFILES and spec['profile_version'] == '1.0.0', 'unsupported profile/version')
    name = spec['publication']
    require(len(safe_parts(name)) == 1, 'Publication name must be one safe path component')
    require(manifest['target'] == {'kind': 'git', 'path': f'publications/{name}/manifest.json'}, 'Publication target mismatch')
    checked(validate_timestamp(spec['created_at'], '/created_at'))
    members = spec['members']
    require(isinstance(members, list) and bool(members), 'closed members required')
    records = {}
    aliases = set()
    for member in members:
        fields(member, {'path', 'ref', 'role', 'purpose', 'dependencies'}, 'member')
        path = member['path']
        safe_parts(path)
        require(path.casefold() not in aliases, 'duplicate or aliased member path')
        aliases.add(path.casefold())
        require(path.split('/')[0] not in {'publications', 'publication-events', 'publication-receipts'}, 'reserved member path')
        checked(validate_fixed_ref(member['ref']))
        checked(validate_target(member['ref']['target']))
        require(member['role'] in ROLES, 'unknown member role')
        text(member['purpose'], 'member purpose')
        refs(member['dependencies'], 'member dependencies')
        data = payloads[path]
        require(digest(data) == member['ref']['sha256'], 'member bytes drift: ' + path)
        target = member['ref']['target']
        if target['kind'] == 'git' and 'repository' not in target:
            require(target['path'] == path, 'local member path must match Git target')
        key = fixed_ref_key(member['ref'])
        require(key not in records, 'duplicate fixed member identity')
        records[key] = (member, data)

    def record(ref, expected=None):
        checked(validate_fixed_ref(ref))
        key = fixed_ref_key(ref)
        require(key in records, 'unclosed fixed reference')
        member, data = records[key]
        if expected is None:
            return member, data
        require(member['role'] == 'artifact', 'typed reference cannot resolve to an opaque material')
        value = parse_json(data)
        require(value['type']['name'] == expected, 'wrong referenced Artifact type: ' + expected)
        return value

    for entry in manifest.get('provenance', []):
        for ref in entry['inputs']:
            record(ref)
    for ref in manifest.get('assurance', []):
        record(ref, 'assessment')
    project = record(spec['project'], 'project')
    checked(validate_project(project))
    manuscript = record(spec['manuscript'], 'manuscript')
    validate_manuscript(manuscript)
    require(manuscript['spec']['profile'] == spec['profile'], 'Manuscript profile mismatch')
    require(manuscript['spec']['project'] == spec['project'], 'Manuscript Project mismatch')
    for author in manuscript['spec']['authors']:
        require(bool(principal_roles(project, author)), 'Manuscript author not bound to Project')
    for field in ('contributions', 'claims', 'evidence', 'conditions', 'limitations', 'materials', 'external_references'):
        require(spec[field] == manuscript['spec'][field], 'Manuscript/manifest mismatch: ' + field)
    for field in ('claims', 'evidence', 'materials', 'external_references'):
        refs(spec[field], field, nonempty=field in {'claims', 'evidence', 'materials'})
        for ref in spec[field]:
            record(ref)
    primaries = [m for m in members if m['role'] == 'primary-text']
    require(len(primaries) == 1 and primaries[0]['ref'] == spec['primary_text'], 'exactly one primary public text required')
    primary, pdf = record(spec['primary_text'])
    require(primary['dependencies'] == [spec['manuscript']], 'primary text must bind exactly the Manuscript')
    require(pdf == render_pdf(manuscript_text(manuscript)), 'PDF is not the deterministic Manuscript projection')

    from research_os.contracts import validate_artifact as validate_registered
    from research_os.workflows.mathematical.projections import TYPES as math_types
    admitted = {'project', 'workstream', 'claim', 'evidence', 'manuscript',
                'assessment', 'external-reference', *math_types}
    artifacts = {}
    for key, (member, data) in records.items():
        declared = member['dependencies']
        for ref in declared:
            record(ref)
        if member['role'] != 'artifact':
            continue
        value = parse_json(data)
        kind = value['type']['name']
        require(kind in admitted, 'unsupported typed publication member: ' + kind)
        checked(validate_registered(
            value, project={**project, 'target': spec['project']['target']},
            project_digest=spec['project']['sha256'],
            evidence_by_digest={ref['sha256']: {**record(ref, 'evidence'), 'target': ref['target']}
                                for ref in spec['evidence']},
            records={key: data for key, (_, data) in records.items()},
        ))
        if kind == 'assessment':
            if value['spec']['dimension'] == 'independent_review':
                subject_member, subject_bytes = record(value['spec']['subject'])
                subject_value = parse_json(subject_bytes) if subject_member['role'] == 'artifact' else {}
                if subject_value.get('type', {}).get('name') == 'manuscript':
                    actual_authors = set(subject_value['spec']['authors'])
                    receipt_authors = set(value['spec']['isolation_receipt']['authors'])
                    require(actual_authors == receipt_authors, 'isolation receipt must bind actual Manuscript authors')
                    require(value['spec']['assessor'] not in actual_authors, 'Manuscript author cannot independently review own work')
        target = value['target']
        expected = member['ref']['target']
        require(target == expected or (expected['kind'] == 'git' and 'repository' not in expected
                and target == {'kind': 'git', 'path': expected['path']}), 'Artifact target/member mismatch')
        if 'project' in value['spec']:
            require(value['spec']['project'] == spec['project'], 'cross-Project Artifact')
        for ref in dependencies(value):
            record(ref)
        artifacts[key] = value

    for kind, field in [('claim', 'claims'), ('evidence', 'evidence'), ('external-reference', 'external_references')]:
        actual = {key for key, value in artifacts.items() if value['type']['name'] == kind}
        listed = {fixed_ref_key(ref) for ref in spec[field]}
        require(actual == listed, 'unlisted or missing ' + field)
    external_specs = [record(ref, 'external-reference')['spec'] for ref in spec['external_references']]
    for member in members:
        target = member['ref']['target']
        if target['kind'] == 'uri' or 'repository' in target:
            require(any(item['target'] == target and item['receipt']['sha256'] == member['ref']['sha256']
                        for item in external_specs), 'external member requires matching retrieval receipt')
    listed_materials = {fixed_ref_key(ref) for ref in spec['materials']}
    require(listed_materials == {key for key, (member, _) in records.items() if member['role'] == 'material'},
            'material revision inventory must match every opaque material')
    for claim_ref in spec['claims']:
        claim = record(claim_ref, 'claim')
        supporting = [relation for ref in spec['evidence']
                      for relation in record(ref, 'evidence')['relations']
                      if fixed_ref_key(relation['claim']) == fixed_ref_key(claim_ref)]
        require(any(covers(r['scope'], claim['spec']['scope']) for r in supporting), 'Claim Evidence scope not covered')
        for field in ('conditions', 'limitations'):
            require(field in claim['spec'] and set(claim['spec'][field]) <= set(spec[field]), 'Claim boundaries omitted: ' + field)
        for relation in supporting:
            require(set(relation['conditions']) <= set(spec['conditions']), 'Evidence conditions omitted')
    fields(spec['assessments'], set(ASSURANCE_DIMENSIONS), 'six-axis Assessment refs')
    assessments = []
    assessment_keys = set()
    for dimension, axis_refs in spec['assessments'].items():
        refs(axis_refs, dimension)
        for ref in axis_refs:
            value = record(ref, 'assessment')
            require(value['spec']['dimension'] == dimension, 'Assessment axis mismatch')
            assessments.append(value)
            assessment_keys.add(fixed_ref_key(ref))
    require(assessment_keys == {k for k, v in artifacts.items() if v['type']['name'] == 'assessment'}, 'unlisted Assessment')
    checked(find_assurance_conflicts(assessments))
    required = {'structural_conformance', 'independent_review', 'human_acceptance',
                'empirical_reproducibility' if spec['profile'] == 'empirical-computational'
                else 'mathematical_argument_review'}
    require(isinstance(spec['required_gates'], list), 'required_gates must be an array')
    gates = [{'dimension': dim, 'subject': spec['manuscript'], 'scope': 'whole_subject'} for dim in sorted(required)]
    gates += spec['required_gates']
    for gate in gates:
        fields(gate, {'dimension', 'subject', 'scope'}, 'required gate')
        require(gate['dimension'] in ASSURANCE_DIMENSIONS, 'unknown required gate axis')
        record(gate['subject'])
        checked(validate_scope(gate['scope']))
        eligible = [a['spec'] for a in assessments if a['spec']['dimension'] == gate['dimension']
                    and a['spec']['subject'] == gate['subject'] and a['spec']['validity'] == 'active']
        require(any(a['verdict'] == 'pass' and covers(a['scope'], gate['scope']) for a in eligible),
                'required gate lacks active scoped pass: ' + gate['dimension'])
    return project
