"""Validate action/driver switching and render representative emote frames."""
import bpy
import importlib.util
import json
import math
from pathlib import Path

project=Path(__file__).resolve().parents[2]
module_path=project/'scripts/animation/mari_emote_controls.py'
spec=importlib.util.spec_from_file_location('mari_controls_check',module_path)
controls=importlib.util.module_from_spec(spec)
spec.loader.exec_module(controls)
registered_here=not hasattr(bpy.types,'MARI_PT_emotes')
if registered_here:
    controls.register()
scene=bpy.data.scenes['Classroom | Golden Hour']
bpy.context.window.scene=scene
manifest=controls.get_manifest(scene)
rig=scene.objects[manifest['rig']]
km=bpy.context.window_manager.keyconfigs.addon.keymaps.get('3D View')
key_count=sum(1 for item in km.keymap_items if item.idname.startswith('mari.')) if km else 0
result={'emotes':[],'keymap_items':key_count,'invalid_drivers':[]}
output=project/'deliverables/previews/emotes'
output.mkdir(parents=True,exist_ok=True)
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=480;scene.render.resolution_y=640
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
if hasattr(scene,'eevee') and hasattr(scene.eevee,'taa_render_samples'):
    scene.eevee.taa_render_samples=16
for entry in manifest['entries']:
    controls.select_emote(scene,entry['number'])
    first={p.name:p.matrix.copy() for p in rig.pose.bones}
    scene.frame_set(entry['end'])
    delta=max(abs(p.matrix[i][j]-first[p.name][i][j]) for p in rig.pose.bones for i in range(4) for j in range(4))
    assert delta<.001,(entry['label'],delta)
    scene.frame_set(entry['preview_frame'])
    bpy.context.view_layer.update()
    assert all(math.isfinite(v) for p in rig.pose.bones for row in p.matrix for v in row)
    result['emotes'].append({'number':entry['number'],'label':entry['label'],'endpoint_matrix_error':delta,'active_slot':rig.animation_data.action_slot.identifier,'face':rig['emote_face']})
    scene.render.filepath=str(output/('emote-%02d.png'%entry['number']))
    bpy.ops.render.render(write_still=True,scene=scene.name)
    print('EMOTE_CHECKED_RENDERED',entry['number'],entry['label'],flush=True)
for data in list(bpy.data.objects)+list(bpy.data.shape_keys):
    if data.animation_data:
        for fc in data.animation_data.drivers:
            if not fc.driver.is_valid:result['invalid_drivers'].append(data.name+':'+fc.data_path)
assert not result['invalid_drivers'],result['invalid_drivers']
controls.select_emote(scene,0)
scene['mari_emote_keys_enabled']=False
assert bpy.ops.mari.select_emote(number=2,keyboard=True)=={'PASS_THROUGH'}
assert scene['mari_emote_current']==0
scene['mari_emote_keys_enabled']=True
assert bpy.ops.mari.select_emote(number=2)=={'FINISHED'}
assert scene['mari_emote_current']==2
assert bpy.ops.mari.select_emote(number=2)=={'FINISHED'}
assert scene['mari_emote_current']==0
result['same_key_returns_idle']=True
result['disabled_keys_pass_through']=True
if registered_here:
    controls.unregister()
    result['unregister_removed_keys']=len(controls._keymaps)==0
(project/'reports/final/emote-validation.json').write_text(json.dumps(result,indent=2))
print('EMOTE_VALIDATION_COMPLETE',json.dumps(result),flush=True)
