"""Blender viewport numpad player for the Mari classroom emote pack."""
bl_info = {
    'name': 'Mari Emote Numpad Controls',
    'author': 'Classroom project',
    'version': (1, 1, 0),
    'blender': (5, 2, 0),
    'location': '3D View > Sidebar > Emotes',
    'description': 'Blend between Mari emotes and both dance versions using the numpad',
    'category': 'Animation',
}

import bpy
import json

_keymaps = []
_timers = []
_face_props = ('emote_face', 'emote_blink_L', 'emote_blink_R')

def capture_pose(rig):
    return ({p.name: p.matrix_basis.decompose() for p in rig.pose.bones},
            {name: float(rig.get(name, 0)) for name in _face_props})

def complete_transition(scene):
    """Replace the short entrance with its canonical action before it loops."""
    manifest = get_manifest(scene)
    rig = scene.objects.get(manifest['rig']) if manifest else None
    action = rig.animation_data.action if rig and rig.animation_data else None
    if action is None or not action.get('mari_transition'):
        return False
    canonical = bpy.data.actions.get(action.get('mari_canonical', ''))
    if canonical is None:
        return False
    slot_id = rig.animation_data.action_slot.identifier
    rig.animation_data.action = canonical
    rig.animation_data.action_slot = next(s for s in canonical.slots if s.identifier == slot_id)
    if action.users == 0:
        bpy.data.actions.remove(action)
    return True

def watch_transition(context, idle):
    _timers[:] = [timer for timer in _timers if bpy.app.timers.is_registered(timer)]
    scene, window = context.scene, context.window
    rig = scene.objects[get_manifest(scene)['rig']]
    action = rig.animation_data.action
    if not action.get('mari_transition'):
        return
    action_name, last_frame = action.name, int(action['mari_transition_end'])
    def tick():
        try:
            current = rig.animation_data.action
            if current is None or current.name != action_name:
                return None
            if scene.frame_current < last_frame:
                return .025
            complete_transition(scene)
            if idle and window.screen.is_animation_playing:
                with bpy.context.temp_override(window=window):
                    bpy.ops.screen.animation_cancel(restore_frame=False)
            return None
        except (ReferenceError, RuntimeError):
            return None
    _timers.append(tick)
    bpy.app.timers.register(tick, first_interval=.025)

def get_manifest(scene):
    raw = scene.get('mari_emote_manifest')
    if not raw:
        return None
    try:
        data = json.loads(raw)
        if data.get('version') != 1 or not isinstance(data.get('entries'), list):
            return None
        return data
    except (ValueError, TypeError):
        return None

def available(context):
    return context.scene is not None and get_manifest(context.scene) is not None

def redraw(context):
    if context.screen:
        for area in context.screen.areas:
            area.tag_redraw()

def select_emote(scene, number, blend=False):
    """Switch the complete rig action, including expression-control channels."""
    manifest = get_manifest(scene)
    if not manifest:
        raise RuntimeError('This scene has no Mari emote pack')
    entry = next((item for item in manifest['entries'] if item['number'] == number), None)
    if not entry:
        raise RuntimeError('Emote %s is not in this pack' % number)
    rig = scene.objects.get(manifest['rig'])
    action = bpy.data.actions.get(entry['action'])
    if rig is None or action is None:
        raise RuntimeError('The emote rig or action is missing')
    slot = next((slot for slot in action.slots if slot.identifier == entry['slot']), None)
    if slot is None:
        raise RuntimeError('The emote action slot is missing')
    rig.animation_data_create()
    old_action = rig.animation_data.action
    source = capture_pose(rig) if blend and old_action else None
    rig.animation_data.action = action
    rig.animation_data.action_slot = slot
    scene.frame_start = entry['start']
    scene.frame_end = entry['end']
    scene.render.fps = entry['fps']
    scene.use_preview_range = False
    scene['mari_emote_current'] = number
    if number:
        scene['mari_emote_previous'] = number
    scene.frame_set(entry['start'])
    if source:
        count = max(3, round(entry['fps'] * .32))
        samples = []
        for frame in range(entry['start'], entry['start'] + count):
            scene.frame_set(frame)
            samples.append(capture_pose(rig))
        transition = action.copy()
        transition.name = 'TRANSITION | ' + entry['label']
        transition.use_fake_user = False
        transition['mari_transition'] = True
        transition['mari_canonical'] = action.name
        transition['mari_transition_end'] = entry['start'] + count - 1
        rig.animation_data.action = transition
        rig.animation_data.action_slot = next(s for s in transition.slots if s.identifier == entry['slot'])
        for index, (target_bones, target_face) in enumerate(samples):
            frame = entry['start'] + index
            u = index / (count - 1)
            weight = u*u*u*(10 + u*(-15 + 6*u))
            for p in rig.pose.bones:
                a, b = source[0][p.name], target_bones[p.name]
                p.location = a[0].lerp(b[0], weight)
                p.rotation_mode = 'QUATERNION'
                p.rotation_quaternion = a[1].slerp(b[1], weight)
                p.rotation_quaternion.make_compatible(b[1])
                p.scale = a[2].lerp(b[2], weight)
                for prop in ('location', 'rotation_quaternion', 'scale'):
                    p.keyframe_insert(data_path=prop, frame=frame, group=p.name)
            for prop in _face_props:
                rig[prop] = (source[1][prop] if weight < .5 else target_face[prop]) if prop == 'emote_face' else source[1][prop]*(1-weight)+target_face[prop]*weight
                rig.keyframe_insert(data_path='["%s"]'%prop, frame=frame, group='Facial expression')
        scene.frame_set(entry['start'])
    if old_action and old_action.get('mari_transition') and old_action.users == 0:
        bpy.data.actions.remove(old_action)
    return entry

class MARI_OT_select_emote(bpy.types.Operator):
    bl_idname = 'mari.select_emote'
    bl_label = 'Play Mari Emote'
    bl_description = 'Play this emote; select it again to return to idle'

    number: bpy.props.IntProperty(default=0, min=0, max=11)
    keyboard: bpy.props.BoolProperty(default=False, options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return available(context)

    def invoke(self, context, event):
        if self.keyboard and not context.scene.get('mari_emote_keys_enabled', False):
            return {'PASS_THROUGH'}
        return self.execute(context)

    def execute(self, context):
        if self.keyboard and not context.scene.get('mari_emote_keys_enabled', False):
            return {'PASS_THROUGH'}
        current = int(context.scene.get('mari_emote_current', 0))
        number = 0 if current == self.number else self.number
        try:
            entry = select_emote(context.scene, number, blend=True)
        except RuntimeError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        if not bpy.app.background and context.screen:
            if not context.screen.is_animation_playing:
                bpy.ops.screen.animation_play()
            watch_transition(context, idle=number == 0)
        redraw(context)
        return {'FINISHED'}

class MARI_OT_toggle_shortcuts(bpy.types.Operator):
    bl_idname = 'mari.toggle_shortcuts'
    bl_label = 'Toggle Emote Shortcuts'
    bl_description = 'Switch between emote numpad shortcuts and normal Blender numpad controls'

    @classmethod
    def poll(cls, context):
        return available(context)

    def execute(self, context):
        enabled = not context.scene.get('mari_emote_keys_enabled', False)
        context.scene['mari_emote_keys_enabled'] = enabled
        self.report({'INFO'}, 'Emote numpad shortcuts ' + ('enabled' if enabled else 'disabled'))
        redraw(context)
        return {'FINISHED'}

class MARI_OT_pause_emote(bpy.types.Operator):
    bl_idname = 'mari.pause_emote'
    bl_label = 'Pause / Resume Emote'
    bl_description = 'Pause/resume the current emote, or replay the previous emote from idle'
    keyboard: bpy.props.BoolProperty(default=False, options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return available(context)

    def invoke(self, context, event):
        if self.keyboard and not context.scene.get('mari_emote_keys_enabled', False):
            return {'PASS_THROUGH'}
        return self.execute(context)

    def execute(self, context):
        if self.keyboard and not context.scene.get('mari_emote_keys_enabled', False):
            return {'PASS_THROUGH'}
        from_idle = int(context.scene.get('mari_emote_current', 0)) == 0
        if from_idle:
            try:
                select_emote(context.scene, int(context.scene.get('mari_emote_previous', 1)), blend=True)
            except RuntimeError as exc:
                self.report({'ERROR'}, str(exc))
                return {'CANCELLED'}
        if not bpy.app.background and context.screen:
            if context.screen.is_animation_playing:
                if not from_idle:
                    bpy.ops.screen.animation_cancel(restore_frame=False)
            else:
                bpy.ops.screen.animation_play()
            watch_transition(context, idle=False)
        redraw(context)
        return {'FINISHED'}

class MARI_PT_emotes(bpy.types.Panel):
    bl_label = 'Mari Emotes'
    bl_idname = 'MARI_PT_emotes'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Emotes'

    @classmethod
    def poll(cls, context):
        return available(context)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        manifest = get_manifest(scene)
        enabled = bool(scene.get('mari_emote_keys_enabled', False))
        layout.operator('mari.toggle_shortcuts', text='Numpad shortcuts: '+('ON' if enabled else 'OFF'), icon='KEYINGSET', depress=enabled)
        layout.label(text='Hover over the 3D viewport to use keys.')
        current = int(scene.get('mari_emote_current', 0))
        for item in manifest['entries']:
            op = layout.operator('mari.select_emote', text='%s  %s'%(item.get('shortcut', str(item['number'])),item['label']), depress=current==item['number'])
            op.number = item['number']
        layout.separator()
        layout.operator('mari.pause_emote', text='Enter: Pause / resume', icon='PLAY')
        layout.label(text='Same key / 0: ease back to idle')
        layout.label(text='Numpad .: enable / disable shortcuts')
        layout.label(text='Turn Num Lock on.')

_classes = (MARI_OT_select_emote,MARI_OT_toggle_shortcuts,MARI_OT_pause_emote,MARI_PT_emotes)

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    config = bpy.context.window_manager.keyconfigs.addon
    if config:
        km = config.keymaps.new(name='3D View', space_type='VIEW_3D')
        bindings = [(number, 'NUMPAD_'+str(number)) for number in range(10)]
        bindings += [(10, 'NUMPAD_PLUS'), (11, 'NUMPAD_MINUS')]
        for number, key in bindings:
            item = km.keymap_items.new('mari.select_emote',key,'PRESS',head=True)
            item.properties.number = number
            item.properties.keyboard = True
            _keymaps.append((km,item))
        item = km.keymap_items.new('mari.pause_emote','NUMPAD_ENTER','PRESS',head=True)
        item.properties.keyboard = True
        _keymaps.append((km,item))
        item = km.keymap_items.new('mari.toggle_shortcuts','NUMPAD_PERIOD','PRESS',head=True)
        _keymaps.append((km,item))

def unregister():
    for timer in _timers:
        if bpy.app.timers.is_registered(timer):
            bpy.app.timers.unregister(timer)
    _timers.clear()
    for km,item in _keymaps:
        km.keymap_items.remove(item)
    _keymaps.clear()
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()
