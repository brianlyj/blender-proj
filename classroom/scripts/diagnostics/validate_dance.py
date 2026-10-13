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
root=project_path('revision');s=bpy.context.scene;rig=bpy.data.objects['MARI | refined character rig'];c=bpy.data.collections['05 Character | refined sports outfit']
errors=[];meshes=[o for o in c.objects if o.type=='MESH']
for o in meshes:
 if not any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers):errors.append(o.name+' has no rig modifier')
 if any(abs(sum(g.weight for g in v.groups)-1)>.001 for v in o.data.vertices):errors.append(o.name+' has non-normalized weights')
footmax=0;shoulder_bounds={};prev=None;largest_jump=0;bone_start={}
for f in range(1,241):
 s.frame_set(f);bpy.context.view_layer.update()
 for sign,suf in [(1,'L'),(-1,'R')]:footmax=max(footmax,(rig.pose.bones['foot.'+suf].head-Vector((sign*.155,0,.122))).length)
 locations=[p.tail.copy() for p in rig.pose.bones]
 if prev:largest_jump=max(largest_jump,max((a-b).length for a,b in zip(locations,prev)))
 prev=locations
 if f==1:bone_start={p.name:p.matrix.copy() for p in rig.pose.bones}
 if f in [1,57,69,121,240]:
  dg=bpy.context.evaluated_depsgraph_get();shoulder_bounds[f]={}
  for suf in ['L','R']:
   o=bpy.data.objects['R4 | Connected sleeve and shoulder.'+suf];ev=o.evaluated_get(dg);me=ev.to_mesh();shoulder_bounds[f][suf]=[[min(v.co[k] for v in me.vertices),max(v.co[k] for v in me.vertices)] for k in range(3)];ev.to_mesh_clear()
loop_error=max(abs(p.matrix[i][j]-bone_start[p.name][i][j]) for p in rig.pose.bones for i in range(4) for j in range(4))
notes=bpy.data.texts.get('START HERE | Classroom and character');notes.clear();notes.write('CLASSROOM + MARI SPORTS CHARACTER + TEN-SECOND DANCE\n\nActive scene: Classroom | Golden Hour\nActive rig: MARI | refined character rig\nSelect the armature and enter Pose Mode to adjust the 49-bone FK rig.\n\nACTIVE ANIMATION\n2 Phut Hon inspired | 10 seconds | clasp to dance\nFrames 1-240 at 24 fps. Spacebar plays.\nStarts and ends with both hands softly clasped at the waist; raised-arm hip-sway dance between. Feet stay planted with knee flexion. Hair, bag, head and ears follow the movement. Four blinks.\nSilent animation: no music recording is bundled.\nTimeline markers label the transitions. Previous greeting action retained in the file.\n\nMODEL FIXES\nSlender side hair and reduced back volume; fitted headband; proportionate ears; repaired face blink. Continuous shoulder/sleeve meshes blend chest and arm weights to prevent gaps. Bottle moved upright to teacher desk for free hands.\n\nCAMERAS\nCamera | 10 second dance (active, full body)\nCamera | character portrait\nCamera | classroom overview\nCamera | refined head detail\n\nOriginal character preserved in the disabled reference-inspired collection. Source creator/license recorded in ASSET CREDIT | supplied model.\n')
rig['rig_notes']='49-bone FK rig with baked 10-second dance, planted feet, blended shoulders, individual fingers/toes, head, hair, ears, halo and bag controls.'
s.frame_set(1);s.camera=bpy.data.objects['Camera | 10 second dance'];s.render.resolution_x=720;s.render.resolution_y=960;s.render.fps=24;s.frame_start=1;s.frame_end=240
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Classroom-dance.blend'))
report={'frames':240,'fps':24,'duration':10,'mesh_count':len(meshes),'bones':len(rig.data.bones),'binding_errors':errors,'max_ankle_target_error_m':footmax,'max_bone_tip_step_m':largest_jump,'endpoint_matrix_error':loop_error,'shoulder_bounds':shoulder_bounds}
(root/'dance-validation.json').write_text(json.dumps(report,indent=2));result={k:v for k,v in report.items() if k!='shoulder_bounds'}
