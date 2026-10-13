# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy, math, random
from mathutils import Vector, Matrix
from pathlib import Path
ROOT = project_path('')
COLL = None

def collection(name, scene=None):
    c=bpy.data.collections.new(name)
    (scene or bpy.context.scene).collection.children.link(c)
    return c

def mat(name, color, rough=.5, metal=0, emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    if emission:
        bs.inputs['Emission Color'].default_value=(*color,1); bs.inputs['Emission Strength'].default_value=emission
    return m

def mesh(name, verts, faces, material, smooth=False):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); COLL.objects.link(ob)
    if material: me.materials.append(material)
    if smooth:
        for p in me.polygons:p.use_smooth=True
    return ob

def bevel(ob, amount=.025, seg=3):
    m=ob.modifiers.new('Soft crafted edges','BEVEL');m.width=amount;m.segments=seg
    return ob

def box(name, pos, size, material, rounded=.02):
    x,y,z=[v/2 for v in size]
    vs=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]
    ob=mesh(name,vs,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],material)
    ob.location=pos
    if rounded:bevel(ob,rounded)
    return ob

def ellipsoid(name, pos, size, material, seg=24, rings=14):
    vs=[];fs=[]
    for j in range(rings+1):
        t=math.pi*j/rings
        for i in range(seg):
            p=math.tau*i/seg
            vs.append((math.sin(t)*math.cos(p)*size[0],math.sin(t)*math.sin(p)*size[1],math.cos(t)*size[2]))
    for j in range(rings):
        for i in range(seg):fs.append((j*seg+i,j*seg+(i+1)%seg,(j+1)*seg+(i+1)%seg,(j+1)*seg+i))
    ob=mesh(name,vs,fs,material,True);ob.location=pos;return ob

def rod(name, a,b,r,material,r2=None,n=16):
    a=Vector(a);b=Vector(b);d=b-a;r2=r if r2 is None else r2
    q=d.to_track_quat('Z','Y');vs=[]
    for z,rr in [(0,r),(d.length,r2)]:
        for i in range(n):vs.append(q@Vector((rr*math.cos(math.tau*i/n),rr*math.sin(math.tau*i/n),z))+a)
    fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]
    fs.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    return mesh(name,vs,fs,material,True)

def line(name,points,r,material,cyclic=False):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=12
    sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    sp.use_cyclic_u=cyclic;cu.bevel_depth=r;cu.bevel_resolution=3
    ob=bpy.data.objects.new(name,cu);COLL.objects.link(ob);cu.materials.append(material);return ob

def text(name,body,pos,size,material,align='LEFT',rot=(math.pi/2,0,0)):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x=align;cu.extrude=.0006
    ob=bpy.data.objects.new(name,cu);COLL.objects.link(ob);ob.location=pos;ob.rotation_euler=rot;cu.materials.append(material);return ob

def camera(name,pos,target,lens=45,ortho=None):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);COLL.objects.link(o);o.location=pos
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens
    if ortho:d.type='ORTHO';d.ortho_scale=ortho
    return o

def area(name,pos,target,power,color,size):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);COLL.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
