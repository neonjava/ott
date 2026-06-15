# test_humanoid_render.py
import bpy
import os
import sys
import mathutils

print("[Script] Starting Humanoid Rig Validation...")

# Clear default scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Read command args
argv = sys.argv
if "--" in argv:
    args_idx = argv.index("--")
    char_path = argv[args_idx + 1]
    action_name = argv[args_idx + 2]
    output_dir = argv[args_idx + 3]
else:
    print("[ERROR] Missing arguments")
    sys.exit(1)

# 1. Import rigged GLB Character
print(f"[Script] Importing GLB: {char_path}")
bpy.ops.import_scene.gltf(filepath=char_path)

# Verify mesh and armature existence
meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
armatures = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']

print(f"VERIFICATION_MESH_COUNT: {len(meshes)}")
print(f"VERIFICATION_ARMATURE_COUNT: {len(armatures)}")

for obj in bpy.context.scene.objects:
    print(f"VERIFICATION_OBJECT: {obj.name} ({obj.type})")

if not armatures:
    print("[ERROR] Armature not found in character file!")
    sys.exit(1)

armature = armatures[0]

# 2. Verify and select Animation Action
print("Available Actions:")
for action in bpy.data.actions:
    print(f"VERIFICATION_ACTION: {action.name}")

selected_action = bpy.data.actions.get(action_name)
if not selected_action:
    # Try case-insensitive lookup
    for action in bpy.data.actions:
        if action.name.lower() == action_name.lower():
            selected_action = action
            break

if not selected_action:
    print(f"[ERROR] Selected action '{action_name}' not found!")
    sys.exit(1)

print(f"VERIFICATION_SELECTED_ACTION: {selected_action.name}")
# Read frame range details
f_start = int(selected_action.frame_range[0])
f_end = int(selected_action.frame_range[1])
print(f"VERIFICATION_FRAME_COUNT: {f_end - f_start}")

# 3. Apply animation to armature
if armature.animation_data is None:
    armature.animation_data_create()
armature.animation_data.action = selected_action

# Compute dynamic bounding box for camera framing
min_coords = None
max_coords = None

for obj in meshes:
    for vertex in obj.bound_box:
        world_vertex = obj.matrix_world @ mathutils.Vector(vertex)
        if min_coords is None:
            min_coords = list(world_vertex)
            max_coords = list(world_vertex)
        else:
            for i in range(3):
                if world_vertex[i] < min_coords[i]:
                    min_coords[i] = world_vertex[i]
                if world_vertex[i] > max_coords[i]:
                    max_coords[i] = world_vertex[i]

if min_coords is not None:
    min_v = mathutils.Vector(min_coords)
    max_v = mathutils.Vector(max_coords)
    center = (min_v + max_v) / 2.0
    size = max_v - min_v
    max_dim = max(size)
else:
    center = mathutils.Vector((0, 0, 0))
    max_dim = 2.0

# 4. Create Camera targeting character armature center dynamically
bpy.ops.object.camera_add()
cam = bpy.context.active_object
bpy.context.scene.camera = cam

# Position camera back and slightly up relative to max dimension
cam.location = center + mathutils.Vector((0, -max_dim * 1.6, max_dim * 0.3))
direction = center - cam.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam.rotation_euler = rot_quat.to_euler()

# 5. Create Sun Light (size-independent)
bpy.ops.object.light_add(type='SUN', align='WORLD', location=(0, 0, max_dim * 2))
sun = bpy.context.active_object
sun.data.energy = 5.0
sun.rotation_euler = (0.7, 0.5, 0)

# Set ambient background color
if bpy.data.worlds.get("World"):
    world = bpy.data.worlds["World"]
    if world.node_tree:
        bg_node = world.node_tree.nodes.get("Background")
        if bg_node:
            bg_node.inputs[0].default_value = (0.15, 0.15, 0.18, 1.0)

# 6. Configure low-sample Cycles GPU Render settings
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

# Configure output directories
bpy.context.scene.render.resolution_percentage = 50
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.image_settings.color_mode = 'RGBA'

bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 120 # Render 120 frames
bpy.context.scene.render.filepath = os.path.join(output_dir, "")

# Run render sequence
bpy.ops.render.render(animation=True)
print("[Script] Exported animation frames successfully.")

