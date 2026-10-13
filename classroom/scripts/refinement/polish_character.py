# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

exec(compile(open(str(project_path('helpers.py')),encoding='utf-8-sig').read(),'helpers.py','exec'))
import bmesh
REV=ROOT/'revision';s=bpy.context.scene;rig=bpy.data.objects['MARI | refined character rig'];COLL=bpy.data.collections['05 Character | refined sports outfit'];skinmat=bpy.data.materials['R2 | Character | peach skin']
# Move the hair ornament onto the visible hair surface.
for ob in COLL.objects:
    if ob.type=='MESH' and any(ob.name.startswith('R2 | '+p) for p in ['flower petal','golden flower center','floral leaf']):
        for v in ob.data.vertices:v.co.y-=.093
# More vivid apricot shading while retaining the supplied painted map.
hair=bpy.data.objects['R2 | Hair | textured crown and fringe'].data.materials[0]
nt=hair.node_tree
for tex in [n for n in nt.nodes if n.type=='TEX_IMAGE']:
    links=[l for l in nt.links if l.from_node==tex and l.from_socket.name=='Color']
    if links:
        hs=nt.nodes.new('ShaderNodeHueSaturation');hs.inputs['Saturation'].default_value=1.3;hs.inputs['Value'].default_value=1.12
        for link in links:nt.links.new(hs.outputs['Color'],link.to_socket)
        nt.links.new(tex.outputs['Color'],hs.inputs['Color'])
# Correct finger placement: fingers spread across the palm, not through its depth.
for ob in list(COLL.objects):
    if ob.type=='MESH' and any(ob.name.startswith('R2 | '+p) for p in ['index ','middle ','ring ','pinky ','Thumb ']):bpy.data.objects.remove(ob,do_unlink=True)
rest={}
for sign,suf in [(1,'L'),(-1,'R')]:
    hb=rig.data.bones['hand.'+suf];wr=hb.head_local.copy();ht=hb.tail_local.copy();d=(ht-wr).normalized();across=d.cross(Vector((0,1,0))).normalized()
    for i,(name,length) in enumerate([('index',.055),('middle',.062),('ring',.055),('pinky',.042)]):
        a=ht-d*.012+across*(i-1.5)*.017;b=a+d*length*.54;c=a+d*length
        rest[(suf,name)]=(a,b,c,.0085 if name!='pinky' else .007)
    a=wr+d*.042-across*sign*.028;b=a-across*sign*.023+d*.018;c=b+d*.032
    rest[(suf,'thumb')]=(a,b,c,.0105)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for (suf,name),(a,b,c,r) in rest.items():
    e=rig.data.edit_bones[name+'.01.'+suf];e.head=a;e.tail=b;e=rig.data.edit_bones[name+'.02.'+suf];e.head=b;e.tail=c
bpy.ops.object.mode_set(mode='OBJECT')
for (suf,name),(a,b,c,r) in rest.items():
    vs=[];fs=[];NS=12;NR=9
    for j in range(NR):
        t=j/(NR-1);p=a.lerp(c,t);d=(c-a).normalized();q=d.to_track_quat('Z','Y');rad=r*(.92-.2*t)*min(1,(1-t)*8+.08)
        for i in range(NS):vs.append(p+q@Vector((rad*math.cos(i*math.tau/NS),rad*math.sin(i*math.tau/NS),0)))
    for j in range(NR-1):
        for i in range(NS):fs.append((j*NS+i,j*NS+(i+1)%NS,(j+1)*NS+(i+1)%NS,(j+1)*NS+i))
    fs.append(tuple(range((NR-1)*NS,NR*NS)))
    ob=mesh('R2 | articulated '+name+'.'+suf,vs,fs,skinmat,True);ob.parent=rig;g1=ob.vertex_groups.new(name=name+'.01.'+suf);g2=ob.vertex_groups.new(name=name+'.02.'+suf)
    for j in range(NR):
        w=max(0,min(1,(j/(NR-1)-.42)/.23));ids=list(range(j*NS,(j+1)*NS));g1.add(ids,1-w,'REPLACE');g2.add(ids,w,'REPLACE')
    m=ob.modifiers.new('Individual finger skin','ARMATURE');m.object=rig;m.use_deform_preserve_volume=True
    m=ob.modifiers.new('Smooth fingers','SUBSURF');m.levels=1;m.render_levels=2
# Make toe controls deform the newly built footwear.
for ob in list(COLL.objects):
    if ob.type=='MESH' and any(ob.name.startswith('R2 | '+p) for p in ['Sneaker','White toe cap','sneaker tongue','Lace stay','woven lace','heel pull']):
        suffix='L' if ob.vertex_groups.get('foot.L') else 'R';fg=ob.vertex_groups.get('foot.'+suffix)
        if fg:
            tg=ob.vertex_groups.get('toe.'+suffix) or ob.vertex_groups.new(name='toe.'+suffix)
            for v in ob.data.vertices:
                w=max(0,min(1,(-v.co.y-.085)/.10));fg.add([v.index],1-w,'REPLACE');tg.add([v.index],w,'REPLACE')
s.frame_set(16)
for ob in bpy.context.selected_objects:ob.select_set(False)
bpy.ops.wm.save_as_mainfile(filepath=str(REV/'Classroom-refined.blend'))
result={'fingers':'individually skinned and corrected','toe_controls':'weighted','file':bpy.data.filepath}
