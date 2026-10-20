"""Check preserved dance, action loops, transition poses, and shortcut coverage."""
import bpy, hashlib, importlib.util, json, math
from pathlib import Path

project=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('fluid_controls_check',project/'scripts/animation/mari_emote_controls.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
scene=bpy.data.scenes['Classroom | Golden Hour'];bpy.context.window.scene=scene
manifest=c.get_manifest(scene);rig=scene.objects[manifest['rig']]
report={'actions':[],'transitions':[],'invalid_drivers':[]}
build=json.loads((project/'reports/final/fluid-motion-build.json').read_text())
assert hashlib.sha256((project/'deliverables/Classroom-dance.blend').read_bytes()).hexdigest()==build['original_file_sha256']
report['original_dance_file_unchanged']=True
assert len(manifest['entries'])==12
km=bpy.context.window_manager.keyconfigs.addon.keymaps.get('3D View')
bindings={item.type: item.idname for item in km.keymap_items if item.idname.startswith('mari.')}
assert len(bindings)==14,bindings
assert all(k in bindings for k in ('NUMPAD_PLUS','NUMPAD_MINUS','NUMPAD_ENTER','NUMPAD_PERIOD'))
report['bindings']=bindings
def matrices():return {p.name:p.matrix.copy() for p in rig.pose.bones}
def delta(a,b):return max(abs(a[n][i][j]-b[n][i][j]) for n in a for i in range(4) for j in range(4))
out=project/'deliverables/previews/fluid';out.mkdir(parents=True,exist_ok=True)
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=360;scene.render.resolution_y=480;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
if hasattr(scene,'eevee'):scene.eevee.taa_render_samples=16
for e in manifest['entries']:
    c.select_emote(scene,e['number']);bpy.context.view_layer.update();first=matrices()
    scene.frame_set(e['end']);last=matrices();error=delta(first,last)
    assert error<.001,(e['number'],error)
    max_velocity=0;previous=None
    for frame in range(1,e['end']+1):
        scene.frame_set(frame)
        points={n:rig.pose.bones[n].head.copy() for n in ('pelvis','head','hand.L','hand.R','foot.L','foot.R')}
        assert all(math.isfinite(x) for p in points.values() for x in p)
        if previous:max_velocity=max(max_velocity,max((points[n]-previous[n]).length for n in points))
        previous=points
    report['actions'].append({'number':e['number'],'label':e['label'],'loop_error':error,'maximum_joint_step_m':max_velocity})
    scene.frame_set(e['preview_frame']);scene.render.filepath=str(out/('pose-%02d.png'%e['number']))
    bpy.ops.render.render(write_still=True)
    print('FLUID_VALIDATED',e['number'],'loop',error,'step',max_velocity,flush=True)
for source,target in [(3,10),(10,6),(6,11),(11,0),(0,2),(2,7)]:
    c.select_emote(scene,source);scene.frame_set(62);before=matrices()
    c.select_emote(scene,target,blend=True);bpy.context.view_layer.update()
    start_error=delta(before,matrices());assert start_error<.0001,(source,target,start_error)
    transient=rig.animation_data.action;last=int(transient['mari_transition_end'])
    scene.frame_set(last);end_pose=matrices()
    assert c.complete_transition(scene)
    scene.frame_set(last);bpy.context.view_layer.update()
    end_error=delta(end_pose,matrices());assert end_error<.0001,(source,target,end_error)
    report['transitions'].append({'from':source,'to':target,'start_error':start_error,'end_error':end_error,'frames':last})
for data in list(bpy.data.objects)+list(bpy.data.shape_keys):
    if data.animation_data:
        for fc in data.animation_data.drivers:
            if not fc.driver.is_valid:report['invalid_drivers'].append(data.name+':'+fc.data_path)
assert not report['invalid_drivers'],report['invalid_drivers']
c.select_emote(scene,0);scene['mari_emote_keys_enabled']=False
assert bpy.ops.mari.select_emote(number=10,keyboard=True)=={'PASS_THROUGH'}
scene['mari_emote_keys_enabled']=True
for number in (10,11,6):
    assert bpy.ops.mari.select_emote(number=number)=={'FINISHED'}
    assert scene['mari_emote_current']==number
    assert bpy.ops.mari.select_emote(number=number)=={'FINISHED'}
    assert scene['mari_emote_current']==0
report['toggle_and_disabled_shortcuts_pass']=True
report['save_backup_versions']=bpy.context.preferences.filepaths.save_version
assert report['save_backup_versions']>=1
(project/'reports/final/fluid-motion-validation.json').write_text(json.dumps(report,indent=2))
print('FLUID_VALIDATION_COMPLETE',json.dumps(report),flush=True)
