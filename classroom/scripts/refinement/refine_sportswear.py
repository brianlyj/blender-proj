# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

exec(compile(open(str(project_path('helpers.py')),encoding='utf-8-sig').read(),'helpers.py','exec'))
import bmesh
REV=ROOT/'revision';scene=bpy.context.scene;rig=bpy.data.objects['MARI | refined character rig'];COLL=bpy.data.collections['05 Character | refined sports outfit']
white=bpy.data.materials['R2 | Character | white sports fabric'];navy=bpy.data.materials['R2 | Character | charcoal violet fabric'];trim=bpy.data.materials['R2 | Character | pale piping'];gold=bpy.data.materials['R2 | Character | cream strap'];skinmat=bpy.data.materials['R2 | Character | peach skin'];hairmat=bpy.data.objects['R2 | Hair | textured crown and fringe'].data.materials[0]
ink=mat('R2 | fine ink',(.029,.025,.039),1);ink.use_backface_culling=True
n=ink.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');em.inputs[0].default_value=(.027,.021,.031,1);ink.node_tree.links.new(em.outputs[0],out.inputs[0])
shadow=mat('R2 | fabric seam shadow',(.20,.22,.31),.85)
# Remove only the first-pass pieces that are being rebuilt.
remove=['Track jacket','White jacket hem','White jacket side piping','Silver center zipper','Zipper pull','Stand-up collar','Shorts leg','Shorts hem','Continuous sports sleeve','Crossbody','Strap white center','Shoulder bag','Bag gold','Bag lower','Bag buckle','Sneaker','Shoe tongue','Criss-cross lace','Long face-framing lock','Side hair layer','Back outer sweep','Back hair layer']
for ob in list(COLL.objects):
    if ob.type=='MESH' and ob.name.startswith('R2 | ') and any(ob.name[5:].startswith(prefix) for prefix in remove):bpy.data.objects.remove(ob,do_unlink=True)

def skin(ob,binding):
    if ob.type!='MESH':
        dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));co=bpy.data.objects.new(ob.name,me);COLL.objects.link(co);co.matrix_world=ob.matrix_world.copy();bpy.data.objects.remove(ob,do_unlink=True);ob=co
    ob.data.transform(Matrix.LocRotScale(ob.location,ob.rotation_euler.to_quaternion(),ob.scale));ob.matrix_world=Matrix.Identity(4);ob.parent=rig
    if binding=='TORSO':
        groups={name:ob.vertex_groups.new(name=name) for name in ['pelvis','spine','chest']}
        for v in ob.data.vertices:
            z=v.co.z
            if z<1.17:a,b,w='pelvis','spine',max(0,min(1,(z-1.01)/.16))
            else:a,b,w='spine','chest',max(0,min(1,(z-1.20)/.19))
            groups[a].add([v.index],1-w,'REPLACE');groups[b].add([v.index],w,'REPLACE')
    else:
        g=ob.vertex_groups.new(name=binding);g.add(list(range(len(ob.data.vertices))),1,'REPLACE')
    mod=ob.modifiers.new('Skin deformation','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True;return ob

def ribbon(name,points,width,material,bone):
    ps=[Vector(p) for p in points];vs=[]
    for i,p in enumerate(ps):
        d=ps[min(i+1,len(ps)-1)]-ps[max(i-1,0)];v=d.cross(Vector((0,-1,0))).normalized()*width/2
        vs.extend([p-v,p+v])
    ob=mesh('R2 | '+name,vs,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(ps)-1)],material,True);so=ob.modifiers.new('Fabric thickness','SOLIDIFY');so.thickness=.0025;return skin(ob,bone)

def loft(name,rings,material,bone,seg=48):
    vs=[];fs=[]
    for j,(x,y,z,rx,ry) in enumerate(rings):
        for i in range(seg):
            a=i*math.tau/seg;fold=.0025*math.sin(a*5+j*.8)*math.sin(j/(len(rings)-1)*math.pi)
            xx=math.copysign(abs(math.cos(a))**.78,math.cos(a));yy=math.copysign(abs(math.sin(a))**.88,math.sin(a))
            vs.append((x+(rx+fold)*xx,y+(ry+fold)*yy,z))
    for j in range(len(rings)-1):
        for i in range(seg):fs.append((j*seg+i,j*seg+(i+1)%seg,(j+1)*seg+(i+1)%seg,(j+1)*seg+i))
    fs.extend([tuple(reversed(range(seg))),tuple(range((len(rings)-1)*seg,len(rings)*seg))]);ob=mesh('R2 | '+name,vs,fs,material,True)
    su=ob.modifiers.new('Tailored surface','SUBSURF');su.levels=1;su.render_levels=2;return skin(ob,bone)
# Tailored jacket body, a flat zipper, contrasting shoulder panels and slim seams.
loft('Tailored track jacket',[(0,0,.95,.245,.146),(0,0,.965,.256,.155),(0,0,.99,.256,.155),(0,0,1.04,.242,.15),(0,0,1.12,.213,.14),(0,0,1.23,.20,.132),(0,0,1.34,.213,.131),(0,.008,1.41,.23,.118),(0,.01,1.46,.164,.095),(0,.01,1.47,.15,.087)],navy,'TORSO')
loft('Bound jacket hem',[(0,0,.95,.244,.147),(0,0,.955,.255,.157),(0,0,.977,.259,.159),(0,0,.99,.254,.156)],white,'pelvis')
loft('High collar',[(0,0,1.437,.116,.091),(0,0,1.46,.11,.086),(0,0,1.51,.085,.074),(0,0,1.531,.084,.073)],navy,'chest')
ribbon('Zipper tape',[(0,-.159,.981),(0,-.155,1.04),(0,-.143,1.16),(0,-.137,1.31),(0,-.119,1.42),(0,-.080,1.525)],.012,white,'TORSO')
for i in range(23):
    z=.995+i*.022;y=-.157 if z<1.1 else (-.142 if z<1.32 else -.127)
    ob=box('R2 | zipper tooth',(.003 if i%2 else -.003,y-.003,z),(.007,.005,.004),trim,0);skin(ob,'TORSO')
ob=box('R2 | zipper pull',(0,-.084,1.488),(.012,.004,.027),trim,.003);skin(ob,'chest')
for sign in [-1,1]:
    ribbon('Ivory jacket side stripe',[(sign*.19,-.112,.987),(sign*.189,-.115,1.05),(sign*.168,-.112,1.15),(sign*.178,-.103,1.33),(sign*.184,-.080,1.408)],.019,white,'TORSO')
    ribbon('Shoulder contrast panel',[(sign*.096,-.074,1.456),(sign*.155,-.096,1.423),(sign*.212,-.102,1.371)],.033,white,'chest')
    ribbon('Welt pocket trim',[(sign*.083,-.148,1.062),(sign*.147,-.133,1.112),(sign*.171,-.119,1.138)],.006,trim,'TORSO')
# Small embroidered emblem and label on chest.
ob=line('R2 | embroidered crest',[(.08,-.143,1.357),(.095,-.145,1.38),(.11,-.143,1.357),(.095,-.145,1.341)],.0018,gold,True);skin(ob,'chest')
ob=text('R2 | athletics embroidery','TRINITY',(.068,-.147,1.324),.011,trim);skin(ob,'chest')
for sign,suf in [(1,'L'),(-1,'R')]:
    x=sign*.118
    loft('Tailored shorts.'+suf,[(x,0,.963,.114,.124),(x,0,.943,.119,.129),(x,0,.88,.121,.129),(x,0,.812,.108,.122),(x,0,.801,.106,.12)],navy,'thigh.'+suf,32)
    loft('Shorts bound edge.'+suf,[(x,0,.799,.106,.12),(x,0,.803,.109,.123),(x,0,.813,.109,.123),(x,0,.818,.107,.121)],trim,'thigh.'+suf,32)
# Bell sleeves with folds and anatomically blended elbow weights.
for sign,suf in [(1,'L'),(-1,'R')]:
    a=rig.data.bones['upper_arm.'+suf].head_local;b=rig.data.bones['forearm.'+suf].head_local;c=rig.data.bones['hand.'+suf].head_local
    vs=[];fs=[];NR=29;NS=32
    for j in range(NR):
        t=j/(NR-1);p=a.lerp(b,t/.56) if t<=.56 else b.lerp(c,(t-.56)/.44);d=(b-a if t<.56 else c-b).normalized();q=d.to_track_quat('Z','Y')
        radius=.096+.045*math.sin(t*math.pi)-.017*t
        for i in range(NS):
            ang=i*math.tau/NS;fold=.009*math.cos(ang*5+t*7)*(math.exp(-((t-.61)/.17)**2)+.45*math.exp(-((t-.88)/.10)**2))
            vs.append(p+q@Vector(((radius+fold)*math.cos(ang),(radius+fold)*math.sin(ang),0)))
    for j in range(NR-1):
        for i in range(NS):fs.append((j*NS+i,j*NS+(i+1)%NS,(j+1)*NS+(i+1)%NS,(j+1)*NS+i))
    ob=mesh('R2 | shaped sleeve with elbow folds.'+suf,vs,fs,white,True);ob.parent=rig;g1=ob.vertex_groups.new(name='upper_arm.'+suf);g2=ob.vertex_groups.new(name='forearm.'+suf)
    for j in range(NR):
        w=max(0,min(1,(j/(NR-1)-.44)/.24));ids=list(range(j*NS,(j+1)*NS));g1.add(ids,1-w,'REPLACE');g2.add(ids,w,'REPLACE')
    mod=ob.modifiers.new('Sleeve skin','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True;su=ob.modifiers.new('Cloth smoothing','SUBSURF');su.levels=1;su.render_levels=2
# Slim flat shoulder strap and a gusseted structured bag.
ribbon('Flat crossbody strap',[(-.163,-.097,1.458),(-.11,-.183,1.365),(-.005,-.185,1.213),(.102,-.182,1.061),(.232,-.169,.897),(.345,-.125,.793)],.035,gold,'TORSO')
ribbon('Strap satin facing',[(-.163,-.102,1.458),(-.11,-.187,1.365),(-.005,-.189,1.213),(.102,-.186,1.061),(.232,-.173,.897),(.345,-.129,.793)],.025,white,'TORSO')
for name,pos,size,m,bev in [('Bag | structured body',(.347,.012,.765),(.307,.195,.32),white,.027),('Bag | front envelope flap',(.347,-.098,.825),(.309,.026,.18),white,.018),('Bag | bottom gusset',(.347,.012,.617),(.29,.19,.029),trim,.012),('Bag | cream front band',(.347,-.121,.703),(.285,.008,.009),gold,.003),('Bag | strap buckle',(.337,-.143,.831),(.048,.008,.041),gold,.005)]:skin(box('R2 | '+name,pos,size,m,bev),'bag')
for dx in [-.134,.134]:ribbon('Bag welt seam',[(.347+dx,-.094,.622),(.347+dx,-.102,.764),(.347+dx,-.102,.898)],.008,gold,'bag')
for dz in [.646,.875]:
    for i in range(16):skin(box('R2 | bag stitching',(.227+i*.016,-.109,dz),(.007,.003,.0025),gold,0),'bag')
# A small geometric crest on the flap.
for sc in [1,.65]:skin(line('R2 | bag crest',[(.347,-.119,.847+.025*sc),(.347+.023*sc,-.119,.822),(.347,-.119,.797-.001*sc),(.347-.023*sc,-.119,.822)],.0018,gold,True),'bag')
# Sculpted sneakers with an actual sole profile, tongue, heel tab, lace stays and laces.
for sign,suf in [(1,'L'),(-1,'R')]:
    x=sign*.118
    def shoe(name,sections,material):
        vs=[];fs=[];NS=32
        for y,z,w,h in sections:
            for i in range(NS):
                a=i*math.tau/NS;vs.append((x+w*math.cos(a),y,z+h*math.sin(a)))
        for j in range(len(sections)-1):
            for i in range(NS):fs.append((j*NS+i,j*NS+(i+1)%NS,(j+1)*NS+(i+1)%NS,(j+1)*NS+i))
        fs.extend([tuple(reversed(range(NS))),tuple(range((len(sections)-1)*NS,len(sections)*NS))]);ob=mesh('R2 | '+name+'.'+suf,vs,fs,material,True);su=ob.modifiers.new('Sneaker smoothing','SUBSURF');su.levels=1;su.render_levels=2;skin(ob,'foot.'+suf);return ob
    shoe('Sneaker sole',[(-.185,.052,.005,.012),(-.175,.052,.047,.020),(-.133,.052,.074,.022),(-.035,.055,.073,.025),(.055,.06,.06,.024),(.087,.06,.046,.017),(.095,.06,.008,.012)],white)
    shoe('Sneaker canvas upper',[(-.175,.076,.006,.007),(-.15,.090,.058,.025),(-.09,.105,.068,.036),(-.032,.130,.064,.055),(.034,.133,.059,.060),(.075,.126,.047,.046),(.084,.12,.004,.025)],navy)
    shoe('White toe cap',[(-.18,.070,.005,.011),(-.16,.079,.051,.022),(-.136,.082,.067,.024),(-.117,.083,.07,.026)],white)
    skin(box('R2 | sneaker tongue.'+suf,(x,-.025,.182),(.075,.084,.015),navy,.01),'foot.'+suf)
    for dx in [-.044,.044]:ribbon('Lace stay.'+suf,[(x+dx,-.087,.141),(x+dx,-.039,.17),(x+dx,.009,.19)],.009,trim,'foot.'+suf)
    for i in range(5):
        y=-.082+i*.019;z=.145+i*.010
        for ss in [-1,1]:skin(line('R2 | woven lace.'+suf,[(x+ss*.039,y,z),(x,y+.01,z+.006),(x-ss*.037,y+.019,z+.01)],.002,white),'foot.'+suf)
    skin(box('R2 | heel pull tab.'+suf,(x,.085,.155),(.022,.01,.047),white,.003),'foot.'+suf)
# Flowing hair roots now begin within the crown and taper at both ends.
def lock(name,points,width,depth,bone,u_offset=0):
    ps=[Vector(p) for p in points];vs=[];fs=[];UV=[];NR=32;NS=12
    for j in range(NR+1):
        t=j/NR;p=(1-t)**3*ps[0]+3*(1-t)**2*t*ps[1]+3*(1-t)*t*t*ps[2]+t**3*ps[3];w=width*(math.sin(math.pi*t)**.6)+.0001;dep=depth*(math.sin(math.pi*t)**.65)+.0001
        for i in range(NS):
            a=i*math.tau/NS;vs.append(p+Vector((w*math.cos(a),dep*math.sin(a),0)));UV.append((.09+u_offset+.068*math.cos(a),.31+.6*(1-t)))
    for j in range(NR):
        for i in range(NS):fs.append((j*NS+i,j*NS+(i+1)%NS,(j+1)*NS+(i+1)%NS,(j+1)*NS+i))
    ob=mesh('R2 | '+name,vs,fs,hairmat,True);uv=ob.data.uv_layers.new()
    for l in ob.data.loops:uv.data[l.index].uv=UV[l.vertex_index]
    return skin(ob,bone)
for sign,suf in [(1,'L'),(-1,'R')]:
    lock('Layered front hair.'+suf,[(sign*.18,-.07,2.095),(sign*.345,-.145,1.91),(sign*.268,-.179,1.43),(sign*.355,-.105,1.26)],.053,.019,'hair.'+suf)
    lock('Layered outer hair.'+suf,[(sign*.225,.075,2.075),(sign*.375,.015,1.82),(sign*.325,.025,1.30),(sign*.401,.10,1.37)],.075,.023,'hair.'+suf,.025)
    lock('Swept back hair.'+suf,[(sign*.16,.215,1.999),(sign*.245,.325,1.60),(sign*.51,.32,1.09),(sign*.36,.30,1.02)],.099,.024,'hair.back',.035)
for i,x in enumerate([-.18,-.09,0,.09,.18]):lock('Layered back hair %d'%i,[(x*.6,.21,2.04),(x,.31,1.63),(x*1.4,.30,1.25),(x*1.4+.024,.20,1.08+abs(x)*.3)],.048,.015,'hair.back',.012*i)
# Light inverted hulls bring the new shapes into the same visual language as the reference.
def outline(ob,thickness):
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    cp=ob.copy();cp.data=ob.data.copy();cp.name=ob.name+' | ink edge';COLL.objects.link(cp)
    # Cached vertex normals are evaluated before reversing winding.
    normals=[v.normal.copy() for v in cp.data.vertices]
    for v,norm in zip(cp.data.vertices,normals):v.co+=norm*thickness
    bm=bmesh.new();bm.from_mesh(cp.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(cp.data);bm.free();cp.data.materials.clear();cp.data.materials.append(ink)
    for p in cp.data.polygons:p.material_index=0
    return cp
outline_prefixes=['R2 | Tailored','R2 | shaped sleeve','R2 | Layered','R2 | Swept','R2 | Bag | structured','R2 | Sneaker canvas']
for ob in list(COLL.objects):
    if ob.type=='MESH' and any(ob.name.startswith(prefix) for prefix in outline_prefixes):outline(ob,.0014)
scene.frame_set(16)
scene.camera=bpy.data.objects['Camera | classroom overview']
bpy.ops.wm.save_as_mainfile(filepath=str(REV/'Classroom-refined.blend'))
result={'sportswear_refined':True,'rig':rig.name,'visible_character_meshes':len([o for o in COLL.objects if o.type=='MESH']),'file':bpy.data.filepath}


