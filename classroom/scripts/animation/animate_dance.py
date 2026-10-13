# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy,math,json
from mathutils import Vector,Matrix,Euler,Quaternion
from pathlib import Path
ROOT=project_path('revision');s=bpy.context.scene;rig=bpy.data.objects['MARI | refined character rig'];coll=bpy.data.collections['05 Character | refined sports outfit']
if rig.animation_data and rig.animation_data.action:rig.animation_data.action.use_fake_user=True
rig.animation_data_clear()
for p in rig.pose.bones:p.rotation_mode='QUATERNION';p.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()

def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def rot(name,angles):rig.pose.bones[name].rotation_quaternion=Euler(angles,'XYZ').to_quaternion()
def aim(name,head,tail):
 p=rig.pose.bones[name];rest=p.bone.matrix_local.to_quaternion();rd=p.bone.tail_local-p.bone.head_local;q=rd.rotation_difference(tail-head)@rest;p.matrix=Matrix.Translation(head)@q.to_matrix().to_4x4();bpy.context.view_layer.update()
def joint(a,c,pole,L1,L2):
 delta=c-a;d=min(delta.length,L1+L2-.0005);d=max(d,abs(L1-L2)+.0005);axis=delta.normalized();along=(L1*L1-L2*L2+d*d)/(2*d);h=math.sqrt(max(0,L1*L1-along*along));perp=pole-a;perp=(perp-axis*perp.dot(axis)).normalized();return a+axis*along+perp*h,a+axis*d
frames=list(range(1,241));samples={};previous_quaternions={}
for f in frames:
 s.frame_set(f)
 for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
 t=(f-1)/24;env=smooth(.45,1.65,t)*(1-smooth(8.25,9.7,t));phase=math.tau*1.15*(t-1.45);sn=math.sin(phase);cs=math.cos(phase)
 pel=rig.pose.bones['pelvis'];pos=pel.bone.head_local+Vector((.060*sn*env,.005*math.sin(phase*2)*env,-.056-.016*(1+math.cos(phase*2))*env));q=Euler((.025*cs*env,.10*sn*env,.055*sn*env),'XYZ').to_quaternion();pel.matrix=Matrix.Translation(pos)@(q@pel.bone.matrix_local.to_quaternion()).to_matrix().to_4x4()
 rot('spine',(-.015*cs*env,0,.05*sn*env));rot('chest',(.02*cs*env,-.045*sn*env,.045*sn*env));rot('neck',(0,0,.02*sn*env));rot('head',(.017*math.cos(phase+.2)*env,.032*math.sin(phase-.2)*env,.025*sn*env))
 for sign,suf in [(1,'L'),(-1,'R')]:
  rot('hair.'+suf,(.022*math.sin(phase-.65)*env,0,.035*math.sin(phase-.45)*env));rot('ear.'+suf,(.012*cs*env,0,sign*.012*sn*env))
 rot('hair.back',(.020*math.sin(phase-.7)*env,.025*math.sin(phase-.45)*env,0));rot('bag',(.014*math.sin(phase-.6)*env,.026*math.sin(phase-.8)*env,.025*math.sin(phase-.5)*env))
 bpy.context.view_layer.update()
 chest_xf=rig.pose.bones['chest'].matrix@rig.data.bones['chest'].matrix_local.inverted()
 for sign,suf in [(1,'L'),(-1,'R')]:
  # Fixed ankle targets prevent foot sliding while the knees absorb the sway.
  a=rig.pose.bones['thigh.'+suf].head.copy();c=Vector((sign*.155,0,.122));pole=Vector((sign*.18,-.7,.51));b,c=joint(a,c,pole,rig.data.bones['thigh.'+suf].length,rig.data.bones['shin.'+suf].length)
  aim('thigh.'+suf,a,b);aim('shin.'+suf,b,c)
  foot=rig.pose.bones['foot.'+suf];foot.matrix=Matrix.Translation(c)@foot.bone.matrix_local.to_quaternion().to_matrix().to_4x4();bpy.context.view_layer.update()
  # Soft clasp at waist transitions to the recognizable elbows-out, hands-near-head pose.
  clasp=Vector((sign*.079,-.276+(.012 if sign==1 else -.012),1.15));raised=Vector((sign*.285,-.025,1.837));wrist=chest_xf@(clasp.lerp(raised,env))
  a=rig.pose.bones['upper_arm.'+suf].head.copy();pole=chest_xf@Vector((sign*(.46+.18*env),-.07,1.08+.50*env));b,c=joint(a,wrist,pole,rig.data.bones['upper_arm.'+suf].length,rig.data.bones['forearm.'+suf].length)
  aim('upper_arm.'+suf,a,b);aim('forearm.'+suf,b,c)
  direction=Vector((-sign*.82,0,-.57)).lerp(Vector((-sign*.08,-.06,.99)),env).normalized();direction=chest_xf.to_3x3()@direction
  aim('hand.'+suf,c,c+direction*rig.data.bones['hand.'+suf].length)
  for finger in ['index','middle','ring','pinky','thumb']:
   for idx in ['01','02']:rot(finger+'.'+idx+'.'+suf,((.30 if idx=='01' else .38)*(1-env)+.10*env,0,0))
 bpy.context.view_layer.update()
 for p in rig.pose.bones:
  if p.name in previous_quaternions:p.rotation_quaternion.make_compatible(previous_quaternions[p.name])
  previous_quaternions[p.name]=p.rotation_quaternion.copy()
  p.keyframe_insert(data_path='location',frame=f,group=p.name);p.keyframe_insert(data_path='rotation_quaternion',frame=f,group=p.name);p.keyframe_insert(data_path='scale',frame=f,group=p.name)
 if f in [1,61,121,181,239,240]:samples[f]={n:list(rig.pose.bones[n].head) for n in ['hand.L','hand.R','foot.L','foot.R','pelvis']}
action=rig.animation_data.action;action.name='2 Phut Hon inspired | 10 seconds | clasp to dance';action.use_fake_user=True
# Synchronize face, eyes and lashes across the new 240-frame performance.
blink_frames=[51,113,174,220]
for name in ['R2 | Eyes | textured anime','R2 | Face | sculpted anime']:
 o=bpy.data.objects[name];keys=o.data.shape_keys;keys.animation_data_clear();k=keys.key_blocks['Blink']
 for f,val in [(1,0)]+[(f+offset,v) for f in blink_frames for offset,v in [(-3,0),(0,1),(3,0)]]+[(240,0)]:k.value=val;k.keyframe_insert(data_path='value',frame=f)
for o in coll.objects:
 if o.name.startswith('R3 | closed eyelash.'):
  o.animation_data_clear();o.data.shape_keys.animation_data_clear();k=o.data.shape_keys.key_blocks['Blink lash']
  for f,val in [(1,0)]+[(f+offset,v) for f in blink_frames for offset,v in [(-2,0),(0,1),(2,0)]]+[(240,0)]:k.value=val;k.keyframe_insert(data_path='value',frame=f)
  for f,val in [(1,True)]+[(f+offset,v) for f in blink_frames for offset,v in [(-1,False),(1,True)]]+[(240,True)]:o.hide_render=val;o.keyframe_insert(data_path='hide_render',frame=f)
# Seat the retained bottle upright on the actual desk surface.
props=bpy.data.collections.get('06 Dance props')
if props and props.objects:
 obs=list(props.objects);cap=next(o for o in obs if 'Bottle cap' in o.name);body=next(o for o in obs if 'Water bottle' in o.name)
 mean=lambda o:sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
 center=mean(body);q=(mean(cap)-center).rotation_difference(Vector((0,0,1)));M=Matrix.Translation(center)@q.to_matrix().to_4x4()@Matrix.Translation(-center)
 for o in obs:o.data.transform(M)
 lo=Vector([min(v.co[k] for o in obs for v in o.data.vertices) for k in range(3)]);hi=Vector([max(v.co[k] for o in obs for v in o.data.vertices) for k in range(3)]);move=Vector((-.92,3.42,.945))-Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
 for o in obs:o.data.transform(Matrix.Translation(move))
name='Camera | 10 second dance';cam=bpy.data.objects.get(name)
if not cam:d=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,d);s.collection.objects.link(cam)
cam.data.type='ORTHO';cam.data.ortho_scale=2.80;target=rig.location+Vector((0,0,1.20));cam.location=target+Vector((.14,-1.22,.12));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam
s.frame_start=1;s.frame_end=240;s.render.fps=24;s.render.resolution_x=720;s.render.resolution_y=960;s.render.resolution_percentage=100
s.timeline_markers.clear()
for name,frame in [('Hands clasped',1),('Arms rise',24),('Dance groove',49),('Return to relaxed pose',202),('Finish',240)]:s.timeline_markers.new(name,frame=frame)
s.frame_set(1)
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Classroom-dance.blend'))
(ROOT/'dance-pose-samples.json').write_text(json.dumps(samples,indent=2))
result={'action':action.name,'duration_seconds':10,'frames':240,'fps':24,'saved':bpy.data.filepath,'samples':samples}
