# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy,math
from mathutils import Vector
from pathlib import Path
r=project_path('revision');s=bpy.data.scenes['Classroom | Golden Hour'];rig=bpy.data.objects['MARI | refined character rig'];s.frame_set(1)
# Temporary close-up cameras in the background process only.
d=bpy.data.cameras.new('Diagnostic');c=bpy.data.objects.new('Diagnostic',d);s.collection.objects.link(c);d.type='ORTHO';d.ortho_scale=1.06;s.camera=c
s.render.resolution_x=750;s.render.resolution_y=800;s.render.resolution_percentage=100
for label,delta in [('front',(0,-3,.05)),('side',(3,-.1,.05))]:
 target=rig.location+Vector((0,.03,1.88));c.location=target+Vector(delta);c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(r/('Head-before-'+label+'.png'));bpy.ops.render.render(write_still=True,scene=s.name)
