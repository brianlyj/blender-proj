# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

exec(compile(open(str(project_path('helpers.py')),encoding='utf-8-sig').read(),'helpers.py','exec'))
import bmesh,json
from mathutils.bvhtree import BVHTree
REV=ROOT/'revision';scene=bpy.context.scene;rig=bpy.data.objects['MARI | refined character rig'];COLL=bpy.data.collections['05 Character | refined sports outfit']
if not (REV/'Classroom-before-head-correction.blend').exists():bpy.ops.wm.save_as_mainfile(filepath=str(REV/'Classroom-before-head-correction.blend'),copy=True)
# Replace the incompatible added crown pieces; retain the rest of the completed character.
prefixes=['R2 | Layered','R2 | Swept','R2 | sculpted ear','R2 | inner ear','R2 | pointed white ear fur','R2 | satin headband','R2 | flower petal','R2 | golden flower center','R2 | floral leaf','R3 |']
for o in list(COLL.objects):
 if any(o.name.startswith(p) for p in prefixes) or o.name in ['R2 | Hair | textured crown and fringe','R2 | Hair | fine outline']:bpy.data.objects.remove(o,do_unlink=True)
components=json.loads((REV/'components.json').read_text())
T=Matrix.Translation((0,0,.40))@Matrix.Diagonal((.80,.75,.84,1))
white=bpy.data.materials['R2 | Character | white sports fabric'];gold=bpy.data.materials['R2 | warm metal'];lilac=bpy.data.materials['R2 | clip petals'];green=bpy.data.materials['R2 | clip leaves']

def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)

def skin(ob,bone='head',hair=False):
 if ob.type!='MESH':
  dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));cp=bpy.data.objects.new(ob.name,me);COLL.objects.link(cp);cp.matrix_world=ob.matrix_world.copy();bpy.data.objects.remove(ob,do_unlink=True);ob=cp
 ob.data.transform(Matrix.LocRotScale(ob.location,ob.rotation_euler.to_quaternion(),ob.scale));ob.matrix_world=Matrix.Identity(4);ob.parent=rig
 ob.vertex_groups.clear()
 if hair:
  gs={n:ob.vertex_groups.new(name=n) for n in ['head','hair.L','hair.R','hair.back']}
  for v in ob.data.vertices:
   w=(1-smooth(1.42,1.90,v.co.z))*.9;bn='hair.back' if v.co.y>.08 else ('hair.L' if v.co.x>0 else 'hair.R');gs['head'].add([v.index],1-w,'REPLACE');gs[bn].add([v.index],w,'REPLACE')
 else:ob.vertex_groups.new(name=bone).add(list(range(len(ob.data.vertices))),1,'REPLACE')
 mod=ob.modifiers.new('Character skin','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True;return ob

def source_part(objname,ids,label):
 with bpy.data.libraries.load(str(REV/'Reference-inspection.blend'),link=False) as (src,dst):dst.objects=[objname]
 ob=dst.objects[0];ob.parent=None;ob.matrix_world=Matrix.Identity(4);COLL.objects.link(ob)
 allowed=set(i for c in components[objname] if c['id'] in ids for i in c['vertex_ids'])
 bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in allowed],context='VERTS');bm.to_mesh(ob.data);bm.free()
 ob.data.transform(T);ob.name=label;return ob
# Extend the original sculpted silhouette itself. Roots and fringe remain continuous.
def extend_hair(v):
 x,y,z=v;back=smooth(.015,.16,y);weight=back
 fall=max(0,min(1,(1.88-z)/.35))**1.55
 slim=(1-smooth(1.60,1.98,z))*back
 return Vector((x*(1-.26*slim)+.010*fall*back,.06+(y-.06)*(1-.18*slim)+.02*fall*back,z-.405*fall*weight))
cap=source_part('Object_7',[0],'R3 | Hair | continuous long silhouette')
for v in cap.data.vertices:v.co=extend_hair(v.co)
hairmat=cap.data.materials[0]
# Keep the original painted palette. No stacked HSV adjustments.
skin(cap,hair=True)
edge=source_part('Object_12',[0],'R3 | Hair | fine contour')
for v in edge.data.vertices:v.co=extend_hair(v.co)
skin(edge,hair=True)
# Close the former idol-band opening with its precisely fitted source surface.
fill=source_part('Object_3',[27],'R3 | Hair | crown infill');fill.data.materials.clear();fill.data.materials.append(hairmat)
for p in fill.data.polygons:p.material_index=0
for u in fill.data.uv_layers.active.data:u.uv=(.11,.72)
skin(fill)
# A real fitted fabric strip: cast onto both the sculpted cap and the filled opening.
verts=[v.co.copy() for v in cap.data.vertices]+[v.co.copy() for v in fill.data.vertices]
faces=[tuple(p.vertices) for p in cap.data.polygons]+[tuple(i+len(cap.data.vertices) for i in p.vertices) for p in fill.data.polygons]
bvh=BVHTree.FromPolygons(verts,faces)
def surface(x,z):
 p,n,idx,d=bvh.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2)
 if p is None:
  p,n,idx,d=bvh.find_nearest(Vector((x,-.12,z)))
 return Vector((x,p.y-.0035,z))
vs=[];fs=[];N=64;W=6
for j in range(N+1):
 x=-.231+.462*j/N;f=abs(x)/.231;cz=1.985-.125*f*f;width=.054-.028*f**3
 for k in range(W+1):
  z=cz+(k/W-.5)*width;p=surface(x,z)
  if p.y>-.06:p.y=-.203+.37*(z-1.96)+1.48*x*x
  vs.append(p)
# Filter minor facets while keeping the cloth in front of the surface.
for iteration in range(4):
 old=[v.copy() for v in vs]
 for j in range(1,N):
  for k in range(W+1):
   i=j*(W+1)+k;avg=(old[i-(W+1)].y+old[i].y*2+old[i+(W+1)].y)/4
   vs[i].y=min(avg,old[i].y)
for v in vs:v.y-=.002
for j in range(N):
 for k in range(W):i=j*(W+1)+k;fs.append((i,i+1,i+W+2,i+W+1))
band=mesh('R3 | Headband | fitted white satin',vs,fs,white,True);solid=band.modifiers.new('Woven thickness','SOLIDIFY');solid.thickness=.002;skin(band)
# Use the supplied model's rounded ear shells and inset fur, mirrored to a balanced pair.
for sign,suf in [(1,'L'),(-1,'R')]:
 for obj,ids,label in [('Object_3',[12,18],'Ear | shaped shell and fur'),('Object_11',[17,19],'Ear | fine contour')]:
  o=source_part(obj,ids,'R3 | '+label+'.'+suf)
  for v in o.data.vertices:
   v.co.x=(.20+(v.co.x+.025-.20)*.84)*sign;v.co.z=2.0+(v.co.z+.045-2.0)*.86;v.co.y+=.055
  if sign<0:
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  skin(o,'ear.'+suf)
# Light tapered wisps emerge below the continuous side hair, with roots held to the head.
def wisp(name,ps,width):
 ps=list(map(Vector,ps));vs=[];fs=[];uv=[];N=28;K=12
 for j in range(N+1):
  t=j/N;p=(1-t)**3*ps[0]+3*(1-t)**2*t*ps[1]+3*(1-t)*t*t*ps[2]+t**3*ps[3]
  w=width*(.09+.91*math.sin(math.pi*t)**.7)*(1-t)**.25+.00005
  for k in range(K):
   a=k*math.tau/K;vs.append(p+Vector((w*math.cos(a),.018*math.sin(math.pi*t)**.65*math.sin(a),0)));uv.append((.105+.022*math.cos(a),.61+.19*(1-t)))
 for j in range(N):
  for k in range(K):fs.append((j*K+k,j*K+(k+1)%K,(j+1)*K+(k+1)%K,(j+1)*K+k))
 o=mesh('R3 | Hair | '+name,vs,fs,hairmat,True);u=o.data.uv_layers.new()
 for l in o.data.loops:u.data[l.index].uv=uv[l.vertex_index]
 return skin(o,hair=True)
for sign,suf in [(1,'L'),(-1,'R')]:
 wisp('long side lock.'+suf,[(sign*.198,.025,1.94),(sign*.274,-.064,1.69),(sign*.248,-.075,1.36),(sign*.293,-.045,1.28)],.031)
 wisp('fine outer curl.'+suf,[(sign*.225,.13,1.88),(sign*.292,.155,1.58),(sign*.283,.19,1.30),(sign*.246,.19,1.21)],.023)
# Flowers and leaves now sit on the surface, not on a flat plane in front of it.
for i,(cx,cz,r) in enumerate([(-.213,1.906,.023),(-.237,1.857,.021),(-.241,1.951,.016)]):
 center=surface(cx,cz);center.y-=.007
 for j in range(5):
  a=j*math.tau/5;p=center+Vector((r*.63*math.cos(a),-.002,r*.63*math.sin(a)))
  skin(ellipsoid('R3 | Hairpin | petal',p,(r*.48,.0035,r*.43),white if i!=1 else lilac,16,10))
 skin(ellipsoid('R3 | Hairpin | gold center',center+Vector((0,-.008,0)),(.004,.003,.004),gold,12,8))
for x,z,tilt in [(-.266,1.925,-.6),(-.225,1.978,.5),(-.275,1.89,-.8)]:
 p=surface(x,z);p.y-=.003;o=ellipsoid('R3 | Hairpin | leaf',p,(.009,.003,.025),green,16,10);o.rotation_euler[1]=tilt;skin(o)
# The facial opening must close with the eye, otherwise blinking exposes the hollow head.
face=bpy.data.objects['R2 | Face | sculpted anime']
if not face.data.shape_keys:face.shape_key_add(name='Basis')
k=face.data.shape_keys.key_blocks.get('Blink') or face.shape_key_add(name='Blink')
for base,v in zip(face.data.shape_keys.key_blocks['Basis'].data,k.data):
 x,y,z=base.co;wx=smooth(.012,.038,abs(x))*(1-smooth(.174,.213,abs(x)));wz=smooth(1.607,1.635,z)*(1-smooth(1.747,1.79,z));wy=1-smooth(-.088,-.065,y);w=wx*wz*wy
 v.co=base.co;v.co.z=z+w*((1.686+(z-1.686)*.025)-z)
for f,val in [(1,0),(36,0),(39,1),(42,0),(91,0),(94,1),(97,0),(120,0)]:k.value=val;k.keyframe_insert(data_path='value',frame=f)
lashmat=mat('R3 | warm eyelash ink',(.10,.055,.038),1)
nt=lashmat.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(.10,.055,.038,1);nt.links.new(em.outputs[0],out.inputs[0])
for sign,suf in [(1,'L'),(-1,'R')]:
 pts=[]
 for j in range(13):
  t=j/12;x=.05+.117*t;pts.append((sign*x,-.166+.20*(x-.05),1.686-.005*math.sin(math.pi*t)+.004*t))
 o=skin(line('R3 | closed eyelash.'+suf,pts,.0019,lashmat))
 o.shape_key_add(name='Basis');key=o.shape_key_add(name='Blink lash')
 # Shape-key Basis lies safely behind the face; closure brings the lash to the skin.
 for v in o.data.shape_keys.key_blocks['Basis'].data:v.co.y+=.04
 for f,val in [(1,0),(37,0),(39,1),(41,0),(92,0),(94,1),(96,0),(120,0)]:key.value=val;key.keyframe_insert(data_path='value',frame=f)
scene.frame_set(16)
for o in bpy.context.selected_objects:o.select_set(False)
rig.select_set(True);bpy.context.view_layer.objects.active=rig
scene.camera=bpy.data.objects['Camera | character portrait']
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:
  try:im.pack()
  except RuntimeError:pass
bpy.ops.wm.save_as_mainfile(filepath=str(REV/'Classroom-refined.blend'))
result={'head_reworked':True,'fitted_band_vertices':len(band.data.vertices),'continuous_hair_vertices':len(cap.data.vertices),'file':bpy.data.filepath}
