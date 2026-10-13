# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=project_path('revision');s=bpy.context.scene;rig=bpy.data.objects['MARI | refined character rig'];coll=bpy.data.collections['05 Character | refined sports outfit']
# Closed lashes appear only during the blink, never across an open iris.
for o in coll.objects:
 if o.name.startswith('R3 | closed eyelash.'):
  for f,val in [(1,True),(37,True),(38,False),(40,True),(92,True),(93,False),(95,True),(120,True)]:
   o.hide_render=val;o.keyframe_insert(data_path='hide_render',frame=f)
# A small fill adjustment keeps the imported unlit skin from going grey under AgX.
face=bpy.data.objects['R2 | Face | sculpted anime']
for m in face.data.materials:
 if m.use_nodes:
  for node in m.node_tree.nodes:
   if node.type=='EMISSION':node.inputs['Strength'].default_value=1.35
# Check binding and deformation, including animated accessories and individually skinned fingers.
meshes=[o for o in coll.objects if o.type=='MESH']
errors=[]
for o in meshes:
 if not any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers):errors.append(o.name+' has no rig modifier')
 for v in o.data.vertices:
  if sum(g.weight for g in v.groups)<.99:errors.append(o.name+' has unweighted vertex '+str(v.index));break
poses={};samples={}
for frame in [1,16,39,64,94,120]:
 s.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 poses[frame]={p.name:list(p.matrix.translation) for p in rig.pose.bones}
 samples[frame]={}
 for name in ['R3 | Hair | continuous long silhouette','R3 | Headband | fitted white satin','R3 | Ear | shaped shell and fur.L','R2 | Face | sculpted anime']:
  o=bpy.data.objects[name];e=o.evaluated_get(dg);me=e.to_mesh();samples[frame][name]=[list(e.matrix_world@me.vertices[i].co) for i in [0,len(me.vertices)//2,len(me.vertices)-1]];e.to_mesh_clear()
loop_delta=max((Vector(poses[1][n])-Vector(poses[120][n])).length for n in poses[1])
# A persistent close-up camera makes the head easy to inspect without changing the classroom camera.
name='Camera | refined head detail';cam=bpy.data.objects.get(name)
if not cam:
 data=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,data);s.collection.objects.link(cam)
cam.data.type='ORTHO';cam.data.ortho_scale=1.13;target=rig.location+Vector((0,.03,1.92));cam.location=target+Vector((0,-3,.05));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
text=bpy.data.texts.get('START HERE | Classroom and character');text.clear();text.write('CLASSROOM + REFINED SPORTS CHARACTER\n\nScene: Classroom | Golden Hour\nCharacter rig: MARI | refined character rig\nSelect the armature, enter Pose Mode. 49 FK bones cover body, hands/fingers, feet/toes, hair, ears, halo and bag.\nAnimation: frames 1-120 at 24 fps, a five-second idle greeting with wave, weight shift, hair movement and two blinks. Spacebar plays the timeline.\nBlink shape keys on Eyes and Face close together; separate closed lashes appear during blinks.\nCameras: classroom overview, character portrait, and refined head detail.\n\nThe refined character stands near the teacher desk. Original character retained in the disabled collection: 05 Character | reference-inspired.\nThe refined collection is: 05 Character | refined sports outfit.\n\nHead revision: source-shaped ears, fitted satin headband, continuous long back hair, retained face-framing curves, surface-mounted flowers and corrected blink. Sports outfit and accessories rebuilt for this scene.\n\nAdapted face, eyes, hair, ears and halo from the user-supplied Mari model. See ASSET CREDIT | supplied model for creator and license.\n')
credit=bpy.data.texts.get('ASSET CREDIT | supplied model');credit.clear();credit.write('ADAPTED SOURCE ASSET\n[Blue Archive] -Mari (Idol)- | Chibi + Stage\nAuthor: VuckyZ / VückyZ\nSource: https://sketchfab.com/3d-models/blue-archive-mari-idol-chibi-stage-7412827541324d13a557d2f4a7f8d3c4\nLicense indicated in supplied GLB metadata: Creative Commons Attribution 4.0\nhttps://creativecommons.org/licenses/by/4.0/\n\nAdapted elements: face, eyes, eyebrows, mouth, hair, ears and halo.\nChanges: idol outfit and stage removed; face/head proportions changed; hair extended and skinned; ears mirrored and reshaped; fitted white headband and flowers; sports outfit and accessories rebuilt; new full body rig, finger/toe controls, greeting animation and blink deformation.\nAll textures packed into this blend file.\n')
for t in list(bpy.data.texts):
 if t.name.startswith('ASSET CREDIT | supplied model.'):bpy.data.texts.remove(t)
s.frame_start=1;s.frame_end=120;s.render.fps=24;s.frame_set(16);s.camera=bpy.data.objects['Camera | character portrait'];s.render.resolution_x=900;s.render.resolution_y=1150;s.render.resolution_percentage=100
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  area.spaces.active.region_3d.view_perspective='CAMERA'
  area.spaces.active.shading.type='MATERIAL'
  area.spaces.active.overlay.show_overlays=False
for o in bpy.context.selected_objects:o.select_set(False)
rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Classroom-refined.blend'))
report={'mesh_count':len(meshes),'bones':len(rig.data.bones),'frame_range':[1,120],'fps':24,'binding_errors':errors,'loop_bone_position_delta':loop_delta,'samples':samples}
(root/'validation.json').write_text(json.dumps(report,indent=2));(root/'ASSET-CREDIT.txt').write_text(credit.as_string(),encoding='utf-8')
result={k:v for k,v in report.items() if k!='samples'}
