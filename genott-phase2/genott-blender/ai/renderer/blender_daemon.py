import bpy
import sys
import os
import json
import time
import shutil
import subprocess
import math
from typing import List
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 5005
DAEMON_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(DAEMON_DIR))
CHARACTER_FILE = os.path.join(PROJECT_DIR, "assets", "characters", "humanoid.glb")

def init_blender_env():
    print("[BlenderDaemon] Initializing persistent environment...")
    
    # 1. Clear scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 2. Setup GPU (OptiX / CUDA preferences activation)
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    
    try:
        preferences = bpy.context.preferences
        cycles_preferences = preferences.addons['cycles'].preferences
        cycles_preferences.refresh_devices()
        
        # Prefer OPTIX, fallback to CUDA
        device_type = "CUDA"
        for device_group in cycles_preferences.get_device_types():
            if device_group[0] == "OPTIX":
                device_type = "OPTIX"
                break
                
        cycles_preferences.compute_device_type = device_type
        print(f"[BlenderDaemon] Cycles compute device type set to: {device_type}")
        
        for device in cycles_preferences.devices:
            if device.type == device_type:
                device.use = True
                print(f"[BlenderDaemon] Enabled Cycles GPU device: {device.name}")
            else:
                device.use = False
    except Exception as e:
        print(f"[BlenderDaemon] Failed to configure GPU preferences: {e}")
        
    bpy.context.scene.cycles.samples = 2
    bpy.context.scene.render.resolution_x = 256
    bpy.context.scene.render.resolution_y = 256
    bpy.context.scene.render.fps = 12
    
    # Enable Filmic View Transform and High Contrast Look for cinematic color grading
    try:
        bpy.context.scene.view_settings.view_transform = 'Filmic'
        bpy.context.scene.view_settings.look = 'High Contrast'
        print("[BlenderDaemon] Color Management set to Filmic High Contrast.")
    except Exception as ce:
        print(f"[BlenderDaemon] Color settings failed: {ce}")
    
    # 3. Import Character
    if os.path.exists(CHARACTER_FILE):
        bpy.ops.import_scene.gltf(filepath=CHARACTER_FILE)
    
    # 4. Setup Cinematic Three-Point Studio Lighting Setup (M4 Visual Quality Upgrades)
    # Key Light (Strong front-side lighting defining shape with soft shadows)
    key_data = bpy.data.lights.new(name="KeyLight", type='SUN')
    key_data.energy = 4.0
    key_data.angle = 0.1  # Soft shadow boundaries
    key_obj = bpy.data.objects.new(name="KeyLight", object_data=key_data)
    bpy.context.collection.objects.link(key_obj)
    key_obj.location = (5, -5, 8)
    # Rotate Key Light toward origin (approximate)
    key_obj.rotation_euler = (math.radians(45), 0, math.radians(45))
 
    # Fill Light (Softer lighting filling shadows)
    fill_data = bpy.data.lights.new(name="FillLight", type='SUN')
    fill_data.energy = 1.5
    fill_data.angle = 0.15  # Extremely soft fill shadows
    fill_obj = bpy.data.objects.new(name="FillLight", object_data=fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-5, -5, 6)
    fill_obj.rotation_euler = (math.radians(35), 0, math.radians(-45))
 
    # Rim Light (Back light highlighting silhouettes and edges)
    rim_data = bpy.data.lights.new(name="RimLight", type='SUN')
    rim_data.energy = 3.0
    rim_data.angle = 0.12  # Soft rim outline
    rim_obj = bpy.data.objects.new(name="RimLight", object_data=rim_data)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.location = (0, 5, 8)
    rim_obj.rotation_euler = (math.radians(-45), 0, 0)
    
    # 5. Setup World
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    tree = world.node_tree
    for node in tree.nodes:
        tree.nodes.remove(node)
    bg_node = tree.nodes.new(type="ShaderNodeBackground")
    out_node = tree.nodes.new(type="ShaderNodeOutputWorld")
    bg_node.inputs['Color'].default_value = (0.5, 0.6, 0.7, 1.0)
    tree.links.new(bg_node.outputs['Background'], out_node.inputs['Surface'])
    
    print("[BlenderDaemon] Initialization complete.")

def customize_character(character_name: str, held_item: str = None, outfits: List[str] = None):
    if not bpy: return
    name_clean = character_name.lower().replace(" ", "_")
    char_suffix = f"_{name_clean}"
    print(f"[BlenderDaemon] Customizing character meshes and materials for: {name_clean} (Outfits: {outfits})")
    
    # Define color mappings for each character type
    char_styles = {
        "knight": {
            "Skin": (0.6, 0.6, 0.65, 1.0),
            "Character_Main": (0.7, 0.7, 0.75, 1.0), # silver steel armor
            "Pants": (0.25, 0.25, 0.3, 1.0),
            "ShoulderPads": True,
            "scale": (1.1, 1.1, 1.1)
        },
        "mage": {
            "Skin": (0.95, 0.8, 0.7, 1.0),
            "Character_Main": (0.3, 0.1, 0.5, 1.0), # royal purple robes
            "Pants": (0.15, 0.08, 0.25, 1.0),
            "ShoulderPads": False,
            "scale": (0.95, 0.95, 0.95)
        },
        "robot": {
            "Skin": (0.8, 0.8, 0.85, 1.0), # chrome skin
            "Character_Main": (0.1, 0.15, 0.2, 1.0), # dark carbon body
            "Pants": (0.05, 0.8, 0.95, 1.0), # glowing cyan accent
            "ShoulderPads": True,
            "scale": (1.05, 1.05, 1.05)
        },
        "anime_girl": {
            "Skin": (0.98, 0.82, 0.75, 1.0), # peach skin
            "Character_Main": (0.95, 0.3, 0.45, 1.0), # pink outfit
            "Pants": (0.95, 0.95, 0.95, 1.0), # white pants
            "ShoulderPads": False,
            "scale": (0.9, 0.9, 0.9)
        },
        "anime_boy": {
            "Skin": (0.98, 0.82, 0.75, 1.0), # peach skin
            "Character_Main": (0.1, 0.3, 0.6, 1.0), # blue jacket
            "Pants": (0.2, 0.2, 0.25, 1.0), # dark pants
            "ShoulderPads": False,
            "scale": (1.0, 1.0, 1.0)
        },
        "humanoid": {
            "Skin": (0.9, 0.9, 0.9, 1.0),
            "Character_Main": (0.5, 0.5, 0.5, 1.0),
            "Pants": (0.3, 0.3, 0.3, 1.0),
            "ShoulderPads": False,
            "scale": (1.0, 1.0, 1.0)
        }
    }
    
    style = char_styles.get(name_clean, char_styles["humanoid"])
    
    # 1. Update materials
    for mat_name in ["Skin", "Character_Main", "Pants"]:
        mat = bpy.data.materials.get(mat_name)
        if mat:
            mat.use_nodes = False
            mat.diffuse_color = style[mat_name]
            
    # Also color the shoulder pad material specifically if knight or robot
    grey_mat = bpy.data.materials.get("Grey")
    if grey_mat:
        grey_mat.use_nodes = False
        grey_mat.diffuse_color = style["Character_Main"]

    # 2. Hide/Unhide Shoulder Pads
    pads = ["ShoulderPad.L", "ShoulderPad.R"]
    for pad_name in pads:
        pad_obj = bpy.context.scene.objects.get(f"{pad_name}{char_suffix}")
        if pad_obj:
            val = not style["ShoulderPads"]
            pad_obj.hide_viewport = val
            pad_obj.hide_render = val

    # 3. Apply scale to armature
    armature = bpy.context.scene.objects.get(f"Armature{char_suffix}")
    if armature:
        armature.scale = style["scale"]
        
    # 4. Hide all weapon meshes built into the model by default
    weapons = ["Revolver", "Sniper", "Revolver_Small", "Pistol", "SMG", "GrenadeLauncher", 
               "ShortCannon", "Shotgun", "Sniper_2", "RocketLauncher", "AK", "Shovel", "Knife_2", "Knife_1"]
    for w_name in weapons:
        w_obj = bpy.context.scene.objects.get(f"{w_name}{char_suffix}")
        if w_obj:
            w_obj.hide_viewport = True
            w_obj.hide_render = True

    # 5. Show matching held item if active
    if held_item:
        held_item_clean = held_item.lower()
        if "shovel" in held_item_clean:
            w_obj = bpy.context.scene.objects.get(f"Shovel{char_suffix}")
            if w_obj:
                w_obj.hide_viewport = False
                w_obj.hide_render = False
        elif "knife" in held_item_clean:
            w_obj = bpy.context.scene.objects.get(f"Knife_1{char_suffix}")
            if w_obj:
                w_obj.hide_viewport = False
                w_obj.hide_render = False
        elif "gun" in held_item_clean or "pistol" in held_item_clean:
            w_obj = bpy.context.scene.objects.get(f"Pistol{char_suffix}")
            if w_obj:
                w_obj.hide_viewport = False
                w_obj.hide_render = False
        elif "rifle" in held_item_clean or "ak" in held_item_clean:
            w_obj = bpy.context.scene.objects.get(f"AK{char_suffix}")
            if w_obj:
                w_obj.hide_viewport = False
                w_obj.hide_render = False

    # 6. Apply outfits material/mesh modifications
    if outfits:
        from typing import List
        for outfit in outfits:
            outfit_clean = outfit.lower().strip()
            if outfit_clean == "helmet":
                head_mat = bpy.data.materials.get("Skin")
                if head_mat:
                    head_mat.use_nodes = False
                    head_mat.diffuse_color = (0.85, 0.72, 0.2, 1.0) # gold helmet
            elif outfit_clean == "armor":
                for pad_name in ["ShoulderPad.L", "ShoulderPad.R"]:
                    pad_obj = bpy.context.scene.objects.get(f"{pad_name}{char_suffix}")
                    if pad_obj:
                        pad_obj.hide_viewport = False
                        pad_obj.hide_render = False
                main_mat = bpy.data.materials.get("Character_Main")
                if main_mat:
                    main_mat.use_nodes = False
                    main_mat.diffuse_color = (0.42, 0.45, 0.5, 1.0) # steel armor
            elif outfit_clean == "crown":
                head_mat = bpy.data.materials.get("Skin")
                if head_mat:
                    head_mat.use_nodes = False
                    head_mat.diffuse_color = (0.95, 0.8, 0.1, 1.0) # golden crown
            elif outfit_clean == "cloak":
                pants_mat = bpy.data.materials.get("Pants")
                if pants_mat:
                    pants_mat.use_nodes = False
                    pants_mat.diffuse_color = (0.55, 0.08, 0.08, 1.0) # royal red cloak
            elif outfit_clean == "boots":
                pants_mat = bpy.data.materials.get("Pants")
                if pants_mat:
                    pants_mat.use_nodes = False
                    pants_mat.diffuse_color = (0.22, 0.15, 0.1, 1.0) # dark brown boots

def apply_emotion_posture(armature, mood: str, f_start: int, f_end: int):
    if not armature: return
    mood_clean = mood.lower().strip()
    
    # Define rotation offsets for each mood (Euler in radians)
    mood_styles = {
        "sad": {
            "Shoulder.L": (0.0, -0.2, 0.1),
            "Shoulder.R": (0.0, 0.2, -0.1),
            "Neck": (0.2, 0.0, 0.0),
            "Head": (0.1, 0.0, 0.0),
            "Torso": (0.1, 0.0, 0.0)
        },
        "aggressive": {
            "Shoulder.L": (0.0, 0.1, -0.1),
            "Shoulder.R": (0.0, -0.1, 0.1),
            "Neck": (0.25, 0.0, 0.0),
            "Head": (-0.1, 0.0, 0.0),
            "Torso": (0.15, 0.0, 0.0)
        },
        "cheerful": {
            "Neck": (-0.1, 0.0, 0.0),
            "Head": (-0.1, 0.1, 0.0),
            "Torso": (-0.05, 0.0, 0.0)
        },
        "tense": {
            "Shoulder.L": (0.0, 0.3, 0.0),
            "Shoulder.R": (0.0, -0.3, 0.0),
            "Neck": (0.1, 0.0, 0.0),
            "Head": (0.05, 0.0, 0.0)
        },
        "triumphant": {
            "Neck": (-0.15, 0.0, 0.0),
            "Head": (-0.1, 0.0, 0.0),
            "Torso": (-0.1, 0.0, 0.0)
        },
        "mysterious": {
            "Shoulder.L": (0.05, 0.1, 0.0),
            "Shoulder.R": (0.05, -0.1, 0.0),
            "Neck": (0.15, 0.0, 0.1),
            "Head": (0.05, 0.0, -0.1)
        },
        "epic": {
            "Neck": (-0.2, 0.0, 0.0),
            "Head": (-0.15, 0.0, 0.0),
            "Torso": (-0.12, 0.0, 0.0)
        },
        "hope": {
            "Neck": (-0.1, 0.0, 0.0),
            "Head": (-0.15, 0.0, 0.0),
            "Torso": (-0.05, 0.0, 0.0)
        },
        "happy": {
            "Neck": (-0.08, 0.0, 0.0),
            "Head": (-0.08, 0.05, 0.0),
            "Torso": (-0.03, 0.0, 0.0)
        }
    }
    
    if mood_clean not in mood_styles:
        return
        
    rotations = mood_styles[mood_clean]
    
    # Create or clean temporary action for this mood posture
    action_name = f"TempPosture_{mood_clean}"
    old_act = bpy.data.actions.get(action_name)
    if old_act:
        bpy.data.actions.remove(old_act)
        
    posture_action = bpy.data.actions.new(name=action_name)
    
    # Temporarily set active action to write keyframes
    armature.animation_data.action = posture_action
    
    # Reset pose bones to default before posing, to ensure we keyframe only the offset
    for bone_name in rotations.keys():
        pb = armature.pose.bones.get(bone_name)
        if pb:
            pb.rotation_euler = (0.0, 0.0, 0.0)
            
    # Apply and keyframe rotations
    for bone_name, rot_offset in rotations.items():
        pb = armature.pose.bones.get(bone_name)
        if pb:
            pb.rotation_mode = 'XYZ'
            pb.rotation_euler = rot_offset
            pb.keyframe_insert(data_path="rotation_euler", frame=f_start)
            
    # Restore armature active action to None (so NLA takes precedence)
    armature.animation_data.action = None
    
    # Add posture action as NLA strip
    track_posture = armature.animation_data.nla_tracks.new()
    track_posture.name = f"Posture_{mood_clean}_Track"
    strip = track_posture.strips.new(f"Posture_{mood_clean}", f_start, posture_action)
    strip.frame_end = f_end
    strip.blend_type = 'ADD'
    strip.extrapolation = 'HOLD'

def apply_shape_key_animations(mesh_obj, mood: str, viseme_timeline: list, f_start: int, f_end: int, fps: int):
    if not mesh_obj or not mesh_obj.data.shape_keys:
        return
        
    shape_keys = mesh_obj.data.shape_keys
    
    # 1. Clear existing animation data on shape keys
    if shape_keys.animation_data:
        shape_keys.animation_data_clear()
        
    # Standard mapping from emotions to blendshape intensity profiles
    EMOTION_TO_BLENDSHAPES = {
        "happy": {"mouthSmileLeft": 0.8, "mouthSmileRight": 0.8, "browInnerUp": 0.3, "cheekSquintLeft": 0.4, "cheekSquintRight": 0.4},
        "sad": {"mouthFrownLeft": 0.9, "mouthFrownRight": 0.9, "browOuterUpLeft": 0.5, "browOuterUpRight": 0.5, "eyeSquintLeft": 0.3, "eyeSquintRight": 0.3},
        "angry": {"browDownLeft": 1.0, "browDownRight": 1.0, "mouthPressLeft": 0.6, "mouthPressRight": 0.6, "eyeSquintLeft": 0.5, "eyeSquintRight": 0.5},
        "fear": {"jawOpen": 0.3, "mouthStretchLeft": 0.7, "mouthStretchRight": 0.7, "browInnerUp": 0.8, "eyeWideLeft": 0.6, "eyeWideRight": 0.6},
        "surprise": {"jawOpen": 0.6, "eyeWideLeft": 0.9, "eyeWideRight": 0.9, "browInnerUp": 0.9},
        "hope": {"mouthSmileLeft": 0.4, "mouthSmileRight": 0.4, "browInnerUp": 0.2},
        "determination": {"browDownLeft": 0.4, "browDownRight": 0.4, "mouthClose": 0.5, "mouthPressLeft": 0.5, "mouthPressRight": 0.5}
    }
    
    VISEME_TO_BLENDSHAPES = {
        "A": {"jawOpen": 0.8, "mouthFunnel": 0.2},
        "E": {"mouthStretchLeft": 0.6, "mouthStretchRight": 0.6, "jawOpen": 0.2},
        "F": {"mouthShrugLower": 0.5, "mouthClose": 0.3},
        "L": {"jawOpen": 0.4, "mouthPressLeft": 0.2},
        "M": {"mouthClose": 1.0},
        "O": {"mouthFunnel": 0.8, "jawOpen": 0.4},
        "rest": {"mouthClose": 0.5}
    }
    
    # Sort and prepare viseme timeline for coarticulation interpolation
    timeline = []
    if viseme_timeline:
        timeline = sorted(viseme_timeline, key=lambda x: x.get("time", 0.0))
    
    scene_dur_sec = (f_end - f_start) / fps
    if not timeline or timeline[0].get("time", 0.0) > 0.0:
        timeline.insert(0, {"time": 0.0, "viseme": "rest"})
    if timeline[-1].get("time", 0.0) < scene_dur_sec:
        timeline.append({"time": scene_dur_sec, "viseme": "rest"})
        
    mood_clean = mood.lower().strip()
    emotion_base = EMOTION_TO_BLENDSHAPES.get(mood_clean, {})
    
    # Identify all shape keys we intend to manipulate to keep others at 0.0
    all_manipulated_shapes = {
        "eyeBlinkLeft", "eyeLookDownLeft", "eyeLookInLeft", "eyeLookOutLeft", "eyeLookUpLeft", "eyeSquintLeft", "eyeWideLeft",
        "eyeBlinkRight", "eyeLookDownRight", "eyeLookInRight", "eyeLookOutRight", "eyeLookUpRight", "eyeSquintRight", "eyeWideRight",
        "jawForward", "jawLeft", "jawRight", "jawOpen", "mouthClose", "mouthFunnel", "mouthPucker", "mouthLeft", "mouthRight",
        "mouthSmileLeft", "mouthSmileRight", "mouthFrownLeft", "mouthFrownRight", "mouthDimpleLeft", "mouthDimpleRight",
        "mouthStretchLeft", "mouthStretchRight", "mouthRollLower", "mouthRollUpper", "mouthShrugLower", "mouthShrugUpper",
        "mouthPressLeft", "mouthPressRight", "mouthLowerDownLeft", "mouthLowerDownRight", "mouthUpperUpLeft", "mouthUpperUpRight",
        "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft", "browOuterUpRight", "cheekPuff", "cheekSquintLeft",
        "cheekSquintRight", "noseSneerLeft", "noseSneerRight", "tongueOut"
    }
    for shapes in EMOTION_TO_BLENDSHAPES.values():
        all_manipulated_shapes.update(shapes.keys())
    for shapes in VISEME_TO_BLENDSHAPES.values():
        all_manipulated_shapes.update(shapes.keys())
        
    # Pre-populate lists of shape keys available on this specific model
    model_keys = {}
    for name in all_manipulated_shapes:
        kb = shape_keys.key_blocks.get(name)
        if kb:
            model_keys[name] = kb

    # Animate frame-by-frame
    for f in range(f_start, f_end + 1):
        t = (f - f_start) / fps
        frame_values = {name: 0.0 for name in model_keys.keys()}
        
        # 1. Base Emotion with micro-expression sine-wave wiggles
        # Ease in the emotion over the first 6 frames of the scene
        ease_in = min(1.0, (f - f_start) / 6.0) if f_end > f_start else 1.0
        micro_variation = 1.0 + 0.08 * math.sin(f * 0.4) # slight 8% pulsing of emotion intensity
        
        for name, base_w in emotion_base.items():
            if name in frame_values:
                frame_values[name] = base_w * ease_in * micro_variation
                
        # 2. Eye Blinking: blink duration = 3 frames, happens every 4 seconds (48 frames)
        # Offset start frame by hash of mesh name to desynchronize multiple characters
        char_offset = hash(mesh_obj.name) % 17
        blink_cycle = 45 # frames
        local_f = (f - f_start + char_offset) % blink_cycle
        blink_weight = 0.0
        if local_f == 0 or local_f == 2:
            blink_weight = 0.5
        elif local_f == 1:
            blink_weight = 1.0
            
        if "eyeBlinkLeft" in frame_values:
            frame_values["eyeBlinkLeft"] = max(frame_values["eyeBlinkLeft"], blink_weight)
        if "eyeBlinkRight" in frame_values:
            frame_values["eyeBlinkRight"] = max(frame_values["eyeBlinkRight"], blink_weight)
            
        # 3. Eye Look Saccades: shifts eye lookup/lookin directions slightly every 1.5 seconds (18 frames)
        saccade_cycle = 18
        saccade_idx = (f - f_start + char_offset) // saccade_cycle
        # Deterministic pseudo-random look offset based on character and saccade index
        look_seed = hash(f"{mesh_obj.name}_{saccade_idx}")
        look_x = ((look_seed % 7) - 3) / 10.0 # -0.3 to 0.3
        look_y = (((look_seed // 7) % 7) - 3) / 10.0 # -0.3 to 0.3
        
        # Smoothly ease the saccadic shift over 3 frames
        saccade_local_f = (f - f_start + char_offset) % saccade_cycle
        saccade_blend = min(1.0, saccade_local_f / 3.0)
        curr_look_x = look_x * saccade_blend
        curr_look_y = look_y * saccade_blend
        
        if curr_look_x > 0:
            if "eyeLookOutLeft" in frame_values: frame_values["eyeLookOutLeft"] = curr_look_x
            if "eyeLookInRight" in frame_values: frame_values["eyeLookInRight"] = curr_look_x
        elif curr_look_x < 0:
            if "eyeLookInLeft" in frame_values: frame_values["eyeLookInLeft"] = -curr_look_x
            if "eyeLookOutRight" in frame_values: frame_values["eyeLookOutRight"] = -curr_look_x
            
        if curr_look_y > 0:
            if "eyeLookUpLeft" in frame_values: frame_values["eyeLookUpLeft"] = curr_look_y
            if "eyeLookUpRight" in frame_values: frame_values["eyeLookUpRight"] = curr_look_y
        elif curr_look_y < 0:
            if "eyeLookDownLeft" in frame_values: frame_values["eyeLookDownLeft"] = -curr_look_y
            if "eyeLookDownRight" in frame_values: frame_values["eyeLookDownRight"] = -curr_look_y

        # 4. Interpolate Lip Sync Coarticulation
        vis_weights = {}
        if len(timeline) == 1:
            vis_weights = VISEME_TO_BLENDSHAPES.get(timeline[0]["viseme"], {})
        else:
            # Find bracket
            found = False
            for i in range(len(timeline) - 1):
                t_curr = timeline[i]["time"]
                t_next = timeline[i+1]["time"]
                if t_curr <= t < t_next:
                    p = (t - t_curr) / (t_next - t_curr) if t_next > t_curr else 0.0
                    vis_a = timeline[i]["viseme"]
                    vis_b = timeline[i+1]["viseme"]
                    shapes_a = VISEME_TO_BLENDSHAPES.get(vis_a, {})
                    shapes_b = VISEME_TO_BLENDSHAPES.get(vis_b, {})
                    
                    # Blend the two viseme shape profiles
                    all_vis_shapes = set(shapes_a.keys()) | set(shapes_b.keys())
                    for sname in all_vis_shapes:
                        w_a = shapes_a.get(sname, 0.0)
                        w_b = shapes_b.get(sname, 0.0)
                        vis_weights[sname] = w_a + (w_b - w_a) * p
                    found = True
                    break
            if not found:
                vis_weights = VISEME_TO_BLENDSHAPES.get(timeline[-1]["viseme"], {})
                
        # Mix visemes into final frame values (max override to prevent mouth and emotion conflicts)
        for sname, w in vis_weights.items():
            if sname in frame_values:
                frame_values[sname] = max(frame_values[sname], w)
                
        # Apply to Blender shape keys and insert keyframe
        for name, val in frame_values.items():
            kb = model_keys[name]
            kb.value = min(1.0, max(0.0, val))
            kb.keyframe_insert(data_path="value", frame=f)
 
class RenderHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
 
    def do_POST(self):
        if self.path == '/render':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                payload = json.loads(post_data)
                
                output_path = payload.get("output_path")
                action_name = payload.get("action", "idle")
                duration = payload.get("duration", 2.0)
                state_file_path = payload.get("state_file_path", "")
                
                print(f"\n[BlenderDaemon] Received job: {action_name} for {duration}s -> {output_path}")
                
                t_start = time.time()
                fps = 12
                
                # --- Parse Multi-Character Payload ---
                characters = payload.get("characters")
                if not characters:
                    characters = [
                        {
                            "name": payload.get("character_name", "humanoid"),
                            "file": payload.get("character_file", CHARACTER_FILE),
                            "action": payload.get("action", "idle"),
                            "action_file": payload.get("action_file", ""),
                            "position": payload.get("start_location", [0.0, 0.0, 0.0]),
                            "rotation": payload.get("start_rotation", [0.0, 0.0, 0.0]),
                            "viseme_timeline": payload.get("viseme_timeline"),
                            "mood": payload.get("mood", "neutral")
                        }
                    ]
                    
                # Delete ALL existing armatures in the scene to prepare for fresh imports
                armatures_to_delete = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']
                for arm in armatures_to_delete:
                    bpy.data.objects.remove(arm, do_unlink=True)
                
                # Clear unused armature data blocks to avoid memory leak
                for arm_data in list(bpy.data.armatures):
                    if arm_data.users == 0:
                        bpy.data.armatures.remove(arm_data)
                
                # --- Continuity: Load State ---
                start_location = (0, 0, 0)
                start_rotation = (0, 0, 0)
                cam_location = None
                cam_rotation = None
                characters_state = {}
                env_seed = None
                if state_file_path and os.path.exists(state_file_path):
                    with open(state_file_path, "r") as sf:
                        try:
                            s_data = json.load(sf)
                            start_location = tuple(s_data.get("location", (0, 0, 0)))
                            start_rotation = tuple(s_data.get("rotation", (0, 0, 0)))
                            if "camera" in s_data:
                                cam_location = tuple(s_data["camera"].get("location", (0, 0, 0)))
                                cam_rotation = tuple(s_data["camera"].get("rotation", (0, 0, 0)))
                            characters_state = s_data.get("characters", {})
                            env_seed = s_data.get("env_seed", None)
                        except: pass


                
                # --- Configure Render Profile Settings ---
                profile_name = payload.get("render_profile", "testing").lower().strip()
                profiles = {
                    "development": {"res_x": 64, "res_y": 64, "samples": 1, "use_denoise": False},
                    "testing": {"res_x": 256, "res_y": 256, "samples": 2, "use_denoise": False},
                    "preview": {"res_x": 640, "res_y": 360, "samples": 4, "use_denoise": True},
                    "production": {"res_x": 1280, "res_y": 720, "samples": 8, "use_denoise": True},
                    "ultra": {"res_x": 1920, "res_y": 1080, "samples": 16, "use_denoise": True}
                }
                profile_opts = profiles.get(profile_name, profiles["testing"])
                
                print(f"[BlenderDaemon] Applying render profile: {profile_name} -> {profile_opts}")
                bpy.context.scene.render.resolution_x = profile_opts["res_x"]
                bpy.context.scene.render.resolution_y = profile_opts["res_y"]
                bpy.context.scene.cycles.samples = profile_opts["samples"]
                
                # Setup Denoising if requested
                if profile_opts["use_denoise"]:
                    bpy.context.scene.cycles.use_denoising = True
                else:
                    bpy.context.scene.cycles.use_denoising = False

                # --- Environment Composition ---
                location_str = payload.get("location", "environment")
                if PROJECT_DIR not in sys.path:
                    sys.path.append(PROJECT_DIR)
                try:
                    from environment_director import get_environment_for_location, build_environment_in_blender
                    env_config = get_environment_for_location(location_str)
                    weather_str = payload.get("weather", "clear")
                    props_list = payload.get("environment_props", [])
                    assets_list = payload.get("assets", [])
                    
                    # Use the primary character's parsed placement as reference position
                    ref_pos = characters[0].get("position", [0.0, 0.0, 0.0])
                    env_seed = build_environment_in_blender(env_config, ref_pos, weather_str, props_list, assets_list, env_seed=env_seed)
                except Exception as env_err:
                    print(f"[BlenderDaemon] Failed to build environment: {env_err}")

                # --- Story-Based Lighting Intelligence (AI Director Lighting Integration) ---
                mood_str = payload.get("mood", "neutral").lower().strip()
                # Default warm studio preset
                lighting_presets = {
                    "cheerful": {
                        "key_color": (1.0, 0.9, 0.7, 1.0), "key_energy": 5.0,
                        "fill_color": (1.0, 0.95, 0.85, 1.0), "fill_energy": 2.0,
                        "rim_color": (1.0, 1.0, 0.9, 1.0), "rim_energy": 3.5
                    },
                    "happy": {
                        "key_color": (1.0, 0.9, 0.7, 1.0), "key_energy": 5.0,
                        "fill_color": (1.0, 0.95, 0.85, 1.0), "fill_energy": 2.0,
                        "rim_color": (1.0, 1.0, 0.9, 1.0), "rim_energy": 3.5
                    },
                    "sad": {
                        "key_color": (0.6, 0.65, 0.8, 1.0), "key_energy": 2.0,
                        "fill_color": (0.5, 0.55, 0.7, 1.0), "fill_energy": 0.8,
                        "rim_color": (0.7, 0.75, 0.9, 1.0), "rim_energy": 1.5
                    },
                    "fear": {
                        "key_color": (0.3, 0.4, 0.6, 1.0), "key_energy": 1.5,
                        "fill_color": (0.2, 0.25, 0.4, 1.0), "fill_energy": 0.4,
                        "rim_color": (0.5, 0.6, 0.85, 1.0), "rim_energy": 2.5
                    },
                    "tense": {
                        "key_color": (0.35, 0.4, 0.55, 1.0), "key_energy": 1.8,
                        "fill_color": (0.2, 0.25, 0.35, 1.0), "fill_energy": 0.5,
                        "rim_color": (0.5, 0.6, 0.75, 1.0), "rim_energy": 2.0
                    },
                    "mysterious": {
                        "key_color": (0.4, 0.3, 0.6, 1.0), "key_energy": 1.2,  # low-key shadows
                        "fill_color": (0.15, 0.1, 0.25, 1.0), "fill_energy": 0.3,
                        "rim_color": (0.7, 0.5, 0.9, 1.0), "rim_energy": 3.0
                    },
                    "aggressive": {
                        "key_color": (1.0, 0.4, 0.3, 1.0), "key_energy": 6.0,  # strong warm orange key
                        "fill_color": (0.3, 0.1, 0.1, 1.0), "fill_energy": 1.0,
                        "rim_color": (1.0, 0.8, 0.6, 1.0), "rim_energy": 4.0
                    },
                    "triumphant": {
                        "key_color": (1.0, 0.95, 0.8, 1.0), "key_energy": 7.0,  # highly exposed glorious rim & key
                        "fill_color": (0.9, 0.85, 0.8, 1.0), "fill_energy": 2.5,
                        "rim_color": (1.0, 1.0, 1.0, 1.0), "rim_energy": 5.0
                    },
                    "neutral": {
                        "key_color": (1.0, 1.0, 1.0, 1.0), "key_energy": 4.0,
                        "fill_color": (1.0, 1.0, 1.0, 1.0), "fill_energy": 1.5,
                        "rim_color": (1.0, 1.0, 1.0, 1.0), "rim_energy": 3.0
                    }
                }
                
                lp = lighting_presets.get(mood_str, lighting_presets["neutral"])
                
                # Apply to KeyLight
                key_light = bpy.data.lights.get("KeyLight")
                if key_light:
                    key_light.energy = lp["key_energy"]
                    key_light.color = lp["key_color"][:3]
                
                # Apply to FillLight
                fill_light = bpy.data.lights.get("FillLight")
                if fill_light:
                    fill_light.energy = lp["fill_energy"]
                    fill_light.color = lp["fill_color"][:3]
                    
                # Apply to RimLight
                rim_light = bpy.data.lights.get("RimLight")
                if rim_light:
                    rim_light.energy = lp["rim_energy"]
                    rim_light.color = lp["rim_color"][:3]



                # --- Helper to find/lookup actions ---
                def find_action(action_name):
                    mapped_action = f"CharacterArmature|{action_name.capitalize()}"
                    if "run" in action_name.lower(): mapped_action = "CharacterArmature|Run"
                    elif "walk" in action_name.lower(): mapped_action = "CharacterArmature|Walk"
                    elif "jump" in action_name.lower(): mapped_action = "CharacterArmature|Jump_Idle"
                    elif "attack" in action_name.lower(): mapped_action = "CharacterArmature|Sword_Slash"
                    elif "wave" in action_name.lower(): mapped_action = "CharacterArmature|Wave"
                    
                    act = bpy.data.actions.get(mapped_action)
                    if not act:
                        for a in bpy.data.actions:
                            if a.name.startswith(mapped_action):
                                act = a
                                break
                    if not act:
                        act = bpy.data.actions.get("CharacterArmature|Idle")
                        if not act:
                            for a in bpy.data.actions:
                                if "idle" in a.name.lower():
                                    act = a
                                    break
                    return act

                # --- Import and Animate Characters ---
                primary_armature = None
                
                # Compute displacement offset for continuity (shift all characters if primary is shifted)
                primary_original_pos = characters[0].get("position", [0.0, 0.0, 0.0])
                if start_location != (0, 0, 0):
                    delta_x = start_location[0] - primary_original_pos[0]
                    delta_y = start_location[1] - primary_original_pos[1]
                else:
                    delta_x = 0.0
                    delta_y = 0.0

                for idx, char_data in enumerate(characters):
                    char_name = char_data["name"]
                    glb_file = char_data["file"]
                    if not glb_file or not os.path.exists(glb_file):
                        glb_file = CHARACTER_FILE
                        
                    # Import
                    pre_objs = set(bpy.data.objects)
                    try:
                        bpy.ops.import_scene.gltf(filepath=glb_file)
                    except Exception as imp_err:
                        print(f"[BlenderDaemon] Failed to import GLB for {char_name}: {imp_err}")
                        continue
                        
                    new_objs = set(bpy.data.objects) - pre_objs
                    
                    char_armature = None
                    char_meshes = []
                    for obj in new_objs:
                        if obj.type == 'ARMATURE':
                            char_armature = obj
                        elif obj.type == 'MESH':
                            char_meshes.append(obj)
                            
                    if not char_armature:
                        print(f"[BlenderDaemon] No armature found for character {char_name}")
                        continue
                        
                    # Rename to keep names unique
                    char_suffix = f"_{char_name}"
                    char_armature.name = f"Armature{char_suffix}"
                    for mesh_obj in char_meshes:
                        mesh_obj.name = f"{mesh_obj.name}{char_suffix}"
                        
                    # Calculate position with continuity delta shift
                    orig_pos = char_data.get("position", [0.0, 0.0, 0.0])
                    orig_rot = char_data.get("rotation", [0.0, 0.0, 0.0])
                    if char_name in characters_state:
                        pos_x, pos_y, pos_z = tuple(characters_state[char_name].get("location", orig_pos))
                        rot_x, rot_y, rot_z = tuple(characters_state[char_name].get("rotation", orig_rot))
                    else:
                        pos_x = orig_pos[0] + delta_x
                        pos_y = orig_pos[1] + delta_y
                        pos_z = orig_pos[2]
                        rot_x, rot_y, rot_z = tuple(orig_rot)
                    
                    char_armature.location = (pos_x, pos_y, pos_z)
                    char_armature.rotation_euler = (rot_x, rot_y, rot_z)
                    
                    # --- Character Memory Integration (Apply state scaling dynamically) ---
                    try:
                        from character_state_manager import CharacterStateManager
                        c_state_manager = CharacterStateManager()
                        c_profile_state = c_state_manager.get_character_state(char_name)
                        custom_scale = c_profile_state.get("scale", [1.0, 1.0, 1.0])
                        char_armature.scale = tuple(custom_scale)
                    except Exception as state_err:
                        print(f"[BlenderDaemon] CharacterStateManager state application failed: {state_err}")

                    
                    # Track primary armature
                    if idx == 0:
                        primary_armature = char_armature
                        
                    # Setup Animation Data
                    if not char_armature.animation_data:
                        char_armature.animation_data_create()
                    else:
                        char_armature.animation_data.action = None
                        while char_armature.animation_data.nla_tracks:
                            char_armature.animation_data.nla_tracks.remove(char_armature.animation_data.nla_tracks[0])
                            
                    # Reset pose bones
                    for pb in char_armature.pose.bones:
                        pb.rotation_euler = (0.0, 0.0, 0.0)
                        pb.location = (0.0, 0.0, 0.0)
                        pb.scale = (1.0, 1.0, 1.0)
                        
                    # Assign Action
                    selected_action = find_action(char_data["action"])
                    if selected_action:
                        track_base = char_armature.animation_data.nla_tracks.new()
                        track_base.name = "Base_Track"
                        f_start = int(selected_action.frame_range[0])
                        f_end = int(selected_action.frame_range[1])
                        strip_base = track_base.strips.new("BaseAnimation", f_start, selected_action)
                        strip_base.frame_end = f_start + int(duration * fps)
                        
                    # Apply custom emotional posture
                    mood_str = char_data.get("mood", "neutral")
                    try:
                        apply_emotion_posture(char_armature, mood_str, 1, int(duration * fps))
                    except Exception as mood_err:
                        print(f"[BlenderDaemon] Failed to apply posture to {char_name}: {mood_err}")
                        
                    # Apply shape key animations (emotions & visemes)
                    viseme_timeline = char_data.get("viseme_timeline", None)
                    head_mesh = None
                    for mesh_obj in char_meshes:
                        if "head" in mesh_obj.name.lower() or "fox" in mesh_obj.name.lower():
                            head_mesh = mesh_obj
                            break
                            
                    if head_mesh:
                        try:
                            apply_shape_key_animations(head_mesh, mood_str, viseme_timeline, 1, int(duration * fps), fps)
                        except Exception as sk_err:
                            print(f"[BlenderDaemon] Failed to apply shape key animations to {char_name}: {sk_err}")

                    # --- Procedural Breathing Animation (V2 Hollywood Quality) ---
                    try:
                        spine_bone = char_armature.pose.bones.get("Spine") or char_armature.pose.bones.get("spine")
                        if spine_bone:
                            spine_bone.rotation_mode = 'XYZ'
                            for f in range(1, int(duration * fps) + 1):
                                # Rhythmic breathing sine wave: 0.02 radians (~1.1 degrees)
                                breath_angle = 0.02 * math.sin(f * 0.15)
                                spine_bone.rotation_euler.x = breath_angle
                                spine_bone.keyframe_insert(data_path="rotation_euler", frame=f)
                    except Exception as breath_err:
                        print(f"[BlenderDaemon] Breathing animation error for {char_name}: {breath_err}")

                    # --- Conversation Eye Contact Head-Tracking (AI Director specs) ---
                    # If multiple characters, make listeners look at the primary character armature position
                    if len(characters) > 1 and idx > 0 and primary_armature:
                        try:
                            # Direct bone rotation toward target
                            neck_bone = char_armature.pose.bones.get("Neck")
                            head_bone = char_armature.pose.bones.get("Head")
                            if neck_bone and head_bone:
                                neck_bone.rotation_mode = 'XYZ'
                                head_bone.rotation_mode = 'XYZ'
                                
                                # Compute simple Euler rotation looking at the primary armature location
                                dx = primary_armature.location.x - char_armature.location.x
                                dy = primary_armature.location.y - char_armature.location.y
                                angle_to_primary = math.atan2(dx, dy)
                                
                                # Animate head look rotation over the frame range
                                for f in range(1, int(duration * fps) + 1):
                                    # Add small natural head wiggles/nods
                                    head_nod = 0.05 * math.sin(f * 0.2)
                                    head_bone.rotation_euler = (head_nod, 0, angle_to_primary * 0.5)
                                    head_bone.keyframe_insert(data_path="rotation_euler", frame=f)
                        except Exception as track_err:
                            print(f"[BlenderDaemon] Head tracking error for {char_name}: {track_err}")
                            
                    # Customize character materials & weapons
                    outfits_list = payload.get("outfits", [])
                    held_item = payload.get("held_item", None)
                    try:
                        customize_character(char_name, held_item, outfits_list)
                    except Exception as char_err:
                        print(f"[BlenderDaemon] Failed to customize character {char_name}: {char_err}")

                # Configure global frame bounds
                bpy.context.scene.frame_start = 1
                bpy.context.scene.frame_end = int(duration * fps)
                f_start = 1
                f_end = int(duration * fps)

                # Camera framing setup
                camera = None
                for obj in bpy.context.scene.objects:
                    if obj.type == 'CAMERA':
                        camera = obj
                        break
                if not camera:
                    cam_data = bpy.data.cameras.new("Camera")
                    camera = bpy.data.objects.new("Camera", cam_data)
                    bpy.context.collection.objects.link(camera)
                
                bpy.context.scene.camera = camera
                camera.location = (0, -4, 1.5)
                camera.rotation_euler = (math.radians(80), 0, 0)

                # Cinematic Camera depth of field configuration (Priority 2: Shot Composition)
                camera.data.dof.use_dof = True
                if primary_armature:
                    camera.data.dof.focus_object = primary_armature
                else:
                    camera.data.dof.focus_distance = 4.0
                camera.data.dof.aperture_fstop = 2.8 # F/2.8 cinematic background blur

                # Update camera target position based on primary character
                if primary_armature:
                    start_location = primary_armature.location
                    start_rotation = primary_armature.rotation_euler

                # Camera Framing offsets and timeline configuration
                camera_timeline = payload.get("camera_timeline", None)
                
                shot_presets = {
                    "wide_shot": ((0, -6.0, 2.2), (math.radians(75), 0, 0)),
                    "medium_shot": ((0, -3.0, 1.8), (math.radians(80), 0, 0)),
                    "close_up": ((0, -1.2, 1.6), (math.radians(90), 0, 0)),
                    "establishing_shot": ((0, -12.0, 6.0), (math.radians(65), 0, 0)),
                    "over_shoulder": ((0.5, 1.0, 1.6), (math.radians(85), 0, math.radians(180))),
                    "tracking_shot": ((2.0, -3.5, 1.5), (math.radians(80), 0, math.radians(-25))),
                    "orbit_shot": ((-3.0, -3.0, 2.0), (math.radians(80), 0, math.radians(-45))),
                    "low_angle": ((0, -2.5, 0.5), (math.radians(100), 0, 0)),
                    "high_angle": ((0, -3.5, 3.5), (math.radians(55), 0, 0))
                }
                
                def get_shot_preset(name):
                    name_clean = str(name).lower().strip().replace(" ", "_")
                    for k, v in shot_presets.items():
                        if k in name_clean or name_clean in k:
                            return v
                    return shot_presets["wide_shot"]

                if camera_timeline:
                    if camera.animation_data:
                        camera.animation_data_clear()
                        
                    for kf in camera_timeline:
                        frame = kf["frame"]
                        if "location" in kf and "rotation" in kf:
                            camera.location = tuple(kf["location"])
                            camera.rotation_euler = tuple(kf["rotation"])
                        else:
                            shot_name = kf.get("camera_shot", "wide_shot")
                            offset, rot = get_shot_preset(shot_name)
                            
                            factor = kf.get("loc_factor", 0.0)
                            
                            # Calculate character locomotion position delta
                            delta_loc = [0.0, 0.0, 0.0]
                            aname = action_name.lower()
                            if "walk" in aname:
                                delta_loc = [0.0, -1.0 * duration * factor, 0.0]
                            elif "run" in aname:
                                delta_loc = [0.0, -3.0 * duration * factor, 0.0]
                            elif "jump" in aname:
                                delta_loc = [0.0, -0.5 * duration * factor, 0.0]
                                
                            char_pos = [start_location[0] + delta_loc[0],
                                        start_location[1] + delta_loc[1],
                                        start_location[2] + delta_loc[2]]
                                        
                            camera.location = (char_pos[0] + offset[0], 
                                               char_pos[1] + offset[1], 
                                               char_pos[2] + offset[2])
                            camera.rotation_euler = rot
                        
                        # Dynamic focal length, FOV, and Depth of Field setup from AI Director Timeline
                        focal_len = kf.get("focal_length", 35.0)  # default cinematic 35mm
                        lens_unit = kf.get("lens_unit", "MILLIMETERS")
                        camera.data.lens = focal_len
                        
                        dof_aperture = kf.get("aperture_fstop", 2.8)
                        camera.data.dof.aperture_fstop = dof_aperture
                        camera.data.dof.use_dof = kf.get("use_dof", True)
                        
                        camera.keyframe_insert(data_path="location", frame=frame)
                        camera.keyframe_insert(data_path="rotation_euler", frame=frame)
                        camera.data.keyframe_insert(data_path="lens", frame=frame)
                        camera.data.dof.keyframe_insert(data_path="aperture_fstop", frame=frame)
                        
                    if camera.animation_data and camera.animation_data.action:
                        try:
                            if hasattr(camera.animation_data.action, "fcurves"):
                                for fcurve in camera.animation_data.action.fcurves:
                                    for kp in fcurve.keyframe_points:
                                        kp.interpolation = "CONSTANT"
                            elif hasattr(camera.animation_data.action, "curves"):
                                for curve in camera.animation_data.action.curves:
                                    for kp in curve.keyframe_points:
                                        kp.interpolation = "CONSTANT"
                        except Exception as interp_err:
                            print(f"[BlenderDaemon] Failed to set camera keyframe interpolation: {interp_err}")
                else:
                    # Fallback single camera logic
                    camera_shot = payload.get("camera_shot", payload.get("camera", "wide_shot")).lower()
                    cam_offset, cam_rot = get_shot_preset(camera_shot)
                    
                    if not cam_location:
                        camera.location = (start_location[0] + cam_offset[0], 
                                           start_location[1] + cam_offset[1], 
                                           start_location[2] + cam_offset[2])
                        camera.rotation_euler = cam_rot
                    else:
                        camera.location = cam_location
                        camera.rotation_euler = cam_rotation
                        
                # Update depsgraph to lock transforms
                bpy.context.view_layer.update()
                
                # Render
                import tempfile
                render_dir = tempfile.mkdtemp(prefix="blender_daemon_")
                bpy.context.scene.render.image_settings.file_format = 'PNG'
                bpy.context.scene.render.image_settings.color_mode = 'RGBA'
                bpy.context.scene.render.filepath = os.path.join(render_dir, "frame_")
                
                t_render_start = time.time()
                bpy.ops.render.render(animation=True)
                t_render_end = time.time()
                
                # FFmpeg
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                ffmpeg_cmd = [
                    "ffmpeg", "-y", "-framerate", str(fps),
                    "-i", os.path.join(render_dir, "frame_%04d.png"),
                    "-c:v", "h264_nvenc", "-pix_fmt", "yuv420p", "-preset", "fast", "-b:v", "2M",
                    output_path
                ]
                t_ffmpeg_start = time.time()
                try:
                    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except:
                    ffmpeg_cmd_sw = ["ffmpeg", "-y", "-framerate", str(fps), "-i", os.path.join(render_dir, "frame_%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", output_path]
                    subprocess.run(ffmpeg_cmd_sw, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                t_ffmpeg_end = time.time()
                
                # Thumb
                first_frame_src = os.path.join(render_dir, f"frame_{str(f_start).zfill(4)}.png")
                storyboard_out = output_path.replace(".mp4", "_thumb.png")
                if os.path.exists(first_frame_src):
                    shutil.copy(first_frame_src, storyboard_out)
                    
                shutil.rmtree(render_dir, ignore_errors=True)
                
                # --- Continuity: Save State ---
                if state_file_path and primary_armature:
                    bpy.context.scene.frame_set(f_end)
                    bpy.context.view_layer.update()
                    
                    delta_loc = [0.0, 0.0, 0.0]
                    aname = characters[0]["action"].lower()
                    if "walk" in aname:
                        delta_loc = [0.0, -1.0 * duration, 0.0]
                    elif "run" in aname:
                        delta_loc = [0.0, -3.0 * duration, 0.0]
                    elif "jump" in aname:
                        delta_loc = [0.0, -0.5 * duration, 0.0]
                        
                    final_loc = [primary_armature.location.x + delta_loc[0], primary_armature.location.y + delta_loc[1], primary_armature.location.z]
                    final_rot = [primary_armature.rotation_euler.x, primary_armature.rotation_euler.y, primary_armature.rotation_euler.z]
                    cam_loc = [camera.location.x + delta_loc[0], camera.location.y + delta_loc[1], camera.location.z]
                    cam_rot = [camera.rotation_euler.x, camera.rotation_euler.y, camera.rotation_euler.z]
                    
                    # Save states for ALL active characters
                    chars_dict = {}
                    for char_data in characters:
                        cname = char_data["name"]
                        char_suffix = f"_{cname}"
                        char_obj = bpy.context.scene.objects.get(f"Armature{char_suffix}")
                        if char_obj:
                            c_delta = [0.0, 0.0, 0.0]
                            c_aname = char_data["action"].lower()
                            if "walk" in c_aname:
                                c_delta = [0.0, -1.0 * duration, 0.0]
                            elif "run" in c_aname:
                                c_delta = [0.0, -3.0 * duration, 0.0]
                            elif "jump" in c_aname:
                                c_delta = [0.0, -0.5 * duration, 0.0]
                            
                            c_final_loc = [char_obj.location.x + c_delta[0], char_obj.location.y + c_delta[1], char_obj.location.z]
                            c_final_rot = [char_obj.rotation_euler.x, char_obj.rotation_euler.y, char_obj.rotation_euler.z]
                            chars_dict[cname] = {
                                "location": c_final_loc,
                                "rotation": c_final_rot
                            }
                    
                    state_data = {
                        "location": final_loc,
                        "rotation": final_rot,
                        "camera": {
                            "location": cam_loc,
                            "rotation": cam_rot
                        },
                        "characters": chars_dict,
                        "env_seed": env_seed,
                        "previous_action": characters[0]["action"]
                    }
                    with open(state_file_path, "w") as sf:
                        json.dump(state_data, sf)


                        
                response = {
                    "status": "success",
                    "output_path": output_path,
                    "timings": {
                        "render_time": t_render_end - t_render_start,
                        "ffmpeg_time": t_ffmpeg_end - t_ffmpeg_start,
                        "total_time": time.time() - t_start
                    }
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                import traceback
                print("[BlenderDaemon] EXCEPTION IN HANDLER:")
                traceback.print_exc()
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "error": str(e)}).encode())

if __name__ == "__main__":
    init_blender_env()
    server = HTTPServer(('127.0.0.1', PORT), RenderHandler)
    print(f"[BlenderDaemon] Listening on port {PORT}...")
    server.serve_forever()
