# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy
from pathlib import Path
from mathutils import Vector
root=project_path('revision');s=bpy.data.scenes['Classroom | Golden Hour'];s.camera=bpy.data.objects['Camera | 10 second dance'];s.render.engine='BLENDER_EEVEE';s.render.resolution_x=720;s.render.resolution_y=960;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
for name,frame in [('Rest-clasped',1),('Dance-left',57),('Dance-right',69),('Dance-middle',121)]:
 s.frame_set(frame);s.render.filepath=str(root/(name+'.png'));bpy.ops.render.render(write_still=True,scene=s.name)
