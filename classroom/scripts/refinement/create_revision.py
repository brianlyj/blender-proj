# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

exec(compile(open(str(project_path('helpers.py')),encoding='utf-8-sig').read(),'helpers.py','exec'))
import bmesh,json
REV=ROOT/'revision';scene=bpy.context.scene
# Save the user's current live scene, including any viewport or pose edits, before refining.
if not (REV/'Classroom-before-refinement.blend').exists():bpy.ops.wm.save_as_mainfile(filepath=str(REV/'Classroom-before-refinement.blend'),copy=True)
partial=bpy.data.collections.get('05 Character | refined sports outfit')
if partial:
    for ob in list(partial.objects):bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.collections.remove(partial)
oldrig=bpy.data.objects['CHARACTER_RIG | select to pose'];oldcoll=bpy.data.collections['05 Character | reference-inspired']
COLL=collection('05 Character | refined sports outfit',scene)
rig=oldrig.copy();rig.data=oldrig.data.copy();rig.name='MARI | refined character rig';COLL.objects.link(rig)
if rig.animation_data and rig.animation_data.action:rig.animation_data.action=rig.animation_data.action.copy()
# Preserve the original version in its disabled collection.
oldcoll.hide_render=True;oldcoll.hide_viewport=True
keep=[]
for ob in list(oldrig.children):
    if ob.type!='MESH':continue
    groups={g.name for g in ob.vertex_groups}
    if groups & {'head','hair.L','hair.R','hair.back','ear.L','ear.R','halo'}:continue
    cp=ob.copy();cp.data=ob.data.copy();cp.name='R2 | '+ob.name;COLL.objects.link(cp);cp.parent=rig
    for m in cp.modifiers:
        if m.type=='ARMATURE':m.object=rig
    keep.append(cp)
# Restrained cel palette for the sports outfit.
def toon(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes;n.clear();links=m.node_tree.links
    d=n.new('ShaderNodeBsdfDiffuse');d.inputs['Color'].default_value=(.7,.7,.7,1)
    rgb=n.new('ShaderNodeShaderToRGB');links.new(d.outputs[0],rgb.inputs[0])
    ramp=n.new('ShaderNodeValToRGB');r=ramp.color_ramp;r.interpolation='EASE';r.elements.remove(r.elements[1])
    for index,(pos,factor) in enumerate([(0,.58),(.35,.78),(.75,.93),(1.2,1)]):
        e=r.elements[0] if index==0 else r.elements.new(min(pos,1));e.position=min(pos,1);e.color=tuple(min(1,c*factor) for c in color)+(1,)
    links.new(rgb.outputs[0],ramp.inputs[0]);em=n.new('ShaderNodeEmission');links.new(ramp.outputs[0],em.inputs[0]);out=n.new('ShaderNodeOutputMaterial');links.new(em.outputs[0],out.inputs['Surface']);return m
palette={
 'Character | peach skin':(.99,.80,.74),'Character | white sports fabric':(.93,.95,1.0),'Character | charcoal violet fabric':(.09,.11,.19),'Character | pale piping':(.71,.76,.88),'Character | shoe sole':(.79,.82,.92),'Character | cream strap':(.77,.73,.57),'Character | bottle translucent blue':(.26,.58,.73),
}
matmap={name:toon('R2 | '+name,c) for name,c in palette.items()}
for ob in keep:
    for i,m in enumerate(ob.data.materials):
        if m and m.name in matmap:ob.data.materials[i]=matmap[m.name]
# Use the provided, textured facial and upper-hair meshes; discard the idol outfit and pigtails.
source_names=['Object_4','Object_5','Object_6','Object_7','Object_8','Object_10','Object_12']
with bpy.data.libraries.load(str(REV/'Reference-inspection.blend'),link=False) as (src,dst):dst.objects=source_names.copy()
components=json.loads((REV/'components.json').read_text())
imported={}
T=Matrix.Translation((0,0,.40))@Matrix.Diagonal((.80,.75,.84,1))
labels={'Object_4':'Eyes | textured anime','Object_5':'Eyebrows','Object_6':'Face | sculpted anime','Object_7':'Hair | textured crown and fringe','Object_8':'Halo | reference motif','Object_10':'Mouth | soft smile','Object_12':'Hair | fine outline'}
for source_name,ob in zip(source_names,dst.objects):
    ob.parent=None;ob.matrix_world=Matrix.Identity(4);COLL.objects.link(ob)
    if source_name in ['Object_7','Object_12']:
        allowed=set(components[source_name][0]['vertex_ids']);bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in allowed],context='VERTS');bm.to_mesh(ob.data);bm.free()
    ob.data.transform(T);ob.name='R2 | '+labels[source_name];ob.parent=rig
    g=ob.vertex_groups.new(name='halo' if source_name=='Object_8' else 'head');g.add(list(range(len(ob.data.vertices))),1,'REPLACE')
    mod=ob.modifiers.new('Skin to full body rig','ARMATURE');mod.object=rig
    imported[source_name]=ob
# Source eye whites/irises get a blink shape; flatten along the true eye center.
eye=imported['Object_4'];eye.shape_key_add(name='Basis');key=eye.shape_key_add(name='Blink')
for v in key.data:
    center=1.686;v.co.z=center+(v.co.z-center)*.025
for f,val in [(1,0),(36,0),(39,1),(42,0),(91,0),(94,1),(97,0),(120,0)]:key.value=val;key.keyframe_insert(data_path='value',frame=f)
# Skinned detail helpers. Everything is built in the rig's local rest coordinates.
def skin(ob,bone):
    if ob.type!='MESH':
        dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));copy=bpy.data.objects.new(ob.name,me);COLL.objects.link(copy);copy.matrix_world=ob.matrix_world.copy();bpy.data.objects.remove(ob,do_unlink=True);ob=copy
    ob.data.transform(Matrix.LocRotScale(ob.location,ob.rotation_euler.to_quaternion(),ob.scale));ob.matrix_world=Matrix.Identity(4);ob.parent=rig
    g=ob.vertex_groups.new(name=bone);g.add(list(range(len(ob.data.vertices))),1,'REPLACE');mod=ob.modifiers.new('Skin to full body rig','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True;return ob
hairmat=imported['Object_7'].data.materials[0]
white=matmap['Character | white sports fabric'];pink=toon('R2 | ear rose',(.90,.53,.50));orange=toon('R2 | ear apricot',(1,.64,.36));fur=toon('R2 | ear fur',(1,.95,.87));leafmat=toon('R2 | clip leaves',(.16,.39,.33));lilac=toon('R2 | clip petals',(.66,.63,.84));gold=toon('R2 | warm metal',(.92,.77,.4))
# Long tapered, textured hair ribbons. Unlike the first blockout, each lock ends in a curved sharp tip.
def lock(name,p0,p1,p2,p3,width,depth,bone):
    ps=[Vector(p) for p in [p0,p1,p2,p3]];vs=[];fs=[];UV=[];nr=24;ns=12
    for j in range(nr+1):
        t=j/nr;p=(1-t)**3*ps[0]+3*(1-t)**2*t*ps[1]+3*(1-t)*t*t*ps[2]+t**3*ps[3]
        w=width*(.65+.5*math.sin(t*math.pi))*(1-t)**.55+.0003
        for i in range(ns):
            a=i*math.tau/ns;vs.append(p+Vector((w*math.cos(a),depth*(1-t)**.5*math.sin(a),0)));UV.append((.09+.065*math.cos(a),.31+.58*(1-t)))
    for j in range(nr):
        for i in range(ns):fs.append((j*ns+i,j*ns+(i+1)%ns,(j+1)*ns+(i+1)%ns,(j+1)*ns+i))
    ob=mesh('R2 | '+name,vs,fs,hairmat,True);uv=ob.data.uv_layers.new(name='Painted hair shading')
    for loop in ob.data.loops:uv.data[loop.index].uv=UV[loop.vertex_index]
    skin(ob,bone);return ob
for s,suf in [(1,'L'),(-1,'R')]:
    lock('Long face-framing lock.'+suf,(s*.248,-.08,1.92),(s*.32,-.19,1.65),(s*.29,-.16,1.32),(s*.365,-.09,1.24),.066,.025,'hair.'+suf)
    lock('Side hair layer.'+suf,(s*.277,.055,1.89),(s*.35,-.02,1.66),(s*.33,.045,1.30),(s*.43,.06,1.36),.074,.031,'hair.'+suf)
    lock('Back outer sweep.'+suf,(s*.20,.21,1.82),(s*.29,.28,1.50),(s*.49,.30,1.09),(s*.38,.31,1.03),.108,.027,'hair.back')
for i,x in enumerate([-.18,-.09,0,.09,.18]):lock('Back hair layer %d'%i,(x,.24,1.84),(x*1.05,.29,1.53),(x*1.4,.32,1.23),(x*1.4+.025,.25,1.07+abs(x)*.3),.064,.021,'hair.back')
# Curved ears with inset pink and irregular fur edges.
for s,suf in [(1,'L'),(-1,'R')]:
    verts=[(s*.162,.024,1.992),(s*.306,.041,2.012),(s*.275,.051,2.274),(s*.215,-.018,2.075),(s*.178,.088,2.018),(s*.282,.102,2.04)]
    ob=mesh('R2 | sculpted ear.'+suf,verts,[(0,1,3),(1,2,3),(2,0,3),(0,4,5,1),(4,2,5),(5,2,1),(4,0,2)],orange,True);skin(ob,'ear.'+suf)
    ob=mesh('R2 | inner ear.'+suf,[(s*.184,-.004,2.037),(s*.273,.013,2.06),(s*.269,.035,2.224)],[(0,1,2)],pink);skin(ob,'ear.'+suf)
    coords=[(.177,2.028),(.188,2.098),(.20,2.079),(.219,2.145),(.231,2.129),(.253,2.197),(.269,2.064),(.252,2.034)]
    ob=mesh('R2 | pointed white ear fur.'+suf,[(s*x,-.021+(z-2.03)*.22,z) for x,z in coords],[tuple(range(len(coords)))],fur);skin(ob,'ear.'+suf)
# Satin headband, modeled as a flat strip rather than a round tube.
vs=[]
for j in range(25):
    a=-1.18+j/24*2.36;x=.292*math.sin(a);z=1.84+.244*math.cos(a);y=-.065-.092*math.cos(a)
    vs.extend([(x,y-.008,z-.014),(x,y+.015,z+.017)])
ob=mesh('R2 | satin headband',vs,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(24)],white,True);so=ob.modifiers.new('Satin thickness','SOLIDIFY');so.thickness=.003;skin(ob,'head')
# Fine floral hair pin.
for i in range(3):
    cx=-.234+(i%2)*.018;cz=1.903+(i-1)*.041
    for j in range(5):
        a=j*math.tau/5;ob=ellipsoid('R2 | flower petal',(cx+.019*math.cos(a),-.167,cz+.019*math.sin(a)),(.014,.004,.012),white if i!=1 else lilac,16,10);skin(ob,'head')
    skin(ellipsoid('R2 | golden flower center',(cx,-.174,cz),(.005,.003,.005),gold,12,8),'head')
for i in range(3):
    ob=ellipsoid('R2 | floral leaf',(-.273-i*.008,-.133,1.94+i*.019),(.014,.005,.034),leafmat,16,10);ob.rotation_euler[1]=-.55;skin(ob,'head')
# Pack attribution and all textures in the editable deliverable.
credit=bpy.data.texts.new('ASSET CREDIT | supplied model')
credit.write('Face, eyes, upper hair and halo adapted from the user-supplied asset:\n[Blue Archive] -Mari (Idol)- | Chibi + Stage\nAuthor: VuckyZ / VückyZ\nSource: https://sketchfab.com/3d-models/blue-archive-mari-idol-chibi-stage-7412827541324d13a557d2f4a7f8d3c4\nLicense indicated in GLB metadata: CC BY 4.0\nhttps://creativecommons.org/licenses/by/4.0/\nChanges: idol outfit/stage removed; head scaled and skinned; new sports outfit detailing, long hair, ears, headband, floral pin, rig and animation.\n')
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file:
        try:im.pack()
        except RuntimeError:pass
scene.frame_set(16)
scene.camera=bpy.data.objects['Camera | classroom overview']
bpy.ops.wm.save_as_mainfile(filepath=str(REV/'Classroom-refined.blend'))
result={'new_rig':rig.name,'imported_details':list(labels.values()),'preserved_original':True,'file':bpy.data.filepath}


