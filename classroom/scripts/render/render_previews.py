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
s=bpy.data.scenes['Classroom | Golden Hour']
s.render.engine='BLENDER_EEVEE'
s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
s.frame_set(16)
s.camera=bpy.data.objects['Camera | classroom overview']
s.render.resolution_x=1200;s.render.resolution_y=1056
s.render.filepath=str(root/'Classroom-preview.png')
bpy.ops.render.render(write_still=True,scene=s.name)
s.camera=bpy.data.objects['Camera | character portrait']
s.render.resolution_x=800;s.render.resolution_y=1000
s.render.filepath=str(root/'Character-preview.png')
bpy.ops.render.render(write_still=True,scene=s.name)
print('PREVIEWS_COMPLETE',flush=True)
