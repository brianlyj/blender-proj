# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy,os
result={'filepath':bpy.data.filepath,'dirty':bpy.data.is_dirty,'images':[{'name':i.name,'path':i.filepath,'packed':bool(i.packed_file),'source':i.source} for i in bpy.data.images if i.source=='FILE'],'libraries':[l.filepath for l in bpy.data.libraries]}
