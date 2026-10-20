"""Exercise the actual UI playback/timer path, then leave the new dance playing."""
import bpy,json,time,traceback
from pathlib import Path
import mari_emote_controls as controls
project=Path(__file__).resolve().parents[2]
scene=bpy.context.scene;rig=scene.objects[controls.get_manifest(scene)['rig']]
window=bpy.context.window
area=next(a for a in window.screen.areas if a.type=='VIEW_3D')
region=next(r for r in area.regions if r.type=='WINDOW')
state={'stage':0,'deadline':time.monotonic()+20}
report={'file':bpy.data.filepath,'controller_version':list(controls.bl_info['version']),'tests':[]}
report_path=project/'reports/final/fluid-live-check.json'
def save():report_path.write_text(json.dumps(report,indent=2))
def invoke(number):
    with bpy.context.temp_override(window=window,area=area,region=region):
        assert bpy.ops.mari.select_emote(number=number)=={'FINISHED'}
def run():
    try:
        if time.monotonic()>state['deadline']:raise RuntimeError('Live transition did not finish before the deadline')
        stage=state['stage']
        if stage==0:
            if window.screen.is_animation_playing:
                with bpy.context.temp_override(window=window):bpy.ops.screen.animation_cancel(restore_frame=False)
            keys=bpy.context.window_manager.keyconfigs.user.keymaps.get('3D View')
            report['key_priority']=[{'order':i,'key':k.type,'operator':k.idname} for i,k in enumerate(keys.keymap_items) if k.type in ('NUMPAD_PLUS','NUMPAD_MINUS')]
            for key in ('NUMPAD_PLUS','NUMPAD_MINUS'):
                first=next(k for k in keys.keymap_items if k.type==key and k.active and not k.ctrl and not k.shift and not k.alt)
                assert first.idname=='mari.select_emote',(key,first.idname)
            controls.select_emote(scene,11);scene.frame_set(65)
            invoke(10);assert rig.animation_data.action.get('mari_transition')
            state['stage']=1
            return .1
        if stage==1:
            if rig.animation_data.action.get('mari_transition'):return .1
            assert window.screen.is_animation_playing
            assert scene['mari_emote_current']==10
            report['tests'].append('Original to refined dance: entrance completed and playback continues')
            invoke(0);state['stage']=2
            return .1
        if stage==2:
            if rig.animation_data.action.get('mari_transition'):return .1
            assert not window.screen.is_animation_playing
            assert scene['mari_emote_current']==0
            report['tests'].append('Return to idle: transition completed and playback stopped')
            with bpy.context.temp_override(window=window,area=area,region=region):
                assert bpy.ops.mari.pause_emote()=={'FINISHED'}
            state['stage']=3
            return .1
        if stage==3:
            if rig.animation_data.action.get('mari_transition'):return .1
            assert window.screen.is_animation_playing
            report['tests'].append('Enter from idle: previous dance resumes with a completed transition')
            with bpy.context.temp_override(window=window,area=area,region=region):
                bpy.ops.mari.pause_emote();assert not window.screen.is_animation_playing
                bpy.ops.mari.pause_emote();assert window.screen.is_animation_playing
            report['tests'].append('Enter pauses and resumes active playback')
            report['passed']=True;report['current']=scene['mari_emote_current'];report['playing']=window.screen.is_animation_playing
            save();print('FLUID_LIVE_CHECK_PASSED',json.dumps(report),flush=True)
            return None
    except Exception:
        report['passed']=False;report['error']=traceback.format_exc();save();print(report['error'],flush=True)
        return None
bpy.app.timers.register(run,first_interval=2)
