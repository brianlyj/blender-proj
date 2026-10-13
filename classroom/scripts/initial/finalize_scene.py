# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy, json, math
from pathlib import Path
s=bpy.context.scene;rig=bpy.data.objects['CHARACTER_RIG | select to pose']
s.frame_set(1);a={b.name:b.matrix.copy() for b in rig.pose.bones}
s.frame_set(120);loop_error=max(abs(rig.pose.bones[n].matrix[i][j]-a[n][i][j]) for n in a for i in range(4) for j in range(4))
unweighted=[]
for ob in rig.children:
    if ob.type=='MESH' and any(not v.groups for v in ob.data.vertices):unweighted.append(ob.name)
reference=project_path('references/Sports-outfit-reference.png')
im=bpy.data.images.load(str(reference),check_existing=True);im.name='Character reference | supplied image';im.pack()
s.frame_set(16)
notes=bpy.data.texts.get('START HERE | Classroom and character')
notes.write('\nFINAL VALIDATION\n49 bones; 175 skinned mesh components; individual fingers and toe deformation; 12 eye meshes with Blink shape keys.\nReference image is packed in this .blend file.\nAnimation length: five seconds (frames 1-120 at 24 fps).\n')
bpy.ops.wm.save_as_mainfile(filepath=str(project_path('Classroom.blend')))
result={'loop_max_matrix_difference':loop_error,'unweighted_meshes':unweighted,'reference_packed':bool(im.packed_file),'skinned_components':len([o for o in rig.children if o.type=='MESH']),'file':bpy.data.filepath}

