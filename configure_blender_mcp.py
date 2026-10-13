import bpy
import json

module = 'bl_ext.user_default.mcp'
assert module in bpy.context.preferences.addons, 'MCP extension was not enabled'
prefs = bpy.context.preferences.addons[module].preferences
prefs.host = '127.0.0.1'
prefs.port = 9876
prefs.use_autostart = True
bpy.context.preferences.system.use_online_access = True
bpy.ops.wm.save_userpref()
print(json.dumps({'mcp_enabled': True, 'host': prefs.host, 'port': prefs.port, 'auto_start': prefs.use_autostart, 'online_access_preference': bpy.context.preferences.system.use_online_access}))


