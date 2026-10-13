"""Resolve historical script paths into the organized project layout.

project_path retains the logical path through / operations, including dynamic
render filenames; all filesystem access resolves through path-map.json.
"""
import json
import os
from pathlib import Path, PurePosixPath

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_MAP = json.loads(Path(__file__).with_name('path-map.json').read_text(encoding='utf-8'))

class _ProjectPath(os.PathLike):
    def __init__(self, logical=''):
        self.logical = str(logical).replace('\\', '/').strip('/')

    @property
    def path(self):
        logical = self.logical
        target = _MAP['files'].get(logical)
        if target is None:
            for old, new in sorted(_MAP['directories'].items(), key=lambda item: -len(item[0])):
                if logical == old or logical.startswith(old + '/'):
                    target = new + logical[len(old):]
                    break
        if target is None:
            target = logical
        resolved = (PROJECT_ROOT / target).resolve()
        if not resolved.is_relative_to(PROJECT_ROOT):
            raise ValueError('Project path escapes the project folder')
        return resolved

    def __truediv__(self, child):
        return _ProjectPath(str(PurePosixPath(self.logical) / os.fspath(child)))

    def __fspath__(self):
        return str(self.path)

    def __str__(self):
        return str(self.path)

    def __getattr__(self, name):
        return getattr(self.path, name)

def project_path(logical=''):
    return _ProjectPath(logical)
