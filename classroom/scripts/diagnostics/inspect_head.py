# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy,json
from pathlib import Path
s=bpy.data.scenes['Classroom | Golden Hour'];r=bpy.data.objects['MARI | refined character rig']
names=['R2 | Eyes | textured anime','R2 | Hair | textured crown and fringe','R2 | Face | sculpted anime']
report={}
for name in names:
 o=bpy.data.objects[name];report[name]={'bounds':[[min(v.co[k] for v in o.data.vertices),max(v.co[k] for v in o.data.vertices)] for k in range(3)],'materials':[m.name for m in o.data.materials]}
 report[name]['samples']=[list(v.co) for v in o.data.vertices if v.index%max(1,len(o.data.vertices)//40)==0]
report['bones']={b.name:[list(b.head_local),list(b.tail_local)] for b in r.data.bones if b.name in ['head','hair.L','hair.R','hair.back','ear.L','ear.R']}
report['headpose']={p.name:list(p.rotation_euler) for p in r.pose.bones if p.name in ['head','hair.L','hair.R','hair.back','ear.L','ear.R']}
project_path('revision/head_report.json').write_text(json.dumps(report,indent=2))
result={'file':bpy.data.filepath,'scene':s.name,'head':report}
