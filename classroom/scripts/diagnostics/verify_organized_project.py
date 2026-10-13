"""Read-only Blender check of the relocated final scene and its dependencies."""
import bpy
import json
from pathlib import Path

project = Path(__file__).resolve().parents[2]
scene = bpy.data.scenes['Classroom | Golden Hour']
rig = bpy.data.objects['MARI | refined character rig']
images = []
for image in bpy.data.images:
    if image.source != 'FILE':
        continue
    external_path = bpy.path.abspath(image.filepath)
    images.append({
        'name': image.name,
        'path': image.filepath,
        'packed': bool(image.packed_file),
        'external_exists': Path(external_path).is_file(),
        'pixels': list(image.size),
    })
report = {
    'file': bpy.data.filepath,
    'blender_version': bpy.app.version_string,
    'scene': scene.name,
    'frames': [scene.frame_start, scene.frame_end],
    'fps': scene.render.fps / scene.render.fps_base,
    'camera': scene.camera.name,
    'bones': len(rig.data.bones),
    'action': rig.animation_data.action.name,
    'render_path': scene.render.filepath,
    'images': images,
    'libraries': [library.filepath for library in bpy.data.libraries],
    'missing_external_images': [i['name'] for i in images if not i['packed'] and not i['external_exists']],
}
assert report['frames'] == [1, 240]
assert report['fps'] == 24
assert report['bones'] == 49
assert not report['missing_external_images'], report['missing_external_images']
assert not report['libraries'], 'Unexpected linked libraries need separate inspection'
(project/'reports/final/organized-project-validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('ORGANIZED_PROJECT_VALIDATED ' + json.dumps(report), flush=True)
