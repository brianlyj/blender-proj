# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy,json
r=bpy.data.objects['MARI | refined character rig'];c=bpy.data.collections['05 Character | refined sports outfit'];s=bpy.context.scene
result={'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'parent':b.parent.name if b.parent else None,'length':b.length} for b in r.data.bones},'objects':[o.name for o in c.objects if any(x in o.name.lower() for x in ['sleeve','cuff','bottle','palm','wrist','upper','arm','hand','neck'])]}
