"""Refresh the embedded controller and default dance without changing geometry."""
import bpy
from pathlib import Path
project=Path(__file__).resolve().parents[2]
block=bpy.data.texts.get('mari_emote_controls.py')
block.clear();block.write((project/'scripts/animation/mari_emote_controls.py').read_text())
scene=bpy.context.scene;scene.sync_mode='FRAME_DROP'
previous=bpy.context.preferences.filepaths.save_version
try:
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(project/'deliverables/Classroom-emotes.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=previous
