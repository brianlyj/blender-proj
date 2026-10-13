"""One-time, reversible organization of the classroom working files.

Prepare writes a hash manifest and preserves the original scripts in a ZIP.
Moves are performed separately with native PowerShell, using that manifest.
Finalize updates script paths and verifies that every original file survived.
"""
import ast
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / 'reports/organization-manifest.json'
OLD_ROOT = 'C:/Users/ASUS/Downloads/mcp-1.0.3/classroom'
REFERENCE = Path('C:/Users/ASUS/AppData/Local/Temp/codex-clipboard-5a6ef3ce-e2bf-4530-baac-ec52ff10f487.png')
DIRECTORIES = {
    'animation_frames': 'renders/initial_greeting_frames',
    'revision/animation_frames': 'renders/revision_greeting_frames',
    'revision/dance_frames': 'renders/dance_frames',
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def destination(relative):
    p = Path(relative)
    name = p.name
    for old, new in DIRECTORIES.items():
        if relative.startswith(old + '/'):
            return new + relative[len(old):]
    if p.suffix == '.py':
        if name in ('helpers.py', 'blender_bridge.py'):
            category = 'shared'
        elif name.startswith('render_'):
            category = 'render'
        elif name == 'animate_dance.py':
            category = 'animation'
        elif name.startswith(('inspect_', 'head_', 'band_', 'list_', 'extract_', 'validate_', 'organization-')):
            category = 'diagnostics'
        elif '/' not in relative:
            category = 'initial'
        else:
            category = 'refinement'
        if relative == 'inspect_rig.py':
            name = 'inspect_rig_initial.py'
        if name == 'organization-inspect.py':
            name = 'inspect_external_assets.py'
        return f'scripts/{category}/{name}'
    if name in ('Classroom-dance.blend', 'Classroom-dance-10s.mp4', 'ASSET-CREDIT.txt'):
        return f'deliverables/{name}'
    if name in ('Dance-preview.png', 'Rest-clasped.png'):
        return f'deliverables/previews/{name}'
    if p.suffix == '.blend1':
        return f'archive/backups/{name}'
    if name.startswith('Classroom-before-'):
        return f'archive/checkpoints/{name}'
    if name.startswith('Reference-'):
        return f'references/{name}'
    if name.endswith('-texture.png'):
        return f'references/textures/{name}'
    if p.suffix == '.json':
        subdir = 'final' if name.startswith('dance-') else 'diagnostics'
        return f'reports/{subdir}/{name}'
    return f"archive/{'refinement' if relative.startswith('revision/') else 'initial'}/{name}"

def legacy_relative(value):
    value = value.replace('\\', '/')
    if value == OLD_ROOT:
        return ''
    if value.startswith(OLD_ROOT + '/'):
        return value[len(OLD_ROOT) + 1:]
    if value == 'C:/Users/ASUS/Downloads/blue_archive_-mari_idol-__chibi__stage.glb':
        return 'revision/Reference-mari.glb'
    if value == REFERENCE.as_posix():
        return 'references/Sports-outfit-reference.png'
    return None

BOOTSTRAP = '''# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

'''

def rewrite(source, filename):
    # Edit only path expressions; retain the original formatting and comments.
    tree = ast.parse(source)
    raw = source.encode('utf-8')
    lines = raw.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    replacements = []
    def visit(node):
        value = None
        as_path = False
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'Path' and len(node.args) == 1 and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            value = legacy_relative(node.args[0].value)
            as_path = True
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = legacy_relative(node.value)
        if value is not None:
            code = f'project_path({value!r})'
            if not as_path:
                code = f'str({code})'
            replacements.append((offsets[node.lineno-1]+node.col_offset, offsets[node.end_lineno-1]+node.end_col_offset, code.encode()))
        else:
            for child in ast.iter_child_nodes(node):
                visit(child)
    visit(tree)
    for start, end, replacement in sorted(replacements, reverse=True):
        raw = raw[:start] + replacement + raw[end:]
    rewritten = BOOTSTRAP + raw.decode('utf-8')
    if filename == 'blender_bridge.py':
        rewritten = rewritten.replace("response = send_code(Path(args.script).read_text(encoding='utf-8-sig'), strict_json=False)", "script_path = Path(args.script).resolve()\nsource = '__file__ = ' + repr(str(script_path)) + '\\n' + script_path.read_text(encoding='utf-8-sig')\nresponse = send_code(source, strict_json=False)")
    compile(rewritten, filename, 'exec')
    return rewritten

PATH_MODULE = '''"""Resolve historical script paths into the organized project layout.

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
        self.logical = str(logical).replace('\\\\', '/').strip('/')

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
'''

def prepare():
    if PLAN.exists():
        raise RuntimeError('Organization manifest already exists; refusing to repeat the migration')
    originals = sorted([p for p in ROOT.iterdir() if p.is_file()] + list((ROOT/'revision').rglob('*')) + list((ROOT/'animation_frames').rglob('*')))
    originals = [p for p in originals if p.is_file()]
    entries = []
    for p in originals:
        relative = p.relative_to(ROOT).as_posix()
        target = destination(relative)
        if (ROOT/target).exists():
            raise RuntimeError(f'Destination already exists: {target}')
        if p.suffix == '.py':
            rewrite(p.read_text(encoding='utf-8-sig'), p.name)
        entries.append({'original': relative, 'organized': target, 'bytes': p.stat().st_size, 'original_sha256': digest(p)})
    assert len({e['organized'].casefold() for e in entries}) == len(entries), 'Destination collision'
    PLAN.parent.mkdir(parents=True, exist_ok=True)
    (ROOT/'archive').mkdir(exist_ok=True)
    with zipfile.ZipFile(ROOT/'archive/scripts-before-organization.zip', 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for p in originals:
            if p.suffix == '.py':
                z.write(p, p.relative_to(ROOT).as_posix())
    PLAN.write_text(json.dumps({'status':'prepared', 'files':entries}, indent=2), encoding='utf-8')
    print(json.dumps({'files_to_move':len(entries), 'bytes':sum(e['bytes'] for e in entries), 'manifest':str(PLAN)}))

def finalize():
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    assert plan['status'] == 'prepared'
    for entry in plan['files']:
        p = ROOT/entry['organized']
        assert digest(p) == entry['original_sha256'], f'Hash mismatch: {p}'
        assert not (ROOT/entry['original']).exists(), f'Original was not moved: {entry}'
    for entry in plan['files']:
        p = ROOT/entry['organized']
        if p.suffix == '.py':
            p.write_text(rewrite(p.read_text(encoding='utf-8-sig'), p.name), encoding='utf-8')
        entry['organized_sha256'] = digest(p)
    shared = ROOT/'scripts/shared'
    shared.mkdir(parents=True, exist_ok=True)
    (shared/'project_paths.py').write_text(PATH_MODULE, encoding='utf-8')
    file_map = {e['original']:e['organized'] for e in plan['files'] if not any(e['original'].startswith(d+'/') for d in DIRECTORIES)}
    (shared/'path-map.json').write_text(json.dumps({'files':file_map, 'directories':dict(DIRECTORIES, revision='archive/refinement')}, indent=2), encoding='utf-8')
    if REFERENCE.exists():
        shutil.copy2(REFERENCE, ROOT/'references/Sports-outfit-reference.png')
    plan['status'] = 'organized_and_hash_verified'
    plan['original_scripts_backup'] = 'archive/scripts-before-organization.zip'
    PLAN.write_text(json.dumps(plan, indent=2), encoding='utf-8')
    for p in (ROOT/'scripts').rglob('*.py'):
        compile(p.read_text(encoding='utf-8-sig'), str(p), 'exec')
    sys.path.insert(0, str(shared))
    from project_paths import project_path
    for entry in plan['files']:
        assert Path(project_path(entry['original'])) == (ROOT/entry['organized']).resolve()
    print(json.dumps({'moved_files_verified':len(plan['files']), 'scripts_compile':True, 'path_mappings_verified':True}))

if __name__ == '__main__':
    {'prepare':prepare, 'finalize':finalize}[sys.argv[1]]()
