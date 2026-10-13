# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import json,struct
from pathlib import Path
p=project_path('revision/Reference-mari.glb')
with p.open('rb') as f:
    magic,version,length=struct.unpack('<4sII',f.read(12))
    chunk_len,chunk_type=struct.unpack('<II',f.read(8))
    doc=json.loads(f.read(chunk_len))
accessors=doc.get('accessors',[])
meshes=[]
for m in doc.get('meshes',[]):
    prims=m.get('primitives',[])
    meshes.append({'name':m.get('name'),'vertices':sum(accessors[p['attributes']['POSITION']]['count'] for p in prims if 'POSITION' in p.get('attributes',{})),'triangles':sum(accessors[p['indices']]['count']//3 for p in prims if 'indices' in p),'morph_targets':max([len(p.get('targets',[])) for p in prims] or [0])})
print(json.dumps({'asset':doc.get('asset'),'scenes':[s.get('name') for s in doc.get('scenes',[])],'mesh_count':len(meshes),'meshes':meshes[:35],'materials':[{'name':m.get('name'),'base_texture':m.get('pbrMetallicRoughness',{}).get('baseColorTexture'),'extensions':list(m.get('extensions',{}))} for m in doc.get('materials',[])],'images':[{'name':i.get('name'),'mimeType':i.get('mimeType'),'embedded':'bufferView' in i} for i in doc.get('images',[])],'skins':[{'name':s.get('name'),'joint_count':len(s.get('joints',[]))} for s in doc.get('skins',[])],'animations':[{'name':a.get('name'),'channels':len(a.get('channels',[]))} for a in doc.get('animations',[]) ]},indent=2))
