# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

import bpy
result = {
    'version': bpy.app.version_string,
    'filepath': bpy.data.filepath,
    'is_dirty': bpy.data.is_dirty,
    'scenes': [{'name': s.name, 'objects': len(s.objects)} for s in bpy.data.scenes],
    'active_scene': bpy.context.scene.name,
    'objects': [{'name': o.name, 'type': o.type} for o in bpy.context.scene.objects][:40],
    'engines': [v.identifier for v in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items],
    'devices': bpy.context.preferences.addons['cycles'].preferences.compute_device_type,
}
