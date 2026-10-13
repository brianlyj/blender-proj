# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy
from pathlib import Path
root=project_path('')
frames=root/'animation_frames';frames.mkdir(exist_ok=True)
s=bpy.data.scenes['Classroom | Golden Hour']
s.camera=bpy.data.objects['Camera | character portrait']
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=640;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
for index,frame in enumerate(range(1,121,2)):
    s.frame_set(frame);s.render.filepath=str(frames/('frame_%03d.png'%index))
    bpy.ops.render.render(write_still=True,scene=s.name)
    print('ANIMATION_FRAME',index+1,'/ 60',flush=True)
