# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy,json
p=str(project_path('revision/Reference-inspection.blend'))
with bpy.data.libraries.load(p,link=False) as (src,dst):
 print(json.dumps(src.objects),flush=True)
