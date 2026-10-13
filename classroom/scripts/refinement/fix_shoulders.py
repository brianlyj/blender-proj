# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

exec(compile(open(str(project_path('helpers.py')),encoding='utf-8-sig').read(),'helpers.py','exec'))
import bmesh
REV=ROOT/'revision';s=bpy.context.scene;rig=bpy.data.objects['MARI | refined character rig'];COLL=bpy.data.collections['05 Character | refined sports outfit']
bpy.ops.wm.save_as_mainfile(filepath=str(REV/'Classroom-before-dance.blend'),copy=True)
white=bpy.data.materials['R2 | Character | white sports fabric']
for o in list(COLL.objects):
 if o.name.startswith(('R2 | shaped sleeve with elbow folds','R4 | Connected sleeve')):bpy.data.objects.remove(o,do_unlink=True)
# One continuous capped mesh runs from an anchored fabric gusset to each cuff.
for sign,suf in [(1,'L'),(-1,'R')]:
 a=rig.data.bones['upper_arm.'+suf].head_local.copy();b=rig.data.bones['forearm.'+suf].head_local.copy();c=rig.data.bones['hand.'+suf].head_local.copy()
 vs=[];fs=[];weights=[];NS=32
 shoulder_rings=[(Vector((sign*.112,0,1.411)),.054,0),(Vector((sign*.135,0,1.41)),.074,.12),(Vector((sign*.162,0,1.407)),.09,.40),(a,.096,.72)]
 d=(b-a).normalized();q=d.to_track_quat('Z','Y')
 for p,r,w in shoulder_rings:
  for i in range(NS):ang=i*math.tau/NS;vs.append(p+q@Vector((r*math.cos(ang),r*math.sin(ang),0)))
  weights.append((1-w,w,0))
 NR=33
 for j in range(1,NR):
  t=j/(NR-1);p=a.lerp(b,t/.56) if t<=.56 else b.lerp(c,(t-.56)/.44);d=(b-a if t<.56 else c-b).normalized();q=d.to_track_quat('Z','Y');radius=.096+.038*math.sin(t*math.pi)-.017*t
  for i in range(NS):
   ang=i*math.tau/NS;fold=.006*math.cos(ang*5+t*7)*(math.exp(-((t-.61)/.17)**2)+.45*math.exp(-((t-.88)/.10)**2));vs.append(p+q@Vector(((radius+fold)*math.cos(ang),(radius+fold)*math.sin(ang),0)))
  wfore=max(0,min(1,(t-.44)/.24));wbody=.28*(1-min(1,t/.16))**2;weights.append((wbody,(1-wbody)*(1-wfore),(1-wbody)*wfore))
 rings=len(weights)
 for j in range(rings-1):
  for i in range(NS):fs.append((j*NS+i,j*NS+(i+1)%NS,(j+1)*NS+(i+1)%NS,(j+1)*NS+i))
 fs.append(tuple(reversed(range(NS))))
 o=mesh('R4 | Connected sleeve and shoulder.'+suf,vs,fs,white,True);o.parent=rig
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 gs=[o.vertex_groups.new(name=n) for n in ['chest','upper_arm.'+suf,'forearm.'+suf]]
 for j,ws in enumerate(weights):
  ids=list(range(j*NS,(j+1)*NS))
  for g,w in zip(gs,ws):
   if w:g.add(ids,w,'REPLACE')
 m=o.modifiers.new('Blended shoulder and arm deformation','ARMATURE');m.object=rig;m.use_deform_preserve_volume=True;m=o.modifiers.new('Smooth continuous fabric','SUBSURF');m.levels=1;m.render_levels=2
# Free both hands for the clasp and dance; retain the bottle as a classroom prop.
bottles=[o for o in COLL.objects if o.name.startswith(('R2 | Water bottle','R2 | Bottle '))]
if bottles:
 dg=bpy.context.evaluated_depsgraph_get();props=bpy.data.collections.get('06 Dance props') or collection('06 Dance props',s);new=[]
 for o in bottles:
  me=bpy.data.meshes.new_from_object(o.evaluated_get(dg));me.transform(o.matrix_world);cp=bpy.data.objects.new('Dance prop | '+o.name[5:],me);props.objects.link(cp);new.append(cp)
  bpy.data.objects.remove(o,do_unlink=True)
 lo=Vector([min(v.co[k] for ob in new for v in ob.data.vertices) for k in range(3)]);hi=Vector([max(v.co[k] for ob in new for v in ob.data.vertices) for k in range(3)]);delta=Vector((-.4,3.67,1.05))-Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
 for o in new:o.data.transform(Matrix.Translation(delta))
bpy.ops.wm.save_as_mainfile(filepath=str(REV/'Classroom-dance.blend'))
result={'continuous_shoulders':True,'bottle_on_desk':len(bottles),'saved':bpy.data.filepath}
