# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy
rig=bpy.data.objects['CHARACTER_RIG | select to pose']
s=bpy.context.scene
checks={}
for f in [1,31,61,91,120]:
    s.frame_set(f)
    checks[str(f)]={n:[round(v,3) for v in rig.pose.bones[n].tail] for n in ['hand.L','hand.R','head','foot.L','foot.R']}
s.frame_set(16)
result={'poses':checks,'rig_bones':len(rig.data.bones),'character_meshes':len([o for o in rig.children if o.type=='MESH']),'unskinned':[o.name for o in rig.children if o.type=='MESH' and not any(m.type=='ARMATURE' for m in o.modifiers)],'shape_key_meshes':len([o for o in rig.children if o.type=='MESH' and o.data.shape_keys])}
