"""Install only the companion controller; preserve the other addon settings."""
import bpy
import addon_utils
import importlib
import json
import shutil
import sys
from pathlib import Path

project=Path(__file__).resolve().parents[2]
source=project/'scripts/animation/mari_emote_controls.py'
addon_dir=Path(bpy.utils.user_resource('SCRIPTS',path='addons',create=True))
target=addon_dir/'mari_emote_controls.py'
pref_file=Path(bpy.utils.user_resource('CONFIG'))/'userpref.blend'
backup_dir=Path(bpy.utils.user_resource('CONFIG'))/'mari-emote-backup'
backup_dir.mkdir(exist_ok=True)
if pref_file.exists() and not (backup_dir/'userpref-before-emotes.blend').exists():
    shutil.copy2(pref_file,backup_dir/'userpref-before-emotes.blend')
if target.exists() and target.read_bytes()!=source.read_bytes():
    shutil.copy2(target,backup_dir/'mari_emote_controls_previous.py')
if addon_utils.check('mari_emote_controls')[1]:
    addon_utils.disable('mari_emote_controls',default_set=False)
shutil.copy2(source,target)
bpy.utils.refresh_script_paths()
importlib.invalidate_caches()
if 'mari_emote_controls' in sys.modules:
    importlib.reload(sys.modules['mari_emote_controls'])
addon_utils.modules_refresh()
module=addon_utils.enable('mari_emote_controls',default_set=True,persistent=True)
assert module is not None,'Controller could not be enabled'
assert addon_utils.check('mari_emote_controls')==(True,True)
assert len(module._keymaps)==14
assert module.bl_info['version']==(1,1,0)
bpy.ops.wm.save_userpref()
report={'installed':str(target),'enabled':True,'keymap_items':len(module._keymaps),'preferences_backup':str(backup_dir/'userpref-before-emotes.blend')}
(project/'reports/final/emote-controller-install.json').write_text(json.dumps(report,indent=2))
print('EMOTE_CONTROLS_INSTALLED',json.dumps(report),flush=True)
