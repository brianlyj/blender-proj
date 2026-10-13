# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import argparse
import json
from pathlib import Path
from blmcp.tools_helpers.connection import send_code

parser = argparse.ArgumentParser()
parser.add_argument('script')
args = parser.parse_args()
script_path = Path(args.script).resolve()
source = '__file__ = ' + repr(str(script_path)) + '\n' + script_path.read_text(encoding='utf-8-sig')
response = send_code(source, strict_json=False)
print(json.dumps(response, indent=2))
if response.get('status') != 'ok':
    raise SystemExit(1)
