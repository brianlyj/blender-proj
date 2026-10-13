# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy
from pathlib import Path
root=project_path('revision');frames=root/'dance_frames';frames.mkdir(exist_ok=True)
s=bpy.data.scenes['Classroom | Golden Hour'];s.camera=bpy.data.objects['Camera | 10 second dance'];s.render.engine='BLENDER_EEVEE';s.render.resolution_x=720;s.render.resolution_y=960;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
if hasattr(s,'eevee') and hasattr(s.eevee,'taa_render_samples'):s.eevee.taa_render_samples=32
for label,frame in [('Rest-clasped',1),('Dance-preview',69)]:
 s.frame_set(frame);s.render.filepath=str(root/(label+'.png'));bpy.ops.render.render(write_still=True,scene=s.name)
s.render.resolution_x=640;s.render.resolution_y=848
if hasattr(s,'eevee') and hasattr(s.eevee,'taa_render_samples'):s.eevee.taa_render_samples=16
for frame in range(1,241):
 s.frame_set(frame);s.render.filepath=str(frames/('frame_%03d.png'%(frame-1)));bpy.ops.render.render(write_still=True,scene=s.name)
 if frame%24==0:print('DANCE_SECOND',frame//24,'/10',flush=True)
