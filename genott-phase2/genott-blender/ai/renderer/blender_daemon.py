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

    # 2. Setup GPU
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.cycles.samples = 1
    bpy.context.scene.render.resolution_x = 64
    bpy.context.scene.render.resolution_y = 64
    bpy.context.scene.render.fps = 12
    
    # 3. Import Character
    if os.path.exists(CHARACTER_FILE):
        bpy.ops.import_scene.gltf(filepath=CHARACTER_FILE)
    
    # 4. Setup Lighting
    light_data = bpy.data.lights.new(name="SunLight", type='SUN')
    light_data.energy = 3.0
    light_obj = bpy.data.objects.new(name="SunLight", object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = (5, -5, 10)
    
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
        
    # 2. Reset all shape keys to 0.0 at the first frame
    for kb in shape_keys.key_blocks:
        if kb.name != "Basis":
            kb.value = 0.0
            kb.keyframe_insert(data_path="value", frame=f_start)
            
    # 3. Apply static emotional pose (emotions)
    EMOTION_TO_BLENDSHAPES = {
        "happy": {"mouthSmileLeft": 0.8, "mouthSmileRight": 0.8, "browInnerUp": 0.3},
        "sad": {"mouthFrownLeft": 0.9, "mouthFrownRight": 0.9, "browOuterUpLeft": 0.5, "browOuterUpRight": 0.5},
        "angry": {"browDownLeft": 1.0, "browDownRight": 1.0, "mouthPressLeft": 0.6, "mouthPressRight": 0.6},
        "fear": {"jawOpen": 0.3, "mouthStretchLeft": 0.7, "mouthStretchRight": 0.7, "browInnerUp": 0.8, "eyeWideLeft": 0.6, "eyeWideRight": 0.6},
        "surprise": {"jawOpen": 0.6, "eyeWideLeft": 0.9, "eyeWideRight": 0.9, "browInnerUp": 0.9},
        "hope": {"mouthSmileLeft": 0.4, "mouthSmileRight": 0.4, "browInnerUp": 0.2},
        "determination": {"browDownLeft": 0.4, "browDownRight": 0.4, "mouthClose": 0.4}
    }
    
    mood_clean = mood.lower().strip()
    emotion_weights = EMOTION_TO_BLENDSHAPES.get(mood_clean, {})
    for shape_name, weight in emotion_weights.items():
        kb = shape_keys.key_blocks.get(shape_name)
        if kb:
            kb.value = weight
            kb.keyframe_insert(data_path="value", frame=f_start)
            # Maintain this emotion at the end of the scene too
            kb.keyframe_insert(data_path="value", frame=f_end)
            
    # 4. Apply viseme lip sync over time
    if viseme_timeline:
        VISEME_TO_BLENDSHAPES = {
            "A": {"jawOpen": 0.8, "mouthFunnel": 0.2},
            "E": {"mouthStretchLeft": 0.6, "mouthStretchRight": 0.6, "jawOpen": 0.2},
            "F": {"mouthShrugLower": 0.5, "mouthClose": 0.3},
            "L": {"jawOpen": 0.4, "mouthPressLeft": 0.2},
            "M": {"mouthClose": 1.0},
            "O": {"mouthFunnel": 0.8, "jawOpen": 0.4},
            "rest": {"mouthClose": 0.5}
        }
        
        # All shape keys used in visemes
        viseme_shapes = set()
        for shapes in VISEME_TO_BLENDSHAPES.values():
            viseme_shapes.update(shapes.keys())
            
        for entry in viseme_timeline:
            time_sec = entry.get("time", 0.0)
            vis = entry.get("viseme", "rest")
            
            frame = int(f_start + (time_sec * fps))
            if frame > f_end:
                frame = f_end
                
            # First set all viseme shape keys to 0.0 at this frame to avoid accumulation
            for shape_name in viseme_shapes:
                kb = shape_keys.key_blocks.get(shape_name)
                if kb:
                    kb.value = 0.0
                    
            # Apply active viseme weights
            active_shapes = VISEME_TO_BLENDSHAPES.get(vis, VISEME_TO_BLENDSHAPES["rest"])
            for shape_name, weight in active_shapes.items():
                kb = shape_keys.key_blocks.get(shape_name)
                if kb:
                    kb.value = weight
                    
            # Insert keyframes for all viseme shape keys at this frame
            for shape_name in viseme_shapes:
                kb = shape_keys.key_blocks.get(shape_name)
                if kb:
                    kb.keyframe_insert(data_path="value", frame=frame)
 
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
                if state_file_path and os.path.exists(state_file_path):
                    with open(state_file_path, "r") as sf:
                        try:
                            s_data = json.load(sf)
                            start_location = tuple(s_data.get("location", (0, 0, 0)))
                            start_rotation = tuple(s_data.get("rotation", (0, 0, 0)))
                            if "camera" in s_data:
                                cam_location = tuple(s_data["camera"].get("location", (0, 0, 0)))
                                cam_rotation = tuple(s_data["camera"].get("rotation", (0, 0, 0)))
                        except: pass
                
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
                    build_environment_in_blender(env_config, ref_pos, weather_str, props_list, assets_list)
                except Exception as env_err:
                    print(f"[BlenderDaemon] Failed to build environment: {env_err}")

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
                    pos_x = orig_pos[0] + delta_x
                    pos_y = orig_pos[1] + delta_y
                    pos_z = orig_pos[2]
                    
                    char_armature.location = (pos_x, pos_y, pos_z)
                    char_armature.rotation_euler = tuple(char_data.get("rotation", [0.0, 0.0, 0.0]))
                    
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
                        
                        camera.keyframe_insert(data_path="location", frame=frame)
                        camera.keyframe_insert(data_path="rotation_euler", frame=frame)
                        
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
                    
                    state_data = {
                        "location": final_loc,
                        "rotation": final_rot,
                        "camera": {
                            "location": cam_loc,
                            "rotation": cam_rot
                        },
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
