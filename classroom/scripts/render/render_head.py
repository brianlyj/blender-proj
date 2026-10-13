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
d=bpy.data.cameras.new('Diagnostic');c=bpy.data.objects.new('Diagnostic',d);s.collection.objects.link(c);d.type='ORTHO';d.ortho_scale=1.13;s.camera=c
s.render.resolution_x=800;s.render.resolution_y=850;s.render.resolution_percentage=100
for label,delta,fr in [('front',(0,-3,.05),1),('side',(3,-.1,.05),1),('blink',(0,-3,.05),39)]:
 s.frame_set(fr);target=rig.location+Vector((0,.03,1.92));c.location=target+Vector(delta);c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(r/('Head-corrected-'+label+'.png'));bpy.ops.render.render(write_still=True,scene=s.name)
s.frame_set(16);s.camera=bpy.data.objects['Camera | character portrait'];s.render.resolution_x=900;s.render.resolution_y=1150;s.render.filepath=str(r/'Character-refined-preview.png');bpy.ops.render.render(write_still=True,scene=s.name)
