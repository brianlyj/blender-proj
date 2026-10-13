# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy,json
from mathutils import Vector,Matrix
s=bpy.data.scenes['Reference inspection'];bpy.context.window.scene=s
print(json.dumps({'camera':{'location':list(s.camera.location),'ortho':s.camera.data.ortho_scale},'objects':[{'name':o.name,'loc':list(o.location),'scale':list(o.scale),'verts':[list(v.co) for v in o.data.vertices[:1]],'render':not o.hide_render} for o in s.objects if o.type=='MESH']}),flush=True)
for o in s.objects:
    if o.type=='MESH':o.matrix_world=Matrix.Identity(4)
bpy.context.view_layer.update()
pts=[o.matrix_world@Vector(c) for o in s.objects if o.type=='MESH' and not o.hide_render for c in o.bound_box]
lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)]);mid=(lo+hi)/2;extent=max(hi-lo)
s.camera.location=mid+Vector((extent*.7,-extent*1.8,extent*.4));s.camera.rotation_euler=(mid-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=extent*1.18
print('BOUNDS',list(lo),list(hi),flush=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
bpy.ops.render.render(write_still=True,scene=s.name)
