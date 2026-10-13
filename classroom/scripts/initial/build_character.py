# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

exec(compile(open(str(project_path('helpers.py')),encoding='utf-8-sig').read(),'helpers.py','exec'))
scene=bpy.context.scene
COLL=collection('05 Character | reference-inspired',scene)
skinmat=mat('Character | peach skin',(.93,.66,.52),.64)
blush=mat('Character | cheek tint',(.91,.35,.33),.7)
hair=mat('Character | apricot hair',(.95,.40,.16),.43)
hairlight=mat('Character | golden strands',(1,.59,.28),.46)
hairshade=mat('Character | copper shadows',(.67,.22,.10),.5)
ivory=mat('Character | white sports fabric',(.9,.92,1),.68)
navy=mat('Character | charcoal violet fabric',(.075,.084,.15),.7)
zipmat=mat('Character | pale piping',(.68,.74,.86),.4)
sole=mat('Character | shoe sole',(.72,.76,.85),.62)
ink=mat('Character | ink outlines',(.042,.036,.06),.6)
irismat=mat('Character | turquoise iris',(.08,.62,.68),.28)
irislight=mat('Character | iris light',(.26,.90,.89),.25)
halo=mat('Character | luminous pale gold',(.98,.84,.29),.33,.3,1.3)
strapmat=mat('Character | cream strap',(.81,.76,.56),.6)
leafmat=mat('Character | floral leaf',(.1,.38,.3),.6)
lilac=mat('Character | flower lilac',(.52,.46,.76),.55)
watermat=mat('Character | bottle translucent blue',(.29,.67,.85),.22,.15)
char_objects=[];bindings=[];blink_objects=[]

def bind(ob,bone):
    char_objects.append(ob);bindings.append((ob,bone));return ob

def B(name,pos,size,material,bone,rounded=.02):return bind(box(name,pos,size,material,rounded),bone)
def E(name,pos,size,material,bone,seg=24,rings=14):return bind(ellipsoid(name,pos,size,material,seg,rings),bone)
def R(name,a,b,r,material,bone,r2=None,n=16):return bind(rod(name,a,b,r,material,r2,n),bone)
def L(name,points,r,material,bone,cyclic=False):return bind(line(name,points,r,material,cyclic),bone)

def loft(name, rings, material, bone, n=32, subdiv=1):
    vs=[];fs=[]
    for cx,cy,z,rx,ry in rings:
        for i in range(n):
            a=i*math.tau/n;vs.append((cx+rx*math.cos(a),cy+ry*math.sin(a),z))
    for j in range(len(rings)-1):
        for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    fs.extend([tuple(reversed(range(n))),tuple(range((len(rings)-1)*n,len(rings)*n))])
    ob=mesh(name,vs,fs,material,True)
    if subdiv:
        m=ob.modifiers.new('Smooth silhouette','SUBSURF');m.levels=subdiv;m.render_levels=subdiv
    return bind(ob,bone)

# A tailored sleeveless track jacket and articulated body.
loft('Track jacket | fitted torso',[(0,0,.97,.235,.145),(0,0,.99,.245,.15),(0,0,1.08,.217,.14),(0,0,1.24,.20,.132),(0,.005,1.40,.22,.125),(0,.005,1.46,.175,.108),(0,.005,1.475,.155,.09)],navy,'TORSO')
loft('White jacket hem',[(0,0,.965,.235,.148),(0,0,.975,.247,.153),(0,0,1.005,.247,.153),(0,0,1.012,.235,.148)],ivory,'pelvis',subdiv=0)
R('Neck',(0,0,1.43),(0,0,1.57),.062,skinmat,'neck',r2=.065)
loft('Stand-up collar',[(0,0,1.42,.118,.084),(0,0,1.49,.095,.077),(0,0,1.535,.085,.071)],navy,'chest',subdiv=0)
L('Silver center zipper',[(0,-.155,.998),(0,-.142,1.2),(0,-.133,1.38),(0,-.081,1.52)],.007,zipmat,'TORSO')
B('Zipper pull',(0,-.094,1.48),(.017,.012,.037),zipmat,'chest',.004)
for side in [-1,1]:
    L('White jacket side piping',[(side*.18,-.106,.998),(side*.173,-.105,1.15),(side*.18,-.077,1.37),(side*.152,-.06,1.46)],.014,ivory,'TORSO')
    B('Shorts leg', (side*.115,.004,.91),(.215,.265,.22),navy,'thigh.L' if side==1 else 'thigh.R',.052)
    L('Shorts hem',[(side*.215,-.104,.827),(side*.117,-.135,.812),(side*.022,-.105,.827)],.007,zipmat,'pelvis')
# Legs and shoes, rest stance slightly apart.
for s,suffix in [(1,'L'),(-1,'R')]:
    x=s*.118
    loft('Skin | thigh.'+suffix,[(x,0,.98,.098,.099),(x,0,.90,.1,.1),(x,0,.78,.092,.092),(x,0,.63,.068,.071),(x,0,.56,.063,.063),(x,0,.52,.062,.061)],skinmat,'LEG.'+suffix)
    loft('Knee and calf.'+suffix,[(x,0,.58,.064,.065),(x,0,.51,.067,.066),(x,.015,.43,.073,.066),(x,.015,.29,.053,.052),(x,0,.15,.042,.042)],skinmat,'shin.'+suffix)
    loft('Long white sock.'+suffix,[(x,0,.15,.045,.045),(x,.012,.26,.052,.053),(x,.014,.41,.067,.066),(x,.008,.49,.068,.066),(x,.008,.51,.067,.066)],ivory,'shin.'+suffix)
    R('Sock cuff.'+suffix,(x,.008,.49),(x,.008,.515),.069,zipmat,'shin.'+suffix)
    E('Sneaker sole.'+suffix,(x,-.038,.071),(.081,.148,.046),sole,'foot.'+suffix)
    E('Sneaker upper.'+suffix,(x,-.033,.119),(.073,.135,.071),navy,'foot.'+suffix)
    E('Sneaker white toe.'+suffix,(x,-.122,.096),(.072,.061,.032),ivory,'foot.'+suffix)
    B('Shoe tongue.'+suffix,(x,-.024,.174),(.09,.095,.025),navy,'foot.'+suffix,.015)
    for i in range(4):
        yy=-.081+i*.025; zz=.164+(i*.005)
        L('Criss-cross lace.'+suffix,[(x-.036,yy,zz),(x+.032,yy+.026,zz+.007)],.004,ivory,'foot.'+suffix)
        L('Criss-cross lace.'+suffix,[(x+.036,yy,zz),(x-.032,yy+.026,zz+.007)],.004,ivory,'foot.'+suffix)
# Arms have separate sleeve segments and full articulated hands.
armdata={}
for s,suffix in [(1,'L'),(-1,'R')]:
    shoulder=Vector((s*.19,0,1.405));elbow=Vector((s*.38,-.014,1.20));wrist=Vector((s*.49,-.03,1.01));handtip=wrist+Vector((s*.04,-.015,-.095))
    armdata[suffix]=(shoulder,elbow,wrist,handtip)
    R('Puffy sleeve upper.'+suffix,shoulder,elbow,.107,ivory,'upper_arm.'+suffix,r2=.12,n=24)
    E('Soft sleeve shoulder.'+suffix,shoulder,(.117,.11,.12),ivory,'upper_arm.'+suffix)
    E('Sleeve elbow fold.'+suffix,elbow,(.127,.115,.12),ivory,'forearm.'+suffix)
    R('Bell sleeve forearm.'+suffix,elbow,wrist,.12,ivory,'forearm.'+suffix,r2=.085,n=24)
    R('Dark elastic cuff.'+suffix,wrist-Vector((s*.015,0,-.025)),wrist+Vector((s*.012,0,-.025)),.069,navy,'hand.'+suffix,n=24)
    E('Palm.'+suffix,(wrist+handtip)/2,(.043,.029,.063),skinmat,'hand.'+suffix)
    for i,f in enumerate(['index','middle','ring','pinky']):
        start=handtip+Vector((0,(i-1.5)*.014,.018));mid=start+Vector((s*.005,-.003,-.027));end=mid+Vector((s*.006,-.004,-.025+(i==3)*.008))
        R(f+' proximal.'+suffix,start,mid,.009,skinmat,f+'.01.'+suffix,r2=.008,n=10)
        E(f+' knuckle.'+suffix,mid,(.008,.009,.01),skinmat,f+'.02.'+suffix,16,10)
        R(f+' distal.'+suffix,mid,end,.008,skinmat,f+'.02.'+suffix,r2=.005,n=10)
    thumbstart=wrist+Vector((-s*.025,-.022,-.025));thumbmid=thumbstart+Vector((-s*.017,-.021,-.017));thumbend=thumbmid+Vector((-s*.006,-.011,-.025))
    R('Thumb proximal.'+suffix,thumbstart,thumbmid,.012,skinmat,'thumb.01.'+suffix,r2=.01)
    R('Thumb distal.'+suffix,thumbmid,thumbend,.01,skinmat,'thumb.02.'+suffix,r2=.006)
# Anime face, hair cap, fringe, and long layered locks.
E('Hair | back cap',(0,.046,1.76),(.253,.176,.278),hair,'head',32,20)
E('Face',(0,-.075,1.736),(.213,.147,.231),skinmat,'head',32,24)
E('Chin',(0,-.103,1.60),(.112,.096,.075),skinmat,'head')
for s in [-1,1]:
    E('Ear',(s*.203,-.056,1.726),(.033,.036,.059),skinmat,'head')
    x=s*.09;z=1.755
    for name,pos,size,m in [
        ('Eye white',(x,-.207,z),(.062,.015,.045),ivory),
        ('Turquoise iris',(x,-.222,z-.002),(.033,.007,.041),irismat),
        ('Iris lower glow',(x,-.230,z-.017),(.025,.004,.019),irislight),
        ('Pupil',(x,-.232,z+.003),(.013,.004,.029),ink),
        ('Eye sparkle',(x-.012,-.238,z+.018),(.010,.003,.011),ivory),
        ('Eye sparkle small',(x+.013,-.237,z-.017),(.005,.002,.005),ivory),
    ]:
        ob=E(name+(' L' if s==1 else ' R'),pos,size,m,'head');blink_objects.append((ob,z))
    L('Upper lash',[(x-.061,-.213,z+.018),(x,-.227,z+.047),(x+.061,-.210,z+.02)],.007,ink,'head')
    L('Outer eyelash',[(x+s*.045,-.219,z+.031),(x+s*.071,-.214,z+.049)],.0045,ink,'head')
    L('Soft eyebrow',[(x-.040,-.190,1.832),(x,-.20,1.844),(x+.04,-.19,1.837)],.006,hairshade,'head')
    E('Warm cheek',(s*.129,-.194,1.677),(.036,.007,.012),blush,'head')
E('Nose',(0,-.22,1.693),(.013,.013,.021),skinmat,'head')
L('Smile',[(-.036,-.210,1.64),(0,-.222,1.63),(.036,-.210,1.64)],.0035,ink,'head')
# Back hair curtain and swept long side locks.
for i,x in enumerate([-.18,-.09,0,.09,.18]):
    loft('Hair | back lock %d'%i,[(x,.13,1.94,.082,.079),(x,.17,1.79,.09,.085),(x*1.2,.16,1.52,.09,.065),(x*1.3,.20,1.26,.075,.05),(x*1.5,.19,1.14,.004,.005)],hair if i%2 else hairshade,'hair.back',n=20)
for s,suffix in [(1,'L'),(-1,'R')]:
    loft('Hair | long front lock.'+suffix,[(s*.177,-.015,1.97,.066,.076),(s*.226,-.066,1.83,.067,.073),(s*.231,-.086,1.61,.062,.057),(s*.25,-.101,1.42,.063,.045),(s*.283,-.075,1.31,.037,.024),(s*.307,-.041,1.35,.002,.002)],hair,'hair.'+suffix,n=20)
    L('Hair highlight.'+suffix,[(s*.20,-.127,1.91),(s*.255,-.144,1.72),(s*.253,-.153,1.49),(s*.272,-.114,1.36)],.008,hairlight,'hair.'+suffix)
for i,(x,tipz) in enumerate([(-.17,1.79),(-.103,1.815),(-.034,1.779),(.045,1.83),(.119,1.807),(.18,1.77)]):
    loft('Hair | sculpted fringe %d'%i,[(x*.45,-.077,1.987,.06,.056),(x*.86,-.152,1.93,.072,.04),(x,-.204,1.87,.058,.025),(x+.012,-.225,tipz,.003,.003)],hairlight if i in [1,2,3] else hair,'head',n=20)
# White headband arcs across the crown.
L('White headband',[(-.214,-.103,1.894),(-.16,-.115,1.98),(0,-.10,2.019),(.16,-.115,1.98),(.214,-.103,1.894)],.025,ivory,'head')
# Pointed ears with pale inset fur.
for s,suffix in [(1,'L'),(-1,'R')]:
    vs=[(s*.12,.035,1.955),(s*.255,.044,1.973),(s*.228,.051,2.249),(s*.17,-.069,2.005)]
    ob=mesh('Pointed ear.'+suffix,vs,[(0,1,2),(0,2,3),(1,3,2),(0,3,1)],hair,True);bevel(ob,.012);bind(ob,'ear.'+suffix)
    vs2=[(s*.153,-.032,2.017),(s*.224,-.035,2.028),(s*.223,.025,2.204)]
    ob=mesh('Ear inner pink.'+suffix,vs2,[(0,1,2)],blush);solid=ob.modifiers.new('Inset fur thickness','SOLIDIFY');solid.thickness=.007;bind(ob,'ear.'+suffix)
    for i in range(3):
        x=s*(.16+i*.028);z=2.033+i*.012
        ob=mesh('Ear white tuft',[(x,-.061,z-.026),(x+s*.027,-.064,z+.003),(x+s*.009,-.065,z+.054)],[(0,1,2)],ivory);bind(ob,'ear.'+suffix)
# Halo: thin floating ring and star points above the head, slightly behind.
pts=[(.31*math.cos(i*math.tau/64),.065,2.30+.20*math.sin(i*math.tau/64)) for i in range(64)]
L('Halo | oval ring',pts,.015,halo,'halo',True)
for i in range(6):
    a=i*math.tau/6;cx=.31*math.cos(a);cz=2.30+.20*math.sin(a)
    star=[]
    for j in range(8):
        ang=j*math.tau/8;rr=.067 if j%2==0 else .026;star.append((cx+rr*math.cos(ang),.064,cz+rr*math.sin(ang)))
    ob=mesh('Halo | luminous star',star,[tuple(range(8))],halo);sol=ob.modifiers.new('Star thickness','SOLIDIFY');sol.thickness=.006;bind(ob,'halo')
# Flower clip at left temple.
for i in range(3):
    cx=-.183+(i%2)*.018;cz=1.89+(i-1)*.046
    for j in range(5):
        a=j*math.tau/5;E('Hair clip flower petal',(cx+.024*math.cos(a),-.194,cz+.024*math.sin(a)),(.019,.008,.017),ivory if i!=1 else lilac,'head',16,10)
    E('Flower center',(cx,-.207,cz),(.01,.006,.01),halo,'head',16,10)
for i in range(2):
    ob=E('Hair clip leaf',(-.23-i*.012,-.169,1.94+i*.034),(.028,.009,.051),leafmat,'head');ob.rotation_euler[1]=-.55
# Ribbon tails behind neck.
for s in [-1,1]:
    L('Hair ribbon',[(s*.04,.14,1.52),(s*.22,.15,1.52),(s*.35,.17,1.44),(s*.38,.16,1.50)],.023,ivory,'hair.back')
# Shoulder bag, crossbody strap and hardware.
L('Crossbody cream strap',[(-.165,-.087,1.465),(-.10,-.167,1.34),(.05,-.163,1.16),(.235,-.144,.93),(.35,-.072,.80)],.024,strapmat,'TORSO')
L('Strap white center',[(-.165,-.11,1.465),(-.1,-.192,1.34),(.05,-.19,1.16),(.235,-.166,.93),(.35,-.095,.80)],.014,ivory,'TORSO')
B('Shoulder bag | body',(.35,.005,.77),(.31,.21,.34),ivory,'bag',.035)
B('Shoulder bag | front flap',(.35,-.116,.82),(.31,.035,.23),ivory,'bag',.018)
for dx in [-.137,.137]:B('Bag gold trim',(.35+dx,-.139,.785),(.009,.008,.27),strapmat,'bag',.004)
B('Bag lower trim',(.35,-.14,.656),(.275,.01,.011),strapmat,'bag',.004)
B('Bag buckle',(.35,-.142,.764),(.047,.008,.036),halo,'bag',.004)
L('Bag tag chain',[(.27,-.14,.67),(.27,-.15,.60),(.255,-.158,.57)],.004,zipmat,'bag')
B('Bag ID tag',(.257,-.154,.558),(.055,.013,.08),navy,'bag',.006)
B('ID card',(.257,-.162,.558),(.043,.003,.056),ivory,'bag',.001)
# Bottle attached to left hand, moves with the animated forearm.
w=armdata['L'][2]
bottle_a=(w.x+.035,w.y-.057,w.z-.10);bottle_b=(w.x+.035,w.y-.057,w.z+.115)
R('Water bottle',bottle_a,bottle_b,.043,watermat,'hand.L',r2=.038,n=24)
R('Bottle neck',bottle_b,(bottle_b[0],bottle_b[1],bottle_b[2]+.037),.022,watermat,'hand.L',n=24)
R('Bottle cap',(bottle_b[0],bottle_b[1],bottle_b[2]+.032),(bottle_b[0],bottle_b[1],bottle_b[2]+.055),.025,navy,'hand.L',n=24)
R('Bottle label',(bottle_a[0],bottle_a[1],bottle_a[2]+.064),(bottle_a[0],bottle_a[1],bottle_a[2]+.127),.044,ivory,'hand.L',n=24)
L('Bottle highlight',[(bottle_a[0]-.025,bottle_a[1]-.034,bottle_a[2]+.018),(bottle_a[0]-.022,bottle_a[1]-.034,bottle_b[2]-.025)],.004,ivory,'hand.L')
# Complete FK skeleton with hands, fingers, toes and secondary controls.
arm=bpy.data.armatures.new('Character | full body skeleton');rig=bpy.data.objects.new('CHARACTER_RIG | select to pose',arm);COLL.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
def bone(name,head,tail,parent=None):
    b=arm.edit_bones.new(name);b.head=head;b.tail=tail
    if parent:b.parent=arm.edit_bones[parent]
    return b
bone('root',(0,0,0),(0,0,.16));bone('pelvis',(0,0,.88),(0,0,1.06),'root');bone('spine',(0,0,1.06),(0,0,1.27),'pelvis');bone('chest',(0,0,1.27),(0,0,1.46),'spine');bone('neck',(0,0,1.46),(0,0,1.56),'chest');bone('head',(0,0,1.56),(0,0,1.98),'neck')
for s,suffix in [(1,'L'),(-1,'R')]:
    x=s*.118;bone('thigh.'+suffix,(x,0,.96),(x,0,.55),'pelvis');bone('shin.'+suffix,(x,0,.55),(x,0,.15),'thigh.'+suffix);bone('foot.'+suffix,(x,0,.15),(x,-.12,.08),'shin.'+suffix);bone('toe.'+suffix,(x,-.12,.08),(x,-.19,.08),'foot.'+suffix)
    sh,el,wr,ht=armdata[suffix];bone('shoulder.'+suffix,(s*.03,0,1.41),sh,'chest');bone('upper_arm.'+suffix,sh,el,'shoulder.'+suffix);bone('forearm.'+suffix,el,wr,'upper_arm.'+suffix);bone('hand.'+suffix,wr,ht,'forearm.'+suffix)
    for i,f in enumerate(['index','middle','ring','pinky']):
        start=ht+Vector((0,(i-1.5)*.014,.018));mid=start+Vector((s*.005,-.003,-.027));end=mid+Vector((s*.006,-.004,-.025+(i==3)*.008))
        bone(f+'.01.'+suffix,start,mid,'hand.'+suffix);bone(f+'.02.'+suffix,mid,end,f+'.01.'+suffix)
    start=wr+Vector((-s*.025,-.022,-.025));mid=start+Vector((-s*.017,-.021,-.017));end=mid+Vector((-s*.006,-.011,-.025))
    bone('thumb.01.'+suffix,start,mid,'hand.'+suffix);bone('thumb.02.'+suffix,mid,end,'thumb.01.'+suffix)
    bone('hair.'+suffix,(s*.21,0,1.88),(s*.26,-.08,1.32),'head');bone('ear.'+suffix,(s*.17,0,1.98),(s*.22,.04,2.23),'head')
bone('hair.back',(0,.14,1.87),(0,.17,1.2),'head');bone('halo',(0,.06,2.12),(0,.06,2.42),'head');bone('bag',(.28,.0,.97),(.35,0,.69),'pelvis')
bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True;arm.display_type='OCTAHEDRAL'
# Every component is skinned. Cloth torso and knees receive blended weights.
for ob,binding in bindings:
    if ob.type!='MESH':
        dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));new_ob=bpy.data.objects.new(ob.name,me);COLL.objects.link(new_ob);new_ob.matrix_world=ob.matrix_world.copy();bpy.data.objects.remove(ob,do_unlink=True);ob=new_ob
    ob.data.transform(ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
    if binding=='TORSO':
        gs={n:ob.vertex_groups.new(name=n) for n in ['pelvis','spine','chest']}
        for v in ob.data.vertices:
            z=v.co.z
            if z<1.16:
                w=max(0,min(1,(z-1.02)/.14));gs['pelvis'].add([v.index],1-w,'REPLACE');gs['spine'].add([v.index],w,'REPLACE')
            else:
                w=max(0,min(1,(z-1.20)/.19));gs['spine'].add([v.index],1-w,'REPLACE');gs['chest'].add([v.index],w,'REPLACE')
    elif binding.startswith('LEG.'):
        suf=binding[-1];g1=ob.vertex_groups.new(name='thigh.'+suf);g2=ob.vertex_groups.new(name='shin.'+suf)
        for v in ob.data.vertices:
            w=max(0,min(1,(.62-v.co.z)/.1));g1.add([v.index],1-w,'REPLACE');g2.add([v.index],w,'REPLACE')
    else:
        g=ob.vertex_groups.new(name=binding);g.add(list(range(len(ob.data.vertices))),1,'REPLACE')
    ob.parent=rig
    mod=ob.modifiers.new('Character skin deformation','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True
rig.location=(1.35,3.23,.055)
rig['rig_notes']='Full FK body rig: root, pelvis, spine, chest, neck, head, shoulders, arms, hands, individual fingers, legs, feet, toes; hair, ears, halo and bag. Eye meshes have animated Blink shape keys.'
rig['reference']='Stylized interpretation of user-provided orange-haired, cat-eared character reference.'
# Four-second looping friendly greeting: subtle body shift, wave and secondary sway.
scene.frame_start=1;scene.frame_end=120;scene.render.fps=24
for pb in rig.pose.bones:pb.rotation_mode='XYZ'
for f in [1,16,31,46,61,76,91,106,120]:
    t=(f-1)/119*math.tau
    pose={
        'pelvis':(.0,.018*math.sin(t),.018*math.sin(t)),
        'spine':(.015*math.sin(t),-.018*math.sin(t),0),
        'chest':(.012*math.sin(t),0,.015*math.sin(t)),
        'head':(.035*math.sin(t),.07*math.sin(t+.4),-.045),
        'upper_arm.R':(.0,0,-.85),
        'forearm.R':(.0,0,-1.10),
        'hand.R':(.1,.13*math.sin(t*2),.16*math.sin(t*2)),
        'upper_arm.L':(.0,0,.30),
        'forearm.L':(-.28,0,.92),
        'hand.L':(.0,.0,.10),
        'hair.L':(.023*math.sin(t-.5),.028*math.sin(t),.015*math.cos(t)),
        'hair.R':(.022*math.sin(t+.3),-.028*math.sin(t),-.015*math.cos(t)),
        'hair.back':(.025*math.sin(t-.6),.018*math.cos(t),0),
        'bag':(.015*math.sin(t-.4),.02*math.sin(t),.02*math.cos(t)),
        'ear.L':(.015*math.sin(t*2),0,.025*math.sin(t)),
        'ear.R':(.015*math.sin(t*2+.5),0,-.025*math.sin(t)),
    }
    for name,rot in pose.items():
        pb=rig.pose.bones[name];pb.rotation_euler=rot;pb.keyframe_insert(data_path='rotation_euler',frame=f,group=name)
    # Bottle-hand fingers softly curled; waving fingers splayed naturally.
    for suf in ['L','R']:
        for finger in ['index','middle','ring','pinky','thumb']:
            for idx in ['01','02']:
                p=rig.pose.bones[finger+'.'+idx+'.'+suf];p.rotation_euler[0]=.30 if suf=='L' else .06;p.keyframe_insert(data_path='rotation_euler',frame=f,group='Fingers')
if rig.animation_data and rig.animation_data.action:rig.animation_data.action.name='Greeting | idle, wave and secondary motion (120f)'
for ob,cz in blink_objects:
    ob.shape_key_add(name='Basis');key=ob.shape_key_add(name='Blink')
    for v in key.data:v.co.z=cz+(v.co.z-cz)*.07
    for f,val in [(1,0),(36,0),(39,1),(42,0),(91,0),(94,1),(97,0),(120,0)]:key.value=val;key.keyframe_insert(data_path='value',frame=f)
scene.timeline_markers.new('GREETING LOOP START',frame=1);scene.timeline_markers.new('BLINK',frame=39);scene.timeline_markers.new('LOOP END',frame=120)
scene.frame_set(16)
# A portrait camera allows close inspection of the rigged character.
COLL=bpy.data.collections.get('06 Cameras and lighting')
portrait=camera('Camera | character portrait',(4.15,-2.25,2.85),(1.35,3.23,1.34),lens=70)
scene.camera=bpy.data.objects.get('Camera | classroom overview')
# Store useful viewport setup and a short in-file guide.
for ob in bpy.context.selected_objects:ob.select_set(False)
rig.select_set(True);bpy.context.view_layer.objects.active=rig
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.shading.type='MATERIAL'
notes=bpy.data.texts.new('START HERE | Classroom and character')
notes.write('CLASSROOM + RIGGED CHARACTER\n\nSpacebar: play frames 1-120 at 24 fps.\nSelect CHARACTER_RIG, enter Pose Mode to pose any body part.\nAll character meshes have armature skinning. Fingers, feet, toes, ears, hair, halo and bag have bones.\nFace meshes include animated Blink shape keys.\nUse Camera | classroom overview or Camera | character portrait.\nScene is a stylized cutaway; original default scene is preserved.\nCharacter is an original stylized 3D interpretation of the supplied reference.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Classroom.blend'))
result={'character_objects':len(char_objects),'bones':len(arm.bones),'animation_frames':[1,120],'file':str(ROOT/'Classroom.blend')}

