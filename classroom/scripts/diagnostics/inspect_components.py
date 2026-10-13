# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy,json
from pathlib import Path
result={}
for name in ['Object_3','Object_7','Object_11','Object_12']:
    o=bpy.data.objects[name];me=o.data;p=list(range(len(me.vertices)))
    def find(x):
        while p[x]!=x:p[x]=p[p[x]];x=p[x]
        return x
    def union(a,b):p[find(a)]=find(b)
    coords={}
    for v in me.vertices:
        key=tuple(round(x,5) for x in v.co)
        if key in coords:union(v.index,coords[key])
        else:coords[key]=v.index
    for f in me.polygons:
        for i in f.vertices[1:]:union(f.vertices[0],i)
    groups={}
    for v in me.vertices:groups.setdefault(find(v.index),[]).append(v.index)
    out=[]
    for ix,ids in enumerate(sorted(groups.values(),key=len,reverse=True)):
        points=[me.vertices[i].co for i in ids];lo=[min(v[i] for v in points) for i in range(3)];hi=[max(v[i] for v in points) for i in range(3)]
        out.append({'id':ix,'n':len(ids),'lo':lo,'hi':hi,'vertex_ids':ids})
    result[name]=out
project_path('revision/components.json').write_text(json.dumps(result))
print(json.dumps({k:[{a:b for a,b in c.items() if a!='vertex_ids'} for c in v] for k,v in result.items()},indent=2))
