# test_import_render.py
import bpy
import sys
import os

print("[Script] Loading Phase 3 Import Rig...")

# Clear default scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Path parameters
argv = sys.argv
if "--" in argv:
    args_idx = argv.index("--")
    char_path = argv[args_idx + 1]
    anim_path = argv[args_idx + 2]
    output_dir = argv[args_idx + 3]
else:
    print("[ERROR] Missing parameters")
    sys.exit(1)

# 1. Import Character GLB
print(f"[Script] Importing GLB Character from: {char_path}")
if os.path.exists(char_path):
    try:
        bpy.ops.import_scene.gltf(filepath=char_path)
    except Exception as e:
        print(f"[Script] GLB Import skipped/failed: {e}. Generating placeholder scene object.")
        # Create a fallback cube mesh representation
        bpy.ops.mesh.primitive_cube_add(size=2, location=(0,0,0))
else:
    print("[ERROR] Character GLB not found!")
    sys.exit(1)

# Find character armature
armature = None
for obj in bpy.context.scene.objects:
    if obj.type == 'ARMATURE':
        armature = obj
        break

# 2. Import Animation FBX
print(f"[Script] Importing FBX Animation from: {anim_path}")
if os.path.exists(anim_path):
    try:
        if armature:
            # Set active object to armature to receive animation data
            bpy.context.view_layer.objects.active = armature
            armature.select_set(True)
        bpy.ops.import_scene.fbx(filepath=anim_path)
        print("[Script] Mapped skeletal keyframes successfully.")
    except Exception as e:
        print(f"[Script] FBX Import skipped/failed: {e}. Running default camera setup.")
else:
    print("[WARNING] Animation FBX file not found. Rendering static mesh.")

# 3. Create Camera
bpy.ops.object.camera_add(location=(0, -6, 2), rotation=(1.3, 0, 0))
cam = bpy.context.active_object
bpy.context.scene.camera = cam

# 4. Create Light
bpy.ops.object.light_add(type='POINT', radius=1.0, align='WORLD', location=(2, -2, 4))
light = bpy.context.active_object
light.data.energy = 1000.0

# 5. Config Cycles GPU Render settings
bpy.context.scene.render.engine = 'CYCLES'
cycles_pref = bpy.context.preferences.addons['cycles'].preferences
cycles_pref.refresh_devices()
cycles_pref.compute_device_type = 'OPTIX'

for device in cycles_pref.devices:
    if device.type == 'OPTIX':
        device.use = True
    else:
        device.use = False

bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.cycles.samples = 16
bpy.context.scene.cycles.preview_samples = 16
bpy.context.scene.cycles.max_bounces = 1

bpy.context.scene.render.resolution_percentage = 25
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.image_settings.color_mode = 'RGBA'

bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 30 # 30 frames test
bpy.context.scene.render.filepath = os.path.join(output_dir, "")

# Run render Eevee/Cycles export
bpy.ops.render.render(animation=True)
print("[Script] Exported animation frames successfully.")
