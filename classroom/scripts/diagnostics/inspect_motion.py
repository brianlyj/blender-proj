# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy
from mathutils import Vector
s=bpy.context.scene;r=bpy.data.objects['MARI | refined character rig'];prev=None;jumps=[];feet=[]
for f in range(1,241):
 s.frame_set(f);bpy.context.view_layer.update();points={p.name:p.tail.copy() for p in r.pose.bones}
 if prev:
  for n,p in points.items():jumps.append(((p-prev[n]).length,f,n))
 prev=points
 for sign,suf in [(1,'L'),(-1,'R')]:feet.append(((r.pose.bones['foot.'+suf].head-Vector((sign*.155,0,.122))).length,f,suf))
result={'max_jumps':sorted(jumps,reverse=True)[:12],'foot_errors':sorted(feet,reverse=True)[:8]}
s.frame_set(1)
