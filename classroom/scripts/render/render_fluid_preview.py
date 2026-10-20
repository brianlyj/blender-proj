"""Render actual motion for visual review; does not save or change the blend."""
import bpy, importlib.util
from pathlib import Path
project=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('fluid_render_controls',project/'scripts/animation/mari_emote_controls.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
scene=bpy.data.scenes['Classroom | Golden Hour'];bpy.context.window.scene=scene
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=360;scene.render.resolution_y=480;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
if hasattr(scene,'eevee'):scene.eevee.taa_render_samples=12
for number,name,stride in [(10,'fluid-dance',1),(6,'fluid-paws',1)]:
    entry=c.select_emote(scene,number)
    folder=project/'renders'/name;folder.mkdir(parents=True,exist_ok=True)
    for index,frame in enumerate(range(entry['start'],entry['end']+1,stride)):
        target=folder/('frame_%03d.png'%index)
        if target.exists():continue
        scene.frame_set(frame);scene.render.filepath=str(target)
        bpy.ops.render.render(write_still=True)
        if index%24==0:print('FLUID_PREVIEW',name,index,flush=True)
print('FLUID_PREVIEWS_RENDERED',flush=True)
