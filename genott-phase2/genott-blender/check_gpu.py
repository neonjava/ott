import bpy
prefs = bpy.context.preferences
cprefs = prefs.addons['cycles'].preferences
cprefs.get_devices()

print(f"=== GPU INFO ===")
print(f"Compute Device Type: {cprefs.compute_device_type}")
for dev in cprefs.devices:
    print(f"Device: {dev.name}, Type: {dev.type}, Use: {dev.use}")
print(f"=================")
