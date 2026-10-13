# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

# Inspect the original cap's front surface where the band needs to sit.
import bpy,json
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from pathlib import Path
p=project_path('revision')
o=bpy.data.objects['R3 | Hair | continuous long silhouette'];b=BVHTree.FromPolygons([v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons]);data=[]
for x in [0,.05,.10,.15,.20,.23,.25,.27]:
 row=[]
 for z in [1.82,1.87,1.92,1.95,1.98,2.,2.02,2.04]:
  q,n,i,d=b.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2);row.append([z,round(q.y,4) if q else None])
 data.append([x,row])
result={'surface':data}
