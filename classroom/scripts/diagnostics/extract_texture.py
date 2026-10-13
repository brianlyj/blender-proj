# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy,json
from pathlib import Path
p=project_path('revision')
for name in ['hair','face','Texture_0']:
 m=bpy.data.materials[name]
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE' and n.image:
   im=n.image;im.filepath_raw=str(p/(name+'-texture.png'));im.file_format='PNG';im.save();print(name,im.size[:],flush=True)
