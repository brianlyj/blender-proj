import bpy,json
s=bpy.context.scene;r=bpy.data.objects['MARI | refined character rig']
m=json.loads(s['mari_emote_manifest']);e=m['entries'][10]
r.animation_data.action=bpy.data.actions[e['action']];r.animation_data.action_slot=r.animation_data.action.slots[0]
s.frame_set(1);bpy.context.view_layer.update();a={p.name:p.matrix_basis.copy() for p in r.pose.bones}
s.frame_set(240);bpy.context.view_layer.update()
for p in r.pose.bones:
    delta=max(abs(a[p.name][i][j]-p.matrix_basis[i][j]) for i in range(4) for j in range(4))
    if delta>.0001:print('MISMATCH',p.name,delta,'start',a[p.name].to_euler(),'end',p.matrix_basis.to_euler(),flush=True)
