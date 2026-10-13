# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy
s=bpy.context.scene;rig=bpy.data.objects['MARI | refined character rig'];c=bpy.data.collections['05 Character | refined sports outfit']
result={'view':{'transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma},'text_names':[t.name for t in bpy.data.texts],'action':rig.animation_data.action.name,'objects':len(c.objects),'bones':len(rig.data.bones),'unweighted':[o.name for o in c.objects if o.type=='MESH' and not o.vertex_groups]}
