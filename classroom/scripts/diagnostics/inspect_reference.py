# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy,json
from mathutils import Vector,Matrix
from pathlib import Path
root=project_path('revision')
s=bpy.data.scenes.new('Reference inspection');bpy.context.window.scene=s
bpy.ops.import_scene.gltf(filepath=str(project_path('revision/Reference-mari.glb')))
obs=list(s.objects)
info=[]
for o in obs:
    if o.type=='MESH':
        pts=[o.matrix_world@Vector(c) for c in o.bound_box]
        info.append({'name':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'materials':[m.name if m else None for m in o.data.materials],'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]})
print('REFERENCE_MESHES='+json.dumps(info),flush=True)
(root/'mesh_inventory.json').write_text(json.dumps(info,indent=2))
for o in obs:
    if o.type=='MESH':
        o.data.transform(o.matrix_world);o.parent=None;o.matrix_world.identity();o.data.transform(Matrix.Scale(1/25000,4))
        if any(m and m.name=='stage' for m in o.data.materials):o.hide_render=True
pts=[o.matrix_world@Vector(c) for o in obs if o.type=='MESH' and not o.hide_render for c in o.bound_box]
lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)]);mid=(lo+hi)/2;extent=max(hi-lo)
world=bpy.data.worlds.new('Reference studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.17,.20,.25,1);world.node_tree.nodes['Background'].inputs[1].default_value=.8;s.world=world
cd=bpy.data.cameras.new('Inspection camera');cam=bpy.data.objects.new('Inspection camera',cd);s.collection.objects.link(cam);s.camera=cam;cd.type='ORTHO';cd.ortho_scale=extent*1.15
cam.location=mid+Vector((extent*.7,-extent*1.8,extent*.65));cam.rotation_euler=(mid-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard';s.render.image_settings.file_format='PNG';s.render.filepath=str(root/'Reference-model.png')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Reference-inspection.blend'))
bpy.ops.render.render(write_still=True,scene=s.name)


