"""Build nine reel-inspired emotes on the existing sports character.

Run with Blender --background Classroom-dance.blend --python this_file.py.
The dance source stays intact; output is Classroom-emotes.blend.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector, Matrix, Euler

PROJECT = Path(__file__).resolve().parents[2]
scene = bpy.data.scenes['Classroom | Golden Hour']
bpy.context.window.scene = scene
rig = bpy.data.objects['MARI | refined character rig']
character = bpy.data.collections['05 Character | refined sports outfit']
OUT = PROJECT / 'deliverables/Classroom-emotes.blend'
FPS, END = 24, 96
EMOTES = [
    (0, 'Relaxed idle', 'idle', 0),
    (1, 'Crossed-arm sass', 'sass', 1),
    (2, 'Happy bounce', 'bounce', 2),
    (3, 'Cheerful twirl', 'twirl', 2),
    (4, 'Deal with it', 'cool', 3),
    (5, 'Cheeky wink', 'wink', 4),
    (6, 'Paw dance', 'paws', 2),
    (7, 'Shy hand clasp', 'shy', 5),
    (8, 'Double point', 'point', 2),
    (9, 'Dejected bow', 'gloom', 6),
]

def preserve_animation(data):
    if data.animation_data and data.animation_data.action:
        data.animation_data.action.use_fake_user = True
    data.animation_data_clear()

preserve_animation(rig)
for pb in rig.pose.bones:
    pb.rotation_mode = 'QUATERNION'
    pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
effects = bpy.data.collections.new('07 Emotes | facial expressions and effects')
scene.collection.children.link(effects)

for prop, value in {'emote_face':0.0, 'emote_blink_L':0.0, 'emote_blink_R':0.0}.items():
    rig[prop] = value

def driver(target, prop, expression, variable='v', source='emote_face'):
    curve = target.driver_add(prop)
    d = curve.driver
    d.type = 'SCRIPTED'
    d.expression = expression
    v = d.variables.new()
    v.name = variable
    v.type = 'SINGLE_PROP'
    v.targets[0].id = rig
    v.targets[0].data_path = '["%s"]' % source

def visible_when(obj, predicate):
    for prop in ('hide_render', 'hide_viewport'):
        driver(obj, prop, 'not (' + predicate + ')')

def emission(name, color):
    m = bpy.data.materials.new('Emote | ' + name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    n = m.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    shader = n.new('ShaderNodeEmission')
    shader.inputs['Color'].default_value = (*color, 1)
    m.node_tree.links.new(shader.outputs[0], out.inputs['Surface'])
    return m

ink = emission('warm ink', (.010,.005,.004))
mouth_mat = emission('mouth interior', (.31,.045,.075))
tongue = emission('pink tongue', (.96,.34,.43))
ivory = emission('ivory teeth and glints', (1,.96,.87))
black = emission('pixel sunglasses', (.012,.016,.023))
blush = emission('soft blush', (.95,.46,.43))
gold = emission('wink sparkle', (1,.78,.14))
purple = emission('gloom purple', (.25,.13,.59))

def mesh(name, vertices, faces, mat, predicate=None):
    data = bpy.data.meshes.new('Emote | ' + name)
    data.from_pydata(vertices, [], faces)
    data.update()
    ob = bpy.data.objects.new('Emote | ' + name, data)
    effects.objects.link(ob)
    data.materials.append(mat)
    ob.parent = rig
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.matrix_basis = Matrix.Identity(4)
    ob.vertex_groups.new(name='head').add(list(range(len(vertices))),1,'REPLACE')
    ob.modifiers.new('Follow head', 'ARMATURE').object = rig
    if predicate:
        visible_when(ob, predicate)
    return ob

def face_y(x, offset=0):
    return -.193 + .18*abs(x) + offset

def patch(name, outline, mat, predicate, depth=0):
    verts = [(x,face_y(x,depth),z) for x,z in outline]
    return mesh(name, verts, [tuple(range(len(verts)))],mat,predicate)

def tube(name, points, radius, mat, predicate, sides=8):
    vertices, faces = [], []
    for i, point in enumerate(points):
        point = Vector(point)
        tangent = Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])
        q = tangent.to_track_quat('Z','Y')
        for j in range(sides):
            vertices.append(point + q@Vector((radius*math.cos(math.tau*j/sides),radius*math.sin(math.tau*j/sides),0)))
    for i in range(len(points)-1):
        for j in range(sides):
            faces.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
    faces += [tuple(reversed(range(sides))),tuple((len(points)-1)*sides+j for j in range(sides))]
    ob = mesh(name,vertices,faces,mat,predicate)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob

def stroke(name, xz, radius, mat, predicate, depth=-.002):
    return tube(name,[(x,face_y(x,depth),z) for x,z in xz],radius,mat,predicate)

# Split the existing eyelid deformation so a wink closes only one eye.
for name in ['R2 | Face | sculpted anime', 'R2 | Eyes | textured anime']:
    ob = bpy.data.objects[name]
    keys = ob.data.shape_keys
    preserve_animation(keys)
    base, closed = keys.key_blocks['Basis'], keys.key_blocks['Blink']
    closed.value = 0
    for side,sign in [('L',1),('R',-1)]:
        key = ob.shape_key_add(name='Emote blink.'+side)
        for a,b,c in zip(base.data,closed.data,key.data):
            c.co = b.co if a.co.x*sign>0 else a.co
        driver(key,'value','v',source='emote_blink_'+side)

for ob in character.objects:
    if ob.name.startswith('R3 | closed eyelash.'):
        preserve_animation(ob)
        preserve_animation(ob.data.shape_keys)
        side = 'L' if '.L' in ob.name else 'R'
        driver(ob.data.shape_keys.key_blocks['Blink lash'],'value','v',source='emote_blink_'+side)
        visible_when(ob, 'v < 1.5 or v > 5.5')

for sign,side in [(1,'L'),(-1,'R')]:
    chevron=[(sign*.169,1.727),(sign*.075,1.693),(sign*.170,1.669)]
    predicate='v==2 or v==5' + (' or v==4' if side=='L' else '')
    stroke('squeeze eye '+side,chevron,.0075,ink,predicate,-.022)
    for j in range(3):
        x=sign*(.14+j*.012)
        stroke('blush '+side+str(j),[(x,1.646),(x-sign*.006,1.632)],.0027,blush,'v==2 or v==4 or v==5',-.004)

# Layer the drawn mouths in front of the original chin/soft-smile mesh.
outline=[(-.043,1.607),(-.022,1.599),(0,1.604),(.022,1.599),(.043,1.607),(.035,1.574),(.020,1.552),(0,1.546),(-.020,1.552),(-.035,1.574)]
patch('open happy mouth',outline,mouth_mat,'v==2 or v==5',-.007)
stroke('happy mouth outline',outline+[outline[0]],.002,ink,'v==2 or v==5',-.010)
patch('happy tongue',[(-.026,1.565),(-.012,1.572),(.012,1.572),(.026,1.565),(.017,1.555),(0,1.551),(-.017,1.555)],tongue,'v==2 or v==5',-.012)
grin=[(-.045,1.600),(-.023,1.589),(0,1.590),(.038,1.609),(.029,1.578),(.008,1.565),(-.019,1.570)]
patch('wink grin',grin,ivory,'v==4',-.008)
stroke('wink grin outline',grin+[grin[0]],.0027,ink,'v==4',-.011)

# Pixel glasses are geometry so they remain visible in viewport and renders.
for sign,side in [(1,'L'),(-1,'R')]:
    outline=[(sign*x,z) for x,z in [(.024,1.736),(.200,1.736),(.200,1.715),(.181,1.715),(.181,1.681),(.153,1.664),(.061,1.664),(.041,1.682),(.041,1.716),(.024,1.716)]]
    patch('pixel lens '+side,outline,black,'v==3',-.026)
    for j in range(3):
        x=sign*(.07+.022*j);z=1.714-.012*j
        patch('pixel glint '+side+str(j),[(x,z),(x+sign*.014,z),(x+sign*.014,z-.010),(x,z-.010)],ivory,'v==3',-.028)
stroke('glasses bridge',[(-.035,1.724),(0,1.728),(.035,1.724)],.005,black,'v==3',-.027)
for sign in [-1,1]:
    for j in range(2):
        x=sign*(.205+j*.026)
        tube('gloom bar %s %s'%(sign,j),[(x,-.10,2.02),(x,-.10,2.12+.028*j)],.006,purple,'v==6')
star=[]
for i in range(10):
    angle=math.pi/2+math.tau*i/10;radius=.027 if i%2==0 else .011
    star.append((-.111+math.cos(angle)*radius,1.696+math.sin(angle)*radius))
patch('wink eye star',star,gold,'v==4',-.012)

def smooth(a,b,x):
    t=max(0,min(1,(x-a)/(b-a)))
    return t*t*(3-2*t)

def rot(name,angles):
    rig.pose.bones[name].rotation_quaternion=Euler(angles,'XYZ').to_quaternion()

def aim(name,head,tail):
    p=rig.pose.bones[name]
    rd=p.bone.tail_local-p.bone.head_local
    q=rd.rotation_difference(tail-head)@p.bone.matrix_local.to_quaternion()
    p.matrix=Matrix.Translation(head)@q.to_matrix().to_4x4()
    bpy.context.view_layer.update()

def joint(a,c,pole,l1,l2):
    dlt=c-a;d=min(dlt.length,l1+l2-.001);d=max(d,abs(l1-l2)+.001)
    axis=dlt.normalized();along=(l1*l1-l2*l2+d*d)/(2*d)
    perp=pole-a;perp=(perp-axis*perp.dot(axis)).normalized()
    return a+axis*along+perp*math.sqrt(max(0,l1*l1-along*along)),a+axis*d

def target_pose(kind,t,env):
    phase=math.tau*t
    sn,cs=math.sin(phase),math.cos(phase)
    sway=math.sin(phase*.5)
    turn=math.tau*smooth(.8,2.85,t) if kind=='twirl' else 0
    lift=.055*max(0,sn)**2*env if kind in ('bounce','twirl') else 0
    root=rig.pose.bones['root']
    root.matrix=Matrix.Translation((0,0,lift))@Matrix.Rotation(turn,4,'Z')@root.bone.matrix_local
    bpy.context.view_layer.update()
    root_xf=root.matrix@root.bone.matrix_local.inverted()
    dx=env*(.028*sway if kind!='gloom' else .008*sway)
    down=.017*(1+cs)*env if kind in ('bounce','paws','twirl') else .006*cs*env
    pel=rig.pose.bones['pelvis']
    pel.matrix=root_xf@Matrix.Translation(pel.bone.head_local+Vector((dx,0,-.062-down)))@Euler((0,.035*sway*env,0),'XYZ').to_matrix().to_4x4()@pel.bone.matrix_local.to_quaternion().to_matrix().to_4x4()
    bend=.48*env if kind=='gloom' else (.08*env if kind=='shy' else 0)
    rot('spine',(bend,0,.025*sway*env))
    rot('chest',(.035*cs*env,-.025*sway*env,.035*sway*env))
    rot('neck',(.06*env if kind=='shy' else 0,0,0))
    rot('head',((.30 if kind=='gloom' else -.05)*env,.045*sway*env,(-.10 if kind in ('cool','wink') else .06*sway)*env))
    for sign,side in [(1,'L'),(-1,'R')]:
        rot('hair.'+side,(.025*math.sin(phase-.5)*env,0,.055*math.sin(phase-.7)*env))
        rot('ear.'+side,((-.14 if kind=='gloom' else .025*cs)*env,0,sign*.025*sn*env))
    rot('hair.back',(.04*math.sin(phase-.7)*env,.025*sn*env,0))
    rot('bag',(.03*math.sin(phase-.8)*env,.07*sway*env,.025*cs*env))
    bpy.context.view_layer.update()
    chest_xf=rig.pose.bones['chest'].matrix@rig.data.bones['chest'].matrix_local.inverted()
    for sign,side in [(1,'L'),(-1,'R')]:
        a=rig.pose.bones['thigh.'+side].head.copy()
        foot_co=Vector((sign*.155,0,.122))
        if kind=='twirl':foot_co.z+=.018*max(0,sign*sn)*env
        foot_target=root_xf@foot_co
        b,c=joint(a,foot_target,root_xf@Vector((sign*.19,-.65,.5)),rig.data.bones['thigh.'+side].length,rig.data.bones['shin.'+side].length)
        aim('thigh.'+side,a,b);aim('shin.'+side,b,c)
        foot=rig.pose.bones['foot.'+side]
        foot.matrix=Matrix.Translation(c)@root_xf.to_quaternion().to_matrix().to_4x4()@foot.bone.matrix_local.to_quaternion().to_matrix().to_4x4()
        bpy.context.view_layer.update()
        idle=Vector((sign*.079,-.276+sign*.012,1.15))
        wrist=idle.copy();direction=Vector((-sign*.82,0,-.57));pole=Vector((sign*.47,-.08,1.12));curl=.3
        if kind in ('sass','wink'):
            wrist=Vector((-sign*.075,-.295-sign*.025,1.285+sign*.045))
            direction=Vector((-sign*.9,0,.35));pole=Vector((sign*.46,-.08,1.11));curl=.30
        elif kind=='bounce':
            wrist=Vector((sign*.27,-.22,1.43+.045*cs));direction=Vector((sign*.05,-.1,1));pole=Vector((sign*.54,-.05,1.19));curl=1.05
        elif kind=='twirl':
            wrist=Vector((sign*.31,-.12,1.49+sign*.10*sway));direction=Vector((sign*.15,0,1));pole=Vector((sign*.60,0,1.30));curl=.85
        elif kind=='cool':
            wrist=Vector((sign*.19,-.22,1.64)) if sign==-1 else Vector((.25,-.12,1.12))
            direction=Vector((0,-.2,1)) if sign==-1 else Vector((-.5,0,-1));curl=.8
        elif kind=='paws':
            wrist=Vector((sign*.23,-.29,1.47+sign*.05*sn));direction=Vector((sign*.15,-.1,.95));pole=Vector((sign*.53,-.04,1.20));curl=.7
        elif kind=='shy':
            wrist=Vector((sign*.055,-.25,1.39+.015*cs));direction=Vector((-sign*.48,-.06,.85));pole=Vector((sign*.44,-.01,1.11));curl=.3
        elif kind=='point':
            wrist=Vector((sign*.23,-.33,1.41+sign*.03*sn));direction=Vector((sign*.07,-.88,.45));pole=Vector((sign*.5,-.03,1.13));curl=1.0
        elif kind=='gloom':
            wrist=Vector((sign*.32,-.04,1.03));direction=Vector((0,0,-1));pole=Vector((sign*.46,.03,1.12));curl=.4
        wrist=chest_xf@idle.lerp(wrist,env)
        a=rig.pose.bones['upper_arm.'+side].head.copy()
        b,c=joint(a,wrist,chest_xf@pole,rig.data.bones['upper_arm.'+side].length,rig.data.bones['forearm.'+side].length)
        aim('upper_arm.'+side,a,b);aim('forearm.'+side,b,c)
        direction=Vector((-sign*.82,0,-.57)).lerp(direction,env).normalized()
        aim('hand.'+side,c,c+chest_xf.to_3x3()@direction*rig.data.bones['hand.'+side].length)
        for finger in ('index','middle','ring','pinky','thumb'):
            for segment in ('01','02'):
                flex=.3*(1-env)+curl*env
                if kind=='point' and finger in ('index','thumb'):flex=.05
                if kind=='cool' and side=='R' and finger=='index':flex=.04
                if finger=='thumb':flex*=.65
                rot(finger+'.'+segment+'.'+side,(flex,0,0))
    bpy.context.view_layer.update()

manifest={'version':1,'rig':rig.name,'source':'https://www.facebook.com/reel/952944630756734/','entries':[]}
report={'emotes':[],'binding_errors':[]}
for number,label,kind,face in EMOTES:
    preserve_animation(rig)
    previous={}
    samples={}
    for f in list(range(1,END+1,3))+[END]:
        scene.frame_set(f)
        for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
        t=(f-1)/(END-1)*4
        env=smooth(0,.45,t)*(1-smooth(3.45,4,t)) if number else 0
        target_pose(kind,t,env)
        visible_face=face if env>.15 else 0
        rig['emote_face']=float(visible_face)
        blink=max(0,1-abs(t-2.65)/.13)
        left=right=blink
        if visible_face==1:left=right=.46
        elif visible_face in (2,5):left=right=1
        elif visible_face==4:left,right=1,0
        elif visible_face==6:left=right=1
        rig['emote_blink_L']=left;rig['emote_blink_R']=right
        for prop in ('emote_face','emote_blink_L','emote_blink_R'):
            rig.keyframe_insert(data_path='["%s"]'%prop,frame=f,group='Facial expression')
        for p in rig.pose.bones:
            if p.name in previous:p.rotation_quaternion.make_compatible(previous[p.name])
            previous[p.name]=p.rotation_quaternion.copy()
            for prop in ('location','rotation_quaternion','scale'):
                p.keyframe_insert(data_path=prop,frame=f,group=p.name)
        if f in (1,49,END):samples[f]={p.name:[list(row) for row in p.matrix] for p in rig.pose.bones}
    action=rig.animation_data.action
    action.name='EMOTE %d | %s'%(number,label)
    action.use_fake_user=True
    action['mari_emote_number']=number
    action['description']=label
    slot=rig.animation_data.action_slot
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for key in fc.keyframe_points:
                        key.interpolation='CONSTANT' if fc.data_path=='["emote_face"]' else 'LINEAR'
    manifest['entries'].append({'number':number,'label':label,'action':action.name,'slot':slot.identifier,'start':1,'end':END,'fps':FPS,'preview_frame':43 if kind!='twirl' else 19})
    delta=max(abs(samples[1][name][i][j]-samples[END][name][i][j]) for name in samples[1] for i in range(4) for j in range(4))
    report['emotes'].append({'number':number,'name':label,'action':action.name,'endpoint_matrix_error':delta,'keyed_bones':len(rig.pose.bones)})
    print('EMOTE_CREATED',number,label,'loop_error',delta,flush=True)

scene['mari_emote_manifest']=json.dumps(manifest)
scene['mari_emote_keys_enabled']=True
scene['mari_emote_current']=0
scene['mari_emote_previous']=1
scene.frame_start=1;scene.frame_end=END;scene.render.fps=FPS
idle=bpy.data.actions[manifest['entries'][0]['action']]
rig.animation_data.action=idle
rig.animation_data.action_slot=next(sl for sl in idle.slots if sl.identifier==manifest['entries'][0]['slot'])
scene.frame_set(1)
scene.camera=bpy.data.objects['Camera | 10 second dance']
scene.camera.data.ortho_scale=2.95
scene.render.resolution_x=720;scene.render.resolution_y=960
scene.render.filepath='//../renders/emotes/'
scene.timeline_markers.clear()
scene.timeline_markers.new('Emote entrance',frame=1)
scene.timeline_markers.new('Emote loop',frame=13)
scene.timeline_markers.new('Return to idle',frame=84)
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA'
        area.spaces.active.shading.type='MATERIAL'
        area.spaces.active.overlay.show_overlays=False
        area.spaces.active.show_region_ui=True
guide=bpy.data.texts.new('EMOTES | Numpad controls')
guide.write('MARI EMOTE PLAYER\n\nHover over the 3D viewport. Numpad 1-9 selects an emote.\nPress the same key again or Numpad 0 to return to idle.\nNumpad Enter pauses/resumes. Numpad . toggles emote shortcuts.\nThe N sidebar > Emotes panel also has buttons.\n\n'+''.join('%d: %s\n'%(n,label) for n,label,_,_ in EMOTES)+'\nShortcuts are active only in this emote project while Emote shortcuts is enabled.\nThe companion mari_emote_controls addon must be installed/enabled.\nThese are hand-animated interpretations of the linked reference reel.\nThe original dance scene is preserved as Classroom-dance.blend.\n')
guide=bpy.data.texts.get('START HERE | Classroom and character')
if guide:
    guide.clear();guide.write(bpy.data.texts['EMOTES | Numpad controls'].as_string())
controller=PROJECT/'scripts/animation/mari_emote_controls.py'
text=bpy.data.texts.new('mari_emote_controls.py')
text.write(controller.read_text(encoding='utf-8'))
report['effect_meshes']=len(effects.objects)
report['rig_bones']=len(rig.data.bones)
report['source_reel']=manifest['source']
(PROJECT/'reports/final/emote-build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(PROJECT/'reports/final/emote-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
print('EMOTE_PACK_SAVED',OUT,flush=True)
