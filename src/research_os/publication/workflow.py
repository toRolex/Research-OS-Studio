"""Staged, explicitly confirmed, closed Publication snapshots and append-only events."""
from __future__ import annotations

import copy
import ctypes
import os
from pathlib import Path
import shutil
import subprocess
import sys

from research_os.validation.semantics.identity import principal_roles
from research_os.validation.semantics.common import validate_timestamp

from .contracts import (
    MANIFEST_FIELDS, artifact, checked, fields, require, text, validate_graph,
)
from .storage import (
    PublicationError, canonical_bytes, digest, directory, git_bytes, parse_json,
    read_bytes, safe_parts, write_exclusive,
)

ERRORS = (ValueError, TypeError, KeyError, IndexError, AttributeError, OSError, subprocess.SubprocessError)
VALIDATOR = {'name': 'publication-preflight', 'version': '1.0.0'}


def _payloads(root, manifest, *, frozen=False):
    payloads = {}
    for member in manifest['spec']['members']:
        path = member['path']
        data = read_bytes(root, 'files/' + path if frozen else path)
        payloads[path] = data
        target = member['ref']['target']
        if not frozen and target['kind'] == 'git' and 'repository' not in target:
            require(git_bytes(root, target) == data, 'working bytes differ from fixed Git blob: ' + path)
    return payloads


def _report(manifest, issues):
    try:
        subject = {'target': manifest['target'], 'sha256': digest(canonical_bytes(manifest))}
    except ERRORS:
        subject = None
    return {'contract': {'name': 'research-os/publication-preflight', 'version': '1.0.0'},
            'validator': VALIDATOR, 'subject': subject,
            'verdict': 'fail' if issues else 'pass', 'exit_code': 1 if issues else 0,
            'issues': issues, 'evidence': [] if subject is None else [subject],
            'stop_reason': 'validation_failed' if issues else 'awaiting_explicit_confirmation',
            'next_steps': []}


def preflight(project: Path, manifest: object) -> dict:
    """Read-only revalidation; missing, malformed, drifted and unknown gates all fail."""
    try:
        snapshot = copy.deepcopy(manifest)
        validate_graph(snapshot, _payloads(Path(project), snapshot))
        return _report(snapshot, [])
    except ERRORS as exc:
        return _report(manifest, [{'code': 'publication.preflight', 'message': str(exc)}])


def stage_publication(project: Path, request: dict, *, stage_path: str | None = None) -> dict:
    """Validate a complete user-selected member set, optionally persist exclusively.

    The stage is a final candidate manifest, not an approval. No Git commit, data
    download, workflow call, new Assessment or human acceptance is synthesized.
    """
    try:
        spec = copy.deepcopy(request)
        fields(spec, MANIFEST_FIELDS - {'profile_version'}, 'stage request')
        spec['profile_version'] = '1.0.0'
        manifest = artifact(f"publications/{spec['publication']}/manifest.json", 'publication', spec)
        report = preflight(project, manifest)
        require(report['exit_code'] == 0, str(report['issues']))
        if stage_path is not None:
            require(safe_parts(stage_path)[0] not in {'publications', 'publication-events'}, 'stage path is reserved')
            write_exclusive(Path(project), stage_path, canonical_bytes(manifest))
        return manifest
    except ERRORS as exc:
        raise PublicationError(str(exc)) from exc


def confirmation_text(manifest: dict) -> str:
    return f"FREEZE {manifest['spec']['publication']} SHA256 {digest(canonical_bytes(manifest))}"


def _rename_exclusive(parent_fd, source, destination):
    """Atomic no-replace directory publication on supported POSIX hosts."""
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == 'darwin':
        operation = libc.renameatx_np
        flag = 4  # RENAME_EXCL
    elif sys.platform.startswith('linux'):
        operation = libc.renameat2
        flag = 1  # RENAME_NOREPLACE
    else:
        raise PublicationError('atomic no-replace directory rename unavailable')
    operation.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    operation.restype = ctypes.c_int
    if operation(parent_fd, source.encode(), parent_fd, destination.encode(), flag) != 0:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code), destination)


def freeze_publication(project: Path, manifest: dict, confirmation: str, principal: str) -> dict:
    """Recheck final bytes and user role, then publish once with a freeze receipt."""
    temp_name = None
    cleanup_fd = None
    root = Path(project)
    try:
        snapshot = copy.deepcopy(manifest)
        payloads = _payloads(root, snapshot)
        project_artifact = validate_graph(snapshot, payloads)
        require(confirmation == confirmation_text(snapshot), 'exact final manifest digest confirmation required')
        require('user' in principal_roles(project_artifact, principal), 'freeze principal must have Project user role')
        name = snapshot['spec']['publication']
        receipt = {'contract': {'name': 'research-os/freeze-receipt', 'version': '1.0.0'},
                   'publication': snapshot['target'], 'manifest_sha256': digest(canonical_bytes(snapshot)),
                   'principal': principal, 'confirmation': confirmation,
                   'confirmed_at': snapshot['spec']['created_at'], 'validator': VALIDATOR}
        with directory(root, ['publications'], create=True) as parent:
            cleanup_fd = os.dup(parent)
            # Parent descriptor remains anchored through publication, including swaps
            # of a directory entry by an unrelated process.
            temp_name = '.stage-' + os.urandom(16).hex()
            os.mkdir(temp_name, 0o700, dir_fd=parent)
            temp_fd = os.open(temp_name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            try:
                for path, data in payloads.items():
                    _write_at(temp_fd, 'files/' + path, data)
                _write_at(temp_fd, 'manifest.json', canonical_bytes(snapshot))
                _write_at(temp_fd, 'freeze-receipt.json', canonical_bytes(receipt))
                os.fsync(temp_fd)
            finally:
                os.close(temp_fd)
            # Re-read live inputs before committing. If changed, demand a new stage.
            require(_payloads(root, snapshot) == payloads, 'input bytes changed during freeze')
            _rename_exclusive(parent, temp_name, name)
            temp_name = None
            os.fsync(parent)
        return receipt
    except ERRORS as exc:
        raise PublicationError(str(exc)) from exc
    finally:
        if cleanup_fd is not None:
            try:
                if temp_name is not None:
                    shutil.rmtree(temp_name, dir_fd=cleanup_fd)
            finally:
                os.close(cleanup_fd)


def _write_at(root_fd, path, data):
    parts = safe_parts(path)
    fd = os.dup(root_fd)
    try:
        for part in parts[:-1]:
            try:
                os.mkdir(part, 0o700, dir_fd=fd)
            except FileExistsError:
                pass
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        output = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
        with os.fdopen(output, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.fsync(fd)
    finally:
        os.close(fd)


def _frozen(project, name):
    require(len(safe_parts(name)) == 1, 'invalid Publication name')
    base = f'publications/{name}'
    manifest_bytes = read_bytes(project, base + '/manifest.json')
    manifest = parse_json(manifest_bytes)
    require(manifest_bytes == canonical_bytes(manifest), 'noncanonical frozen manifest')
    require(manifest['spec']['publication'] == name, 'frozen Publication name mismatch')
    payloads = {m['path']: read_bytes(project, base + '/files/' + m['path']) for m in manifest['spec']['members']}
    project_artifact = validate_graph(manifest, payloads)
    receipt = parse_json(read_bytes(project, base + '/freeze-receipt.json'))
    fields(receipt, {'contract', 'publication', 'manifest_sha256', 'principal', 'confirmation', 'confirmed_at', 'validator'}, 'freeze receipt')
    require(receipt['contract'] == {'name': 'research-os/freeze-receipt', 'version': '1.0.0'}
            and receipt['validator'] == VALIDATOR, 'unsupported freeze receipt')
    require(receipt['manifest_sha256'] == digest(manifest_bytes)
            and receipt['publication'] == manifest['target']
            and receipt['confirmation'] == confirmation_text(manifest)
            and receipt['confirmed_at'] == manifest['spec']['created_at'], 'freeze receipt binding mismatch')
    require('user' in principal_roles(project_artifact, receipt['principal']), 'invalid freeze receipt user')
    expected = {'manifest.json', 'freeze-receipt.json'} | {'files/' + p for p in payloads}
    actual = set()
    for folder, dirs, files in os.walk(Path(project) / base, followlinks=False):
        for entry in dirs + files:
            require(not (Path(folder) / entry).is_symlink(), 'frozen package contains symlink')
        actual.update((Path(folder) / entry).relative_to(Path(project) / base).as_posix() for entry in files)
    require(actual == expected, 'frozen package is not the closed declared file set')
    return manifest, project_artifact


def verify_publication(project: Path, name: str) -> dict:
    """Verify only the immutable snapshot, without depending on current upstream files."""
    manifest = None
    try:
        manifest, _ = _frozen(Path(project), name)
        report = _report(manifest, [])
        report['stop_reason'] = 'verification_complete'
        return report
    except ERRORS as exc:
        return _report(manifest, [{'code': 'publication.integrity', 'message': str(exc)}])


def append_event(project: Path, name: str, event: dict, principal: str, confirmation: str) -> dict:
    """Append user-confirmed supersede/retract/notice; never edit the original bundle."""
    try:
        manifest, project_artifact = _frozen(Path(project), name)
        kind = event['kind']
        require(kind in {'supersede', 'retract', 'notice'}, 'unsupported user event kind')
        fields(event, {'kind', 'reason', 'issued_at'} | ({'replacement'} if kind == 'supersede' else set()), 'Publication event')
        text(event['reason'], 'event reason')
        checked(validate_timestamp(event['issued_at'], '/issued_at'))
        require('user' in principal_roles(project_artifact, principal), 'event requires Project user')
        require(confirmation == f'{kind.upper()} {name}', 'explicit event confirmation required')
        spec = copy.deepcopy(event)
        if kind == 'supersede':
            replacement, _ = _frozen(Path(project), event['replacement'])
            require(event['replacement'] != name, 'cannot supersede itself')
            require(replacement['spec']['project'] == manifest['spec']['project'], 'replacement Project differs')
            spec['replacement'] = {'target': replacement['target'], 'sha256': digest(canonical_bytes(replacement))}
        spec.update(publication={'target': manifest['target'], 'sha256': digest(canonical_bytes(manifest))}, principal=principal)
        return _event_write(Path(project), name, spec)
    except ERRORS as exc:
        raise PublicationError(str(exc)) from exc


def _event_write(project, name, spec):
    # Event digest chooses an append-only filename, not an Artifact identity scheme.
    path = f'publication-events/{name}/{digest(canonical_bytes(spec))}.json'
    value = artifact(path, 'publication-event', spec)
    write_exclusive(project, path, canonical_bytes(value))
    return {'path': path, 'artifact': value}


def stale_audit(project: Path, name: str, *, issued_at: str) -> dict:
    """Append observed current-byte differences; missing sources are not successes."""
    try:
        manifest, _ = _frozen(Path(project), name)
        checked(validate_timestamp(issued_at, '/issued_at'))
        changes = []
        for member in manifest['spec']['members']:
            try:
                current = digest(read_bytes(Path(project), member['path']))
                if current != member['ref']['sha256']:
                    changes.append({'path': member['path'], 'expected_sha256': member['ref']['sha256'],
                                    'actual_sha256': current, 'observation': 'changed'})
            except (OSError, PublicationError) as exc:
                changes.append({'path': member['path'], 'expected_sha256': member['ref']['sha256'],
                                'actual_sha256': None, 'observation': 'unavailable', 'detail': str(exc)})
        spec = {'kind': 'stale-audit', 'issued_at': issued_at,
                'publication': {'target': manifest['target'], 'sha256': digest(canonical_bytes(manifest))},
                'changes': changes, 'validator': {'name': 'publication-stale-audit', 'version': '1.0.0'}}
        return _event_write(Path(project), name, spec)['artifact']
    except ERRORS as exc:
        raise PublicationError(str(exc)) from exc
