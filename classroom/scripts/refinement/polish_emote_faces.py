"""One-time visibility polish for the first generated emote pack."""
import bpy
from mathutils import Vector

scene=bpy.data.scenes['Classroom | Golden Hour']
if not scene.get('mari_emote_face_polish'):
    for name in ('Emote | squeeze eye L','Emote | squeeze eye R'):
        ob=bpy.data.objects[name]
        # Tubes have three rings, eight vertices per ring.
        for start in range(0,len(ob.data.vertices),8):
            ring=list(ob.data.vertices)[start:start+8]
            center=sum((v.co for v in ring),Vector())/len(ring)
            for v in ring:
                v.co=center+(v.co-center)*(.0075/.0043)
                v.co.y-=.020
        ob.data.update()
    material=bpy.data.materials['Emote | warm ink']
    material.diffuse_color=(.010,.005,.004,1)
    next(n for n in material.node_tree.nodes if n.type=='EMISSION').inputs['Color'].default_value=(.010,.005,.004,1)
    scene['mari_emote_face_polish']=True
    previous_versions=bpy.context.preferences.filepaths.save_version
    try:
        bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
    finally:
        bpy.context.preferences.filepaths.save_version=previous_versions
print('EMOTE_FACE_POLISH_COMPLETE',flush=True)
