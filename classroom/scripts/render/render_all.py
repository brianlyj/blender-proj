# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import runpy
from pathlib import Path
root=project_path('')
runpy.run_path(str(root/'render_previews.py'))
runpy.run_path(str(root/'render_animation.py'))
