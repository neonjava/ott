# test_render_script.py
import bpy
import math

print("[Script] Starting Render...")

# 1. Clear default scene elements
bpy.ops.wm.read_factory_settings(use_empty=True)

# 2. Create a test Cube
bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
cube = bpy.context.active_object

# 3. Create a Camera
bpy.ops.object.camera_add(location=(0, -6, 2), rotation=(1.3, 0, 0))
cam = bpy.context.active_object
bpy.context.scene.camera = cam

# 4. Create a Point Light
bpy.ops.object.light_add(type='POINT', radius=1.0, align='WORLD', location=(2, -2, 4))
light = bpy.context.active_object
light.data.energy = 1000.0

# 5. Set up keyframe animation rotation for the Cube (60 frames)
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 60

# Frame 1 Keyframe
cube.rotation_euler = (0, 0, 0)
cube.keyframe_insert(data_path="rotation_euler", frame=1)

# Frame 60 Keyframe (complete 360 rotation around Z-axis)
cube.rotation_euler = (0, 0, math.radians(360))
cube.keyframe_insert(data_path="rotation_euler", frame=60)

# 6. Configure Render & Output settings
bpy.context.scene.render.engine = 'CYCLES'

# Enable Cycles GPU OptiX Rendering
cycles_pref = bpy.context.preferences.addons['cycles'].preferences
cycles_pref.refresh_devices()
cycles_pref.compute_device_type = 'OPTIX'

# Enable the RTX 4060 GPU device
for device in cycles_pref.devices:
    if device.type == 'OPTIX':
        device.use = True
    else:
        device.use = False

bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.cycles.samples = 32
bpy.context.scene.cycles.preview_samples = 32
bpy.context.scene.cycles.max_bounces = 2
bpy.context.scene.cycles.diffuse_bounces = 2
bpy.context.scene.cycles.glossy_bounces = 2
bpy.context.scene.cycles.transparent_max_bounces = 2
bpy.context.scene.cycles.transmission_bounces = 2

# Reduce resolution to speed up test render
bpy.context.scene.render.resolution_percentage = 50
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.image_settings.color_mode = 'RGBA'

# Output location is passed via parameter
import sys
argv = sys.argv
if "--" in argv:
    output_dir = argv[argv.index("--") + 1]
    bpy.context.scene.render.filepath = output_dir + "/"
    print(f"[Script] Output frames path set to: {output_dir}/")

# Trigger Render Animation
bpy.ops.render.render(animation=True)
print("[Script] Rendering Finished successfully.")
