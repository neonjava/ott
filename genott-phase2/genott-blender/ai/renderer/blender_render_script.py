# ai/renderer/blender_render_script.py
"""
Real Blender render script for the movie pipeline.
Runs inside Blender's Python (bpy) to render a scene from a JSON payload.
Based on the proven render_action_blender.py approach.
"""
import sys
import os
import json
import time

def setup_and_render_scene(payload_file):
    """Load payload config, import character, apply animation, render to MP4."""
    with open(payload_file, "r") as f:
        data = json.load(f)

    character_name = data.get("character_name", "humanoid")
    action = data.get("action", "idle")
    action_file = data.get("action_file", "")
    character_file = data.get("character_file", "")
    location = data.get("location", "battlefield")
    duration = data.get("duration", 5.0)
    output_path = data.get("output_path")
    camera_shot = data.get("camera_shot", "cinematic wide")

    print(f"[BlenderEngine] Rendering scene: character={character_name}, action={action}")
    print(f"[BlenderEngine] Character file: {character_file}")
    print(f"[BlenderEngine] Output path: {output_path}")
    start_loc = data.get("start_location", [0.0, 0.0, 0.0])
    state_file = data.get("state_file_path", "")

    try:
        import bpy
        import mathutils
    except ImportError:
        print("[BlenderEngine] ERROR: bpy not available. This script must run inside Blender.")
        print("[BlenderEngine] Use: flatpak run org.blender.Blender -b --python this_script.py -- payload.json")
        sys.exit(1)

    # Clear default scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # ── 1. Import character GLB ──
    t_start = time.time()
    if character_file and os.path.exists(character_file) and os.path.getsize(character_file) > 100:
        print(f"[BlenderEngine] Importing GLB: {character_file}")
        bpy.ops.import_scene.gltf(filepath=character_file)
    else:
        print(f"[BlenderEngine] WARNING: Character file missing or placeholder: {character_file}")
        print("[BlenderEngine] Creating fallback cube character")
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
    t_import = time.time()
    print(f"[Timing] GLB Import: {t_import - t_start:.2f}s")

    # Move all newly imported top-level objects to start_location
    imported_objects = [obj for obj in bpy.context.scene.objects if not obj.parent]
    for obj in imported_objects:
        obj.location.x += start_loc[0]
        obj.location.y += start_loc[1]
        obj.location.z += start_loc[2]
        
    # Create persistent ground plane for scene continuity
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
    ground = bpy.context.active_object
    mat = bpy.data.materials.new(name="GroundMaterial")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.15, 0.15, 0.15, 1)
        bsdf.inputs['Roughness'].default_value = 0.9
    if ground.data.materials:
        ground.data.materials[0] = mat
    else:
        ground.data.materials.append(mat)

    # Find meshes and armatures
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    armatures = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']

    # ── 2. Apply animation ──
    selected_action = None

    if armatures:
        armature = armatures[0]

        # Track existing actions before importing FBX
        actions_before = set(bpy.data.actions)

        # Check if action_file is an FBX path to import
        is_fbx = action_file and action_file.lower().endswith(".fbx") and os.path.exists(action_file) and os.path.getsize(action_file) > 100
        
        if is_fbx:
            print(f"[BlenderEngine] Importing FBX animation: {action_file}")
            bpy.ops.import_scene.fbx(filepath=action_file)
            actions_after = set(bpy.data.actions)
            new_actions = actions_after - actions_before
            if new_actions:
                selected_action = list(new_actions)[0]
                print(f"[BlenderEngine] Using imported FBX action: {selected_action.name}")
        
        if not selected_action:
            # Try to find embedded action by name (case-insensitive)
            for act in bpy.data.actions:
                if action.lower() in act.name.lower():
                    selected_action = act
                    break
            
            # Fallback: just use the first available action
            if not selected_action and bpy.data.actions:
                selected_action = bpy.data.actions[0]

        if selected_action:
            if armature.animation_data is None:
                armature.animation_data_create()
            armature.animation_data.action = selected_action
            print(f"[BlenderEngine] Applied action: {selected_action.name}")
        else:
            print("[BlenderEngine] No animation found — rendering static pose")

    # ── 3. Compute bounding box for camera framing ──
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
        center = mathutils.Vector((0, 0, 0.5))
        max_dim = 2.0

    # ── 4. Create camera ──
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    bpy.context.scene.camera = cam

    # Camera distance based on shot type
    if "close" in camera_shot.lower():
        dist_mult = 1.0
    elif "wide" in camera_shot.lower() or "aerial" in camera_shot.lower():
        dist_mult = 2.2
    else:
        dist_mult = 1.6

    cam.location = center + mathutils.Vector((0, -max_dim * dist_mult, max_dim * 0.3))
    direction = center - cam.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()

    # ── 5. Lighting ──
    bpy.ops.object.light_add(type='SUN', align='WORLD', location=(0, 0, max_dim * 2))
    sun = bpy.context.active_object
    sun.data.energy = 5.0
    sun.rotation_euler = (0.7, 0.5, 0)

    # Add fill light for better visibility
    bpy.ops.object.light_add(type='AREA', location=(max_dim * 1.5, max_dim * 0.5, max_dim))
    fill = bpy.context.active_object
    fill.data.energy = 200
    fill.data.size = max_dim

    # Set world background (Colors)
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    tree = world.node_tree
    
    # Clear default nodes
    for node in tree.nodes:
        tree.nodes.remove(node)
        
    bg_node = tree.nodes.new(type="ShaderNodeBackground")
    out_node = tree.nodes.new(type="ShaderNodeOutputWorld")
    
    # Adjust sky based on location keywords
    loc_lower = location.lower()
    if "dark" in loc_lower or "storm" in loc_lower or "night" in loc_lower:
        bg_node.inputs['Color'].default_value = (0.02, 0.02, 0.04, 1.0)
    elif "forest" in loc_lower or "field" in loc_lower:
        bg_node.inputs['Color'].default_value = (0.3, 0.5, 0.8, 1.0)
    else:
        bg_node.inputs['Color'].default_value = (0.5, 0.6, 0.7, 1.0)
        
    tree.links.new(bg_node.outputs['Background'], out_node.inputs['Surface'])

    # ── 6. Render settings — Cycles GPU ──
    t_setup = time.time()
    print(f"[Timing] Scene Setup: {t_setup - t_import:.2f}s")
    bpy.context.scene.render.engine = 'CYCLES'
    cycles_pref = bpy.context.preferences.addons['cycles'].preferences
    cycles_pref.get_devices()
    
    # Try OPTIX first, fall back to CUDA
    try:
        cycles_pref.compute_device_type = 'OPTIX'
        for device in cycles_pref.devices:
            if device.type == 'OPTIX':
                device.use = True
    except Exception:
        try:
            cycles_pref.compute_device_type = 'CUDA'
            for device in cycles_pref.devices:
                if device.type == 'CUDA':
                    device.use = True
        except Exception:
            print("[BlenderEngine] WARNING: No GPU found, falling back to CPU")

    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.cycles.samples = 16
    bpy.context.scene.cycles.preview_samples = 8
    bpy.context.scene.cycles.max_bounces = 2

    # Resolution
    bpy.context.scene.render.resolution_x = 960
    bpy.context.scene.render.resolution_y = 540
    bpy.context.scene.render.resolution_percentage = 100

    # ── 7. Frame range ──
    fps = 24
    bpy.context.scene.render.fps = fps

    if selected_action:
        f_start = int(selected_action.frame_range[0])
        f_end = int(selected_action.frame_range[1])
        # If animation is very short, loop it to fill duration
        anim_frames = f_end - f_start + 1
        target_frames = int(duration * fps)
        if anim_frames < target_frames and anim_frames > 0:
            # Use the animation's natural length
            pass
        print(f"[BlenderEngine] Frame range: {f_start} to {f_end} ({anim_frames} frames)")
    else:
        f_start = 1
        f_end = int(duration * fps)
        print(f"[BlenderEngine] Static scene: {f_start} to {f_end}")

    bpy.context.scene.frame_start = f_start
    bpy.context.scene.frame_end = f_end

    # ── 8. Render to PNG frames then compile to MP4 ──
    import tempfile
    render_dir = tempfile.mkdtemp(prefix="blender_render_")
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    bpy.context.scene.render.filepath = os.path.join(render_dir, "frame_")

    print(f"[BlenderEngine] Rendering {f_end - f_start + 1} frames to {render_dir}...")
    t_render_start = time.time()
    bpy.ops.render.render(animation=True)
    t_render_end = time.time()
    print(f"[Timing] Frame Rendering: {t_render_end - t_render_start:.2f}s")
    print("[BlenderEngine] Frame rendering complete.")

    # Save first frame as storyboard thumbnail
    first_frame_src = os.path.join(render_dir, f"frame_{str(f_start).zfill(4)}.png")
    storyboard_out = output_path.replace(".mp4", "_thumb.png")
    if os.path.exists(first_frame_src):
        import shutil
        shutil.copy(first_frame_src, storyboard_out)
        print(f"[BlenderEngine] Saved storyboard thumbnail: {storyboard_out}")

    # Compile frames to MP4 using FFmpeg
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    import subprocess
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", os.path.join(render_dir, "frame_%04d.png"),
        "-c:v", "h264_nvenc",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-b:v", "2M",
        output_path
    ]

    try:
        t_ffmpeg_start = time.time()
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        t_ffmpeg_end = time.time()
        print(f"[Timing] FFmpeg Compile: {t_ffmpeg_end - t_ffmpeg_start:.2f}s")
        print(f"[BlenderEngine] Video compiled: {output_path}")
    except subprocess.CalledProcessError:
        # Fallback to software encoder
        t_ffmpeg_start = time.time()
        ffmpeg_cmd_sw = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", os.path.join(render_dir, "frame_%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-crf", "23",
            output_path
        ]
        subprocess.run(ffmpeg_cmd_sw, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        t_ffmpeg_end = time.time()
        print(f"[Timing] FFmpeg Compile (SW): {t_ffmpeg_end - t_ffmpeg_start:.2f}s")
        print(f"[BlenderEngine] Video compiled (software): {output_path}")

    # Cleanup render frames
    import shutil
    shutil.rmtree(render_dir, ignore_errors=True)

    # ── 9. Save State (Character Persistence) ──
    if state_file:
        # Determine ending location
        end_loc = list(start_loc)
        # Approximate movement (if action is "walk" or "run", they move forward. Blender actions here are in-place or root motion. 
        # If root motion, we should evaluate the armature at f_end. If in-place, we manually simulate movement.)
        speed = 0.0
        if "run" in action.lower(): speed = 4.0
        elif "walk" in action.lower(): speed = 1.5
        elif "jump" in action.lower() or "fly" in action.lower(): speed = 2.0
        
        distance = speed * duration
        # Assuming character faces -Y
        end_loc[1] -= distance
        
        with open(state_file, "w") as f:
            json.dump({"end_location": end_loc}, f)
        print(f"[BlenderEngine] Saved persistent character state: {end_loc}")

    print(f"[BlenderEngine] Scene render complete: {output_path}")


if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        setup_and_render_scene(argv[argv.index("--") + 1])
    else:
        print("[BlenderEngine] Usage: blender -b --python blender_render_script.py -- payload.json")
