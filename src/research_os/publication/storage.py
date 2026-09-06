"""No-follow, ordinary-file IO and exact-byte identity at the project boundary."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import unicodedata


class PublicationError(ValueError):
    """A required publication fact could not be established."""


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8') + b'\n'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_json(data: bytes):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise PublicationError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    def invalid(value):
        raise PublicationError('non-finite JSON number: ' + value)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid)


def safe_parts(path: str) -> list[str]:
    if (not isinstance(path, str) or not path or '\\' in path or ':' in path
            or any(ord(c) < 32 or ord(c) == 127 for c in path)
            or unicodedata.normalize('NFC', path) != path):
        raise PublicationError('unsafe publication path')
    parts = path.split('/')
    if any(p in {'', '.', '..'} or p.casefold() == '.git' or p.endswith((' ', '.'))
           for p in parts):
        raise PublicationError('unsafe publication path: ' + path)
    return parts


@contextmanager
def directory(root: Path, parts=(), *, create=False):
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts:
            if create:
                try:
                    os.mkdir(part, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd
    finally:
        os.close(fd)


def read_bytes(root: Path, path: str) -> bytes:
    parts = safe_parts(path)
    with directory(root, parts[:-1]) as parent:
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(fd, 'rb') as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise PublicationError('member must be a regular file: ' + path)
            return stream.read()


def write_exclusive(root: Path, path: str, data: bytes) -> None:
    parts = safe_parts(path)
    with directory(root, parts[:-1], create=True) as parent:
        temporary = '.write-' + os.urandom(16).hex()
        linked = False
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=parent)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.link(temporary, parts[-1], src_dir_fd=parent, dst_dir_fd=parent,
                    follow_symlinks=False)
            linked = True
            os.fsync(parent)
        except BaseException:
            if linked:
                os.unlink(parts[-1], dir_fd=parent)
            raise
        finally:
            os.unlink(temporary, dir_fd=parent)


def git_bytes(root: Path, target: dict) -> bytes:
    path = target['path']
    safe_parts(path)
    commit = target['commit']
    args = ['git', '-C', str(root), '--no-replace-objects']
    tree = subprocess.run(args + ['ls-tree', '-z', commit, '--', path],
                          check=True, capture_output=True).stdout
    records = tree.split(b'\0')
    matches = [record.split(b'\t', 1)[0].split() for record in records
               if b'\t' in record and record.split(b'\t', 1)[1] == path.encode()]
    if len(matches) != 1 or matches[0][0] not in {b'100644', b'100755'}:
        raise PublicationError('Git member is missing or not an ordinary blob: ' + path)
    return subprocess.run(args + ['cat-file', 'blob', matches[0][2].decode()],
                          check=True, capture_output=True).stdout
