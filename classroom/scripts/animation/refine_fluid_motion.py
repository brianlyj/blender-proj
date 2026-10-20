"""Refine the existing emote pack and restore both versions of the dance.

Keeps meshes and user scene edits. The original dance file is only read.
Uses a hierarchy-aware pose solver and keys every frame at 24 fps.
"""
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector, Matrix, Euler

PROJECT=Path(__file__).resolve().parents[2]
scene=bpy.data.scenes['Classroom | Golden Hour'];bpy.context.window.scene=scene
rig=bpy.data.objects['MARI | refined character rig']
manifest=json.loads(scene['mari_emote_manifest'])
source_file=PROJECT/'deliverables/Classroom-dance.blend'
original_file_hash=hashlib.sha256(source_file.read_bytes()).hexdigest()
bones=rig.data.bones
I=Matrix.Identity(4)
FPS=24

def curves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                yield from bag.fcurves

def bone_hash(action):
    result=[]
    for fc in curves(action):
        if fc.data_path.startswith('pose.bones'):
            result.append((fc.data_path,fc.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in fc.keyframe_points]))
    return hashlib.sha256(json.dumps(sorted(result),sort_keys=True).encode()).hexdigest()

# Append the exact action used in the saved, original ten-second dance file.
original_name='2 Phut Hon inspired | 10 seconds | clasp to dance.002'
with bpy.data.libraries.load(str(source_file),link=False) as (src,dst):
    assert original_name in src.actions,'Original dance action is missing'
    dst.actions=[original_name]
original=dst.actions[0]
original.name='DANCE | 2 Phut Hon | ORIGINAL'
original.use_fake_user=True
original_bone_hash=bone_hash(original)
rig.animation_data_create();rig.animation_data.action=original
rig.animation_data.action_slot=original.slots[0]
for frame in range(1,241):
    scene.frame_set(frame)
    blink=max([0]+[max(0,1-abs(frame-center)/3) for center in (51,113,174,220)])
    for prop,value in [('emote_face',0.0),('emote_blink_L',blink),('emote_blink_R',blink)]:
        rig[prop]=value;rig.keyframe_insert(data_path='["%s"]'%prop,frame=frame,group='Facial expression')
assert original_bone_hash==bone_hash(original),'Original dance bone keys changed'

def smooth(a,b,t):
    u=max(0,min(1,(t-a)/(b-a)))
    return u*u*u*(10+u*(-15+6*u))

def pulse(t,center,width):
    return 1-smooth(0,width,abs(t-center))

def joint(a,c,pole,l1,l2):
    delta=c-a;distance=max(abs(l1-l2)+.0002,min(delta.length,l1+l2-.0002))
    axis=delta.normalized();along=(l1*l1-l2*l2+distance*distance)/(2*distance)
    perp=pole-a;perp=(perp-axis*perp.dot(axis)).normalized()
    return a+axis*along+perp*math.sqrt(max(0,l1*l1-along*along)),a+axis*distance

class Pose:
    def __init__(self):
        self.local={};self.world={}
    def rotate(self,name,xyz):
        self.local[name]=Euler(xyz,'XYZ').to_matrix().to_4x4()
    def get(self,name):
        if name not in self.world:
            b=bones[name]
            kwargs={'parent_matrix':self.get(b.parent.name),'parent_matrix_local':b.parent.matrix_local} if b.parent else {}
            self.world[name]=b.convert_local_to_pose(self.local.get(name,I),b.matrix_local,**kwargs)
        return self.world[name]
    def set(self,name,matrix):
        self.world[name]=matrix
    def aim(self,name,head,tail):
        b=bones[name]
        q=(b.tail_local-b.head_local).rotation_difference(tail-head)@b.matrix_local.to_quaternion()
        self.set(name,Matrix.Translation(head)@q.to_matrix().to_4x4())
    def apply(self):
        for pb in rig.pose.bones:
            b=pb.bone
            kwargs={'parent_matrix':self.get(b.parent.name),'parent_matrix_local':b.parent.matrix_local} if b.parent else {}
            pb.matrix_basis=b.convert_local_to_pose(self.get(pb.name),b.matrix_local,invert=True,**kwargs)

def make_pose(kind,t,duration):
    p=Pose();env=smooth(0,.65,t)*(1-smooth(duration-.8,duration,t))
    if kind=='dance':env=smooth(.35,1.6,t)*(1-smooth(8.25,9.85,t))
    phase=math.tau*(1.15*(t-1.45) if kind=='dance' else 1.05*t)
    beat=math.sin(phase);slow=math.sin(math.tau*t/3)
    breath=.0025*math.sin(math.tau*2*t/duration)
    bounce_kind=kind in ('bounce','paws','point')
    crouch=.026*max(0,-math.sin(phase-.4))**2*env if bounce_kind else .007*(1-math.cos(phase))*env
    lift=.060*max(0,math.sin(phase-.4))**3*env if kind=='bounce' else 0
    turn=0
    if kind=='twirl':
        turn=-.24*pulse(t,.62,.60)+math.tau*smooth(.85,3.45,t)
        turn+=.055*math.sin(8*(t-3.45))*math.exp(-3*max(0,t-3.45))*smooth(3.45,3.65,t)*(1-smooth(4.5,5.1,t))
    pivot=Vector((-.145,-.085,0)) if kind=='twirl' else Vector((0,0,0))
    root_xf=Matrix.Translation((0,0,lift))@Matrix.Translation(pivot)@Matrix.Rotation(turn,4,'Z')@Matrix.Translation(-pivot)
    p.set('root',root_xf@bones['root'].matrix_local)
    sway_amp=.075 if kind=='dance' else (.052 if kind in ('sass','paws','point') else .034)
    dx=sway_amp*math.sin(phase if kind=='dance' else phase*.5-.2)*env
    if kind=='twirl':dx=-.045*env
    if kind=='gloom':dx=.012*slow*env
    anticipation=-.018*pulse(t,.27,.24)
    dy=(.009*math.sin(phase-.55)*env if kind!='gloom' else -.012*env)
    pelvis_roll=(.12*math.sin(phase) if kind=='dance' else .075*math.sin(phase*.5-.15))*env
    pelvis_pitch=(.025*math.sin(phase-.35)*env)
    pelvis_yaw=(.055*math.sin(phase*.5)*env)
    hip_position=bones['pelvis'].head_local+Vector((dx,dy,-.062-crouch+breath+anticipation))
    p.set('pelvis',root_xf@Matrix.Translation(hip_position)@Euler((pelvis_pitch,pelvis_roll,pelvis_yaw),'XYZ').to_matrix().to_4x4()@bones['pelvis'].matrix_local.to_quaternion().to_matrix().to_4x4())
    bow=.43*env if kind=='gloom' else (.08*env if kind=='shy' else 0)
    p.rotate('spine',(bow+.018*math.sin(phase-.3)*env,0,-.045*math.sin(phase*.5-.45)*env))
    p.rotate('chest',(.025*math.sin(phase-.55)*env,-.035*math.sin(phase-.65)*env,-.065*math.sin(phase*.5-.6)*env))
    p.rotate('neck',(.055*env if kind=='shy' else 0,0,.025*math.sin(phase*.5-.7)*env))
    nod=.025*math.sin(phase-.65)*env
    if kind=='gloom':nod+=.27*env+.035*math.sin(phase*.5)*env
    if kind=='cool':nod-=.06*env
    p.rotate('head',(nod,.045*math.sin(phase*.5-.8)*env,(-.11 if kind in ('wink','cool') else .065*math.sin(phase*.5-.9))*env))
    for sign,side in [(1,'L'),(-1,'R')]:
        p.rotate('shoulder.'+side,(.015*math.sin(phase+sign*.4)*env,.025*math.sin(phase-.3+sign*.45)*env,0))
        p.rotate('hair.'+side,(.045*math.sin(phase-.95+sign*.18)*env,.025*math.sin(phase*.5-1)*env,.075*math.sin(phase*.5-.95)*env))
        p.rotate('ear.'+side,((-.18 if kind=='gloom' else .04*math.sin(phase-.8+sign*.3))*env,0,sign*.035*math.sin(phase-.5)*env))
    p.rotate('hair.back',(.055*math.sin(phase-1.15)*env,.055*math.sin(phase*.5-1.05)*env,.02*math.sin(phase*.5)*env))
    p.rotate('bag',(.055*math.sin(phase-1.2)*env,.09*math.sin(phase*.5-1.15)*env,.04*math.sin(phase*.5-.9)*env))
    chest_xf=p.get('chest')@bones['chest'].matrix_local.inverted()
    feet={}
    for sign,side in [(1,'L'),(-1,'R')]:
        ankle=Vector((sign*.155,0,.122))
        heel=0
        if kind=='dance':heel=.011*max(0,sign*beat)**2*env
        elif kind=='twirl':
            ankle.x=sign*.145
            ankle.z+=.105*env if sign==1 else .014*env
            ankle.y+=.055*env if sign==1 else 0
            heel=.10*env if sign==1 else .014*env
        ankle.z+=heel if kind!='twirl' else 0
        target=root_xf@ankle
        a=p.get('thigh.'+side).translation.copy()
        knee,c=joint(a,target,root_xf@Vector((sign*.20,-.7,.5)),bones['thigh.'+side].length,bones['shin.'+side].length)
        p.aim('thigh.'+side,a,knee);p.aim('shin.'+side,knee,c)
        pitch=(heel/.12) if kind!='twirl' else (.12*env if sign==-1 else -.15*env)
        p.set('foot.'+side,Matrix.Translation(c)@root_xf.to_quaternion().to_matrix().to_4x4()@Matrix.Rotation(pitch,4,'X')@bones['foot.'+side].matrix_local.to_quaternion().to_matrix().to_4x4())
        feet[side]=(target,c)
        idle=Vector((sign*.079,-.276+sign*.012,1.15))
        idle.z+=breath
        wrist=idle.copy();direction=Vector((-sign*.82,0,-.57));pole=Vector((sign*.48,-.06,1.13));curl=.30
        local_phase=phase-(.32 if sign==1 else .73)
        gesture=.055*math.sin(local_phase)
        if kind in ('sass','wink'):
            wrist=Vector((-sign*.075,-.315-sign*.025,1.285+sign*.045))
            wrist.z+=.011*math.sin(local_phase*.5)
            direction=Vector((-sign*.9,-.05,.30));pole=Vector((sign*.47,-.08,1.11))
        elif kind=='bounce':
            wrist=Vector((sign*(.27+.025*math.sin(local_phase)),-.25+.028*math.cos(local_phase),1.45+gesture))
            direction=Vector((sign*.12, -.18*math.cos(local_phase-.3),1));pole=Vector((sign*.55,-.07,1.20));curl=1.03
        elif kind=='twirl':
            high=.13 if sign==1 else -.06
            wrist=Vector((sign*(.32+.035*math.sin(local_phase*.5)),-.15+.04*math.sin(local_phase),1.49+high+.045*math.sin(local_phase*.5)))
            direction=Vector((sign*.18,-.08,1));pole=Vector((sign*.6,-.03,1.34));curl=.65
        elif kind=='cool':
            wrist=Vector((sign*.19,-.24,1.65+.014*math.sin(local_phase*.5))) if sign==-1 else Vector((.25,-.15,1.12))
            direction=Vector((0,-.18,1)) if sign==-1 else Vector((-.5,0,-1));curl=.82
        elif kind=='paws':
            wrist=Vector((sign*(.235+.032*math.sin(local_phase)),-.30+.03*math.cos(local_phase),1.47+sign*.065*math.sin(phase-.4)))
            direction=Vector((sign*.1,-.22-.22*math.sin(local_phase-.3),1));pole=Vector((sign*.53,-.07,1.22));curl=.67+.15*math.sin(local_phase-.2)
        elif kind=='shy':
            wrist=Vector((sign*.055,-.27,1.39+.014*math.sin(local_phase*.5)))
            direction=Vector((-sign*.48,-.06,.85));pole=Vector((sign*.43,-.04,1.13));curl=.33
        elif kind=='point':
            wrist=Vector((sign*(.23+.035*math.sin(local_phase)),-.33-.055*math.sin(local_phase),1.43+sign*.035*math.sin(phase-.2)))
            direction=Vector((sign*.10,-.88,.48+.10*math.sin(local_phase-.2)));pole=Vector((sign*.5,-.05,1.17));curl=1
        elif kind=='gloom':
            wrist=Vector((sign*.32,-.10+.012*math.sin(local_phase*.5),1.035))
            direction=Vector((0,-.15,-1));pole=Vector((sign*.45,.02,1.12));curl=.35
        elif kind=='dance':
            wrist=Vector((sign*(.285+.016*math.sin(local_phase)),-.025-.016*math.cos(local_phase),1.837+.020*math.sin(local_phase-.2)))
            direction=Vector((-sign*.08,-.08+.10*math.cos(local_phase),.99));pole=Vector((sign*.65,-.06,1.60+.025*math.sin(local_phase)));curl=.12
        arm_env=smooth(.06 if sign==1 else .13,.70 if sign==1 else .79,t)*(1-smooth(duration-.85,duration-.04,t))
        if kind=='dance':arm_env=env
        if kind=='idle':arm_env=0
        wrist=chest_xf@idle.lerp(wrist,arm_env)
        a=p.get('upper_arm.'+side).translation.copy()
        elbow_pole=Vector((sign*.48,-.06,1.13)).lerp(pole,arm_env)
        elbow,c=joint(a,wrist,chest_xf@elbow_pole,bones['upper_arm.'+side].length,bones['forearm.'+side].length)
        p.aim('upper_arm.'+side,a,elbow);p.aim('forearm.'+side,elbow,c)
        hand_dir=Vector((-sign*.82,0,-.57)).lerp(direction,arm_env).normalized()
        p.aim('hand.'+side,c,c+chest_xf.to_3x3()@hand_dir*bones['hand.'+side].length)
        for finger in ('index','middle','ring','pinky','thumb'):
            for segment in ('01','02'):
                flex=.3*(1-arm_env)+curl*arm_env
                if kind=='point' and finger in ('index','thumb'):flex=.3*(1-arm_env)+.04*arm_env
                if kind=='cool' and side=='R' and finger=='index':flex=.3*(1-arm_env)+.04*arm_env
                if finger=='thumb':flex*=.65
                p.rotate(finger+'.'+segment+'.'+side,(flex,0,0))
    p.apply()
    return env,max((a-b).length for a,b in feet.values())

old_entries=manifest['entries']
labels={e['number']:e['label'] for e in old_entries}
kinds={0:'idle',1:'sass',2:'bounce',3:'twirl',4:'cool',5:'wink',6:'paws',7:'shy',8:'point',9:'gloom',10:'dance'}
faces={0:0,1:1,2:2,3:2,4:3,5:4,6:2,7:5,8:2,9:6,10:0}
report={'original_file_sha256':original_file_hash,'original_dance_bone_key_sha256':original_bone_hash,'animations':[]}
entries=[]
for number in range(11):
    duration=10 if number==10 else 6
    end=duration*FPS
    label='2 Phut Hon - fluid' if number==10 else labels[number]
    if rig.animation_data and rig.animation_data.action:rig.animation_data.action.use_fake_user=True
    rig.animation_data_clear();previous={};max_foot_error=0
    for pb in rig.pose.bones:pb.rotation_mode='QUATERNION'
    start_pose=None
    for frame in range(1,end+1):
        if frame in (1,end):scene.frame_set(frame)
        t=(frame-1)/(end-1)*duration
        env,error=make_pose(kinds[number],t,duration)
        max_foot_error=max(max_foot_error,error)
        face=faces[number] if env>.85 else 0
        blink=max(pulse(t,2.55,.13),pulse(t,4.75,.13))
        if number==10:blink=max(pulse(t,x,.13) for x in (2.1,4.7,7.25,9.1))
        left=right=blink
        if faces[number]==1:left=right=max(blink,.44*env)
        elif faces[number] in (2,5,6):left=right=max(blink,env)
        elif faces[number]==4:left,right=max(blink,env),blink*(1-env)
        for prop,value in [('emote_face',float(face)),('emote_blink_L',left),('emote_blink_R',right)]:
            rig[prop]=value;rig.keyframe_insert(data_path='["%s"]'%prop,frame=frame,group='Facial expression')
        for pb in rig.pose.bones:
            if pb.name in previous:pb.rotation_quaternion.make_compatible(previous[pb.name])
            previous[pb.name]=pb.rotation_quaternion.copy()
            for prop in ('location','rotation_quaternion','scale'):
                pb.keyframe_insert(data_path=prop,frame=frame,group=pb.name)
        if frame in (1,end):
            bpy.context.view_layer.update()
            matrices={pb.name:pb.matrix.copy() for pb in rig.pose.bones}
            if frame==1:start_pose=matrices
            else:loop=max(abs(matrices[n][i][j]-start_pose[n][i][j]) for n in matrices for i in range(4) for j in range(4))
    assert loop<.001,(number,loop)
    action=rig.animation_data.action
    action.name=('DANCE | '+label) if number==10 else ('EMOTE %d | '%number)+label+' | fluid'
    action.use_fake_user=True
    action['fluid_revision']=1
    for fc in curves(action):
        for key in fc.keyframe_points:
            key.interpolation='CONSTANT' if fc.data_path=='["emote_face"]' else 'BEZIER'
            key.handle_left_type=key.handle_right_type='AUTO_CLAMPED'
    entries.append({'number':number,'label':label,'shortcut':'+' if number==10 else str(number),'action':action.name,'slot':rig.animation_data.action_slot.identifier,'start':1,'end':end,'fps':FPS,'preview_frame':57 if number!=3 else 24})
    report['animations'].append({'number':number,'label':label,'frames':end,'loop_error':loop,'max_foot_target_error':max_foot_error})
    print('FLUID_ACTION_READY',number,label,'loop',loop,'feet',max_foot_error,flush=True)

entries.append({'number':11,'label':'2 Phut Hon - original','shortcut':'-','action':original.name,'slot':original.slots[0].identifier,'start':1,'end':240,'fps':24,'preview_frame':69})
manifest['entries']=entries
manifest['motion_revision']='Fluid motion and restored dance access'
scene['mari_emote_manifest']=json.dumps(manifest)
scene['mari_emote_current']=10;scene['mari_emote_previous']=10
scene['mari_emote_keys_enabled']=True
rig.animation_data.action=bpy.data.actions[entries[10]['action']]
rig.animation_data.action_slot=rig.animation_data.action.slots[0]
scene.frame_start=1;scene.frame_end=240;scene.render.fps=24;scene.sync_mode='FRAME_DROP';scene.frame_set(1)
scene.timeline_markers.clear()
for label,frame in [('Settle and raise arms',1),('Dance groove',40),('Ease to rest',202)]:scene.timeline_markers.new(label,frame=frame)
guide='MARI ANIMATIONS\n\nNumpad +: refined 10-second 2 Phut Hon dance\nNumpad -: original 10-second 2 Phut Hon dance\nNumpad 1-9: emotes\nNumpad 0 / same key: return to idle\nNumpad Enter: pause / resume\nNumpad .: enable / disable emote shortcuts\n\nHover over the 3D viewport; Num Lock on.\nSwitching animations eases from the current pose over 0.3 seconds.\nEmotes use staggered gestures, anticipation, counter-motion, planted support\nfeet, and delayed hair/ear/bag follow-through.\nThe original dance bone keys are preserved exactly in the original action.\nThe original Classroom-dance.blend is unchanged.\n'
for name in ('EMOTES | Numpad controls','START HERE | Classroom and character'):
    block=bpy.data.texts.get(name) or bpy.data.texts.new(name);block.clear();block.write(guide)
controller=bpy.data.texts.get('mari_emote_controls.py') or bpy.data.texts.new('mari_emote_controls.py')
controller.clear();controller.write((PROJECT/'scripts/animation/mari_emote_controls.py').read_text(encoding='utf-8'))
assert hashlib.sha256(source_file.read_bytes()).hexdigest()==original_file_hash
assert bone_hash(original)==original_bone_hash
report['original_dance_preserved']=True
(PROJECT/'reports/final/fluid-motion-build.json').write_text(json.dumps(report,indent=2))
(PROJECT/'reports/final/emote-manifest.json').write_text(json.dumps(manifest,indent=2))
previous_versions=bpy.context.preferences.filepaths.save_version
try:
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(PROJECT/'deliverables/Classroom-emotes.blend'),compress=True)
finally:
    bpy.context.preferences.filepaths.save_version=previous_versions
print('FLUID_PACK_SAVED',flush=True)
