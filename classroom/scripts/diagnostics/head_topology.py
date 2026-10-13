# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy,json
from pathlib import Path
r=project_path('revision')
face=bpy.data.objects['R2 | Face | sculpted anime'];eyes=bpy.data.objects['R2 | Eyes | textured anime']
# Save mesh buffers for local topology analysis, without the scene's other content.
for o in [face,eyes]:
 d={'v':[list(v.co) for v in o.data.vertices],'p':[list(p.vertices) for p in o.data.polygons],'uv':[list(v.uv) for v in o.data.uv_layers.active.data]}
 (r/('face-topology.json' if o==face else 'eyes-topology.json')).write_text(json.dumps(d))
result={'topology_saved':True}
