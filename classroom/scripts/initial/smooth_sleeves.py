# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

exec(compile(open(str(project_path('helpers.py')),encoding='utf-8-sig').read(),'helpers.py','exec'))
scene=bpy.context.scene;rig=bpy.data.objects['CHARACTER_RIG | select to pose'];COLL=bpy.data.collections['05 Character | reference-inspired']
for suffix in ['L','R']:
    for prefix in ['Puffy sleeve upper.','Soft sleeve shoulder.','Sleeve elbow fold.','Bell sleeve forearm.']:
        ob=bpy.data.objects.get(prefix+suffix)
        if ob and ob.parent==rig:bpy.data.objects.remove(ob,do_unlink=True)
    a=rig.data.bones['upper_arm.'+suffix].head_local.copy();b=rig.data.bones['forearm.'+suffix].head_local.copy();c=rig.data.bones['hand.'+suffix].head_local.copy()
    verts=[];faces=[];weights=[];n=24
    for j in range(17):
        t=j/16
        if t<=.56:p=a.lerp(b,t/.56);d=(b-a).normalized()
        else:p=b.lerp(c,(t-.56)/.44);d=(c-b).normalized()
        q=d.to_track_quat('Z','Y');r=.103+math.sin(t*math.pi)*.010-.021*t
        for i in range(n):verts.append(p+q@Vector((r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),0)))
        weights.append(max(0,min(1,(t-.45)/.22)))
    for j in range(16):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple(range(16*n,17*n))])
    ob=mesh('Continuous sports sleeve.'+suffix,verts,faces,bpy.data.materials['Character | white sports fabric'],True);ob.parent=rig
    g1=ob.vertex_groups.new(name='upper_arm.'+suffix);g2=ob.vertex_groups.new(name='forearm.'+suffix)
    for j,w in enumerate(weights):g1.add(list(range(j*n,(j+1)*n)),1-w,'REPLACE');g2.add(list(range(j*n,(j+1)*n)),w,'REPLACE')
    m=ob.modifiers.new('Character skin deformation','ARMATURE');m.object=rig;m.use_deform_preserve_volume=True
    m=ob.modifiers.new('Soft cloth silhouette','SUBSURF');m.levels=2;m.render_levels=2
cam=bpy.data.objects['Camera | character portrait'];cam.location=(2.15,.02,1.80);target=Vector((1.35,3.23,1.40));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=34
scene.frame_set(16)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Classroom.blend'))
result={'sleeves':'continuous weighted cloth','character_meshes':len([o for o in rig.children if o.type=='MESH'])}
