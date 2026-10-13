# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy
from pathlib import Path
root=project_path('revision');frames=root/'animation_frames';frames.mkdir(exist_ok=True)
s=bpy.data.scenes['Classroom | Golden Hour'];s.render.engine='BLENDER_EEVEE';s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.frame_set(16);s.camera=bpy.data.objects['Camera | character portrait'];s.render.resolution_x=900;s.render.resolution_y=1150;s.render.filepath=str(root/'Character-refined-preview.png');bpy.ops.render.render(write_still=True,scene=s.name)
s.camera=bpy.data.objects['Camera | refined head detail'];s.render.resolution_x=800;s.render.resolution_y=850;s.render.filepath=str(root/'Head-refined-preview.png');bpy.ops.render.render(write_still=True,scene=s.name)
s.camera=bpy.data.objects['Camera | classroom overview'];s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.filepath=str(root/'Classroom-refined-preview.png');bpy.ops.render.render(write_still=True,scene=s.name)
s.camera=bpy.data.objects['Camera | character portrait'];s.render.resolution_x=720;s.render.resolution_y=920
for index,frame in enumerate(range(1,121,2)):
 s.frame_set(frame);s.render.filepath=str(frames/('frame_%03d.png'%index));bpy.ops.render.render(write_still=True,scene=s.name);print('ANIMATION_FRAME',index+1,'/60',flush=True)
