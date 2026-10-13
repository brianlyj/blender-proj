# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy, math
from mathutils import Vector, Matrix
from pathlib import Path
s=bpy.context.scene;rig=bpy.data.objects['CHARACTER_RIG | select to pose'];root=project_path('')
# Make the chalk diagram straight-sided.
for ob in list(s.objects):
    if ob.name.startswith('Geometry triangle') and ob.type=='CURVE':
        sp=ob.data.splines[0]
        for p in sp.bezier_points:p.handle_left_type='VECTOR';p.handle_right_type='VECTOR'
# Remove an overlapping chin shell; the face already has a rounded chin.
ob=bpy.data.objects.get('Chin')
if ob and ob.parent==rig:bpy.data.objects.remove(ob,do_unlink=True)
# Keep socks consistently outside the calf surface and add real toe weights.
for ob in rig.children:
    if ob.type!='MESH':continue
    if ob.name.startswith('Long white sock'):
        suf=ob.name.split('.')[-1];cx=.118 if suf=='L' else -.118
        for v in ob.data.vertices:
            v.co.x=cx+(v.co.x-cx)*1.13;v.co.y*=1.13
    if any(ob.name.startswith(prefix) for prefix in ['Sneaker','Shoe tongue','Criss-cross lace']):
        suffix='L' if any(g.name=='foot.L' for g in ob.vertex_groups) else 'R'
        fg=ob.vertex_groups.get('foot.'+suffix);tg=ob.vertex_groups.new(name='toe.'+suffix)
        if fg:
            for v in ob.data.vertices:
                w=max(0,min(1,(-v.co.y-.085)/.10));fg.add([v.index],1-w,'REPLACE');tg.add([v.index],w,'REPLACE')
# Bottle must be upright when the left hand is lifted.
w=Vector((.49,-.03,1.01));center=w+Vector((.035,-.057,0))
flip=Matrix.Translation(center)@Matrix.Rotation(math.pi,4,'X')@Matrix.Translation(-center)
for ob in rig.children:
    if ob.type=='MESH' and ob.name.startswith(('Water bottle','Bottle neck','Bottle cap','Bottle label','Bottle highlight')):ob.data.transform(flip)
# Rebuild the animation using explicit armature-space directions for the arms.
rig.animation_data_clear()
for pb in rig.pose.bones:pb.rotation_mode='XYZ';pb.rotation_euler=(0,0,0);pb.location=(0,0,0)
arm_names=['upper_arm.R','forearm.R','hand.R','upper_arm.L','forearm.L','hand.L']
for name in arm_names:rig.pose.bones[name].rotation_mode='QUATERNION'
def aim(name,direction):
    pb=rig.pose.bones[name];rest=pb.bone.matrix_local.to_quaternion();rest_direction=pb.bone.tail_local-pb.bone.head_local
    q=rest_direction.rotation_difference(Vector(direction))@rest
    pb.matrix=Matrix.Translation(pb.head)@q.to_matrix().to_4x4()
    bpy.context.view_layer.update()
for f in [1,16,31,46,61,76,91,106,120]:
    s.frame_set(f);t=(f-1)/119*math.tau
    pose={'pelvis':(0,.012*math.sin(t),.012*math.sin(t)), 'spine':(.013*math.sin(t),-.012*math.sin(t),0), 'chest':(.01*math.sin(t),0,.015*math.sin(t)), 'head':(.022*math.sin(t),.045*math.sin(t+.4),-.035), 'hair.L':(.016*math.sin(t-.5),.018*math.sin(t),.012*math.cos(t)), 'hair.R':(.016*math.sin(t+.3),-.018*math.sin(t),-.012*math.cos(t)), 'hair.back':(.018*math.sin(t-.6),.012*math.cos(t),0), 'bag':(.012*math.sin(t-.4),.015*math.sin(t),.013*math.cos(t)), 'ear.L':(.012*math.sin(t*2),0,.02*math.sin(t)), 'ear.R':(.012*math.sin(t*2+.5),0,-.02*math.sin(t))}
    for name,rot in pose.items():
        p=rig.pose.bones[name];p.rotation_euler=rot;p.keyframe_insert(data_path='rotation_euler',frame=f,group=name)
    bpy.context.view_layer.update()
    aim('upper_arm.R',(-.26,-.035,-.1));aim('forearm.R',(-.038+.035*math.sin(t*2),-.03,.22));aim('hand.R',(.016*math.sin(t*2),-.003,.1))
    aim('upper_arm.L',(.19,-.038,-.19));aim('forearm.L',(.032,-.10,.19));aim('hand.L',(-.012,-.007,.10))
    for name in arm_names:rig.pose.bones[name].keyframe_insert(data_path='rotation_quaternion',frame=f,group=name)
    for suf in ['L','R']:
        for finger in ['index','middle','ring','pinky','thumb']:
            for idx in ['01','02']:
                p=rig.pose.bones[finger+'.'+idx+'.'+suf];p.rotation_euler[0]=.25 if suf=='L' else .02;p.keyframe_insert(data_path='rotation_euler',frame=f,group='Fingers')
rig.animation_data.action.name='Greeting | 5 second looping wave'
s.frame_set(16)
# Better portrait composition, slightly closer to straight-on.
cam=bpy.data.objects['Camera | character portrait'];cam.location=(3.0,-3.8,2.8);target=Vector((1.35,3.23,1.38));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=78
for ob in bpy.context.selected_objects:ob.select_set(False)
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.overlay.show_extras=False;a.spaces.active.shading.type='MATERIAL';a.spaces.active.region_3d.view_perspective='CAMERA'
s.camera=bpy.data.objects['Camera | classroom overview']
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Classroom.blend'))
result={'saved':bpy.data.filepath,'hand_positions':{n:list(rig.pose.bones[n].tail) for n in ['hand.R','hand.L']}}
