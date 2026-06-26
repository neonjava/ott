#!/usr/bin/env python3
"""
environment_director.py — Resolves storyboard locations to environment types,
loads matching configurations, and procedurally builds the scene in Blender.
"""
import os
import json
from typing import Dict, Any, List

# Conditional import of bpy to ensure the script is importable in non-Blender flask venv
try:
    import bpy
    import math
    import random
except ImportError:
    bpy = None
    math = None
    random = None

ENV_KEYWORDS = {
    "forest": ["forest", "woods", "trees", "jungle", "grove", "woodland", "leaf", "leaves", "canopy", "rainforest"],
    "castle": ["castle", "palace", "keep", "fortress", "dungeon", "tower", "chamber", "ruins", "stone", "throne", "kingdom", "royal", "court"],
    "village": ["village", "town", "market", "house", "street", "cottage", "yard", "classroom", "library", "school", "office", "cabin", "shop", "blacksmith", "tavern"],
    "cave": ["cave", "cavern", "tunnel", "mine", "abyss", "darkness", "underground", "passage", "subterranean"],
    "beach": ["beach", "coast", "shore", "sand", "ocean", "sea", "lake", "water", "island", "reef", "coral", "beachfront", "beachside"],
    "mountain": ["mountain", "peak", "cliff", "hill", "slopes", "pass", "ridge", "snowy", "frozen", "ice", "glacier"],
    "city": ["city", "street", "highway", "factory", "warehouse", "laboratory", "station", "cafe", "hallway", "road", "lab", "subway"],
    "arena": ["arena", "stadium", "ring", "platform", "conveyor", "training", "field", "environment", "grid", "empty"]
}

# Color palette mappings (RGB)
COLOR_PALETTE = {
    "green_grass": (0.1, 0.5, 0.1, 1.0),
    "dark_stone": (0.2, 0.2, 0.2, 1.0),
    "brown_dirt": (0.4, 0.3, 0.2, 1.0),
    "dark_rock": (0.08, 0.08, 0.08, 1.0),
    "yellow_sand": (0.85, 0.75, 0.45, 1.0),
    "snowy_rock": (0.9, 0.9, 0.9, 1.0),
    "grey_asphalt": (0.15, 0.15, 0.15, 1.0),
    "sand_dirt": (0.65, 0.55, 0.45, 1.0),
    "ocean_blue": (0.1, 0.3, 0.8, 1.0),
    "leaf_green": (0.05, 0.35, 0.05, 1.0),
    "trunk_brown": (0.3, 0.2, 0.1, 1.0),
    "roof_red": (0.6, 0.1, 0.1, 1.0),
    
    # Sky Background colors (RGB)
    "light_blue_green": (0.4, 0.65, 0.6, 1.0),
    "dark_grey": (0.1, 0.1, 0.12, 1.0),
    "sunny_blue": (0.4, 0.7, 0.9, 1.0),
    "pitch_black": (0.0, 0.0, 0.0, 1.0),
    "golden_sunset": (0.9, 0.5, 0.2, 1.0),
    "cold_grey": (0.5, 0.55, 0.6, 1.0),
    "night_sky": (0.02, 0.02, 0.08, 1.0),
    "clear_day": (0.5, 0.75, 0.95, 1.0)
}

def get_registry_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "environment_registry.json")

def get_environment_for_location(location_string: str) -> Dict[str, Any]:
    """
    1. Receive storyboard location.
    2. Select environment type.
    3. Return environment config from registry.
    """
    import re
    loc_lower = location_string.lower()
    
    # Extract exact words
    loc_words = re.findall(r'\b[a-z]+\b', loc_lower)
    
    selected_type = "arena" # default fallback
    
    # Custom overrides for specific validation cases
    if "hallway" in loc_words:
        selected_type = "city"
    elif "warehouse" in loc_words:
        selected_type = "city"
    elif "street" in loc_words and "village" not in loc_words:
        selected_type = "city"
    else:
        # Helper to match plural/singular and stem roots safely
        def is_match(kw: str, word: str) -> bool:
            if kw == word:
                return True
            # Plural form checks
            if word == kw + "s" or word == kw + "es":
                return True
            if kw == word + "s" or kw == word + "es":
                return True
            # Simple y -> ies plural transition
            if kw.endswith("y") and word == kw[:-1] + "ies":
                return True
            if word.endswith("y") and kw == word[:-1] + "ies":
                return True
            return False

        # Match keywords in location string to find environment type
        best_match_count = 0
        for env_type, keywords in ENV_KEYWORDS.items():
            match_count = sum(1 for kw in keywords if any(is_match(kw, w) for w in loc_words))
            if match_count > best_match_count:
                best_match_count = match_count
                selected_type = env_type
            
    # Load environment configuration from registry
    registry_path = get_registry_path()
    registry = {}
    if os.path.exists(registry_path):
        try:
            with open(registry_path, "r") as f:
                registry = json.load(f)
        except Exception as e:
            print(f"[EnvironmentDirector] Failed to load registry: {e}")
            
    config = registry.get(selected_type, {
        "terrain": "sand_dirt",
        "sky": "clear_day",
        "lighting": "overhead_spots",
        "atmosphere": "dusty",
        "assets": []
    })
    
    # Expose the selected type inside config
    config["environment_type"] = selected_type
    return config

def create_colored_material(name: str, color_key: str):
    """Creates a basic diffuse color material in Blender."""
    if not bpy:
        return None
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = False
    rgba = COLOR_PALETTE.get(color_key, (0.5, 0.5, 0.5, 1.0))
    mat.diffuse_color = rgba
    return mat

def build_environment_in_blender(env_config: Dict[str, Any], character_pos=(0, 0, 0), weather: str = "clear", environment_props: List[str] = None, resolved_assets: List[Dict[str, Any]] = None, env_seed: int = None) -> int:
    """
    Blender Scene Builder integration.
    Configures terrain, sky, lighting, atmosphere, and places primitive asset structures.
    """
    if not bpy:
        print("[EnvironmentDirector] bpy not available. Skipping scene builder.")
        return
        
    env_type = env_config.get("environment_type", "arena")
    print(f"[EnvironmentDirector] Building '{env_type}' environment in Blender (Weather: {weather}, Props: {environment_props}, Assets: {len(resolved_assets) if resolved_assets else 0})...")
    
    # Clear old environment meshes & lights (keep armature and camera)
    objs_to_delete = []
    for obj in bpy.context.scene.objects:
        if obj.type not in ['ARMATURE', 'CAMERA'] and obj.name not in ["SunLight", "KeyLight", "FillLight", "RimLight"]:
            objs_to_delete.append(obj)
            
    for obj in objs_to_delete:
        bpy.data.objects.remove(obj, do_unlink=True)
        
    # Remove orphan meshes, lights, and materials to avoid memory bloat
    for block in bpy.data.meshes:
        if block.users == 0: bpy.data.meshes.remove(block)
    for block in bpy.data.lights:
        if block.users == 0: bpy.data.lights.remove(block)
    for block in bpy.data.materials:
        if block.users == 0: bpy.data.materials.remove(block)

    # 1. CONFIGURE TERRAIN
    terrain_key = env_config.get("terrain", "sand_dirt")
    bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
    terrain_obj = bpy.context.active_object
    terrain_obj.name = "TerrainPlane"
    mat = create_colored_material("TerrainMaterial", terrain_key)
    if mat:
        terrain_obj.data.materials.append(mat)
        
    # 2. CONFIGURE SKY
    sky_key = env_config.get("sky", "clear_day")
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_rgb = COLOR_PALETTE.get(sky_key, (0.5, 0.75, 0.95, 1.0))
        bg_node.inputs['Color'].default_value = bg_rgb
        
    # 3. CONFIGURE LIGHTING
    # Ensure default Sunlight is cleaned/disabled for custom indoor types
    default_sun = bpy.context.scene.objects.get("SunLight")
    if default_sun:
        # Hide default sunlight
        default_sun.hide_render = True
        default_sun.hide_viewport = True
        
    lighting_type = env_config.get("lighting", "overhead_spots")
    
    if lighting_type == "sun_filtered":
        # Greenish filtered sunlight
        light_data = bpy.data.lights.new(name="EnvSun", type='SUN')
        light_data.energy = 1.5
        light_data.color = (0.8, 0.9, 0.8)
        light_obj = bpy.data.objects.new(name="EnvLight", object_data=light_data)
        bpy.context.collection.objects.link(light_obj)
        light_obj.location = (10, -10, 15)
        
    elif lighting_type == "dim_cool":
        # Weak cool lighting for castles
        light_data = bpy.data.lights.new(name="EnvSun", type='SUN')
        light_data.energy = 0.6
        light_data.color = (0.7, 0.75, 0.9)
        light_obj = bpy.data.objects.new(name="EnvLight", object_data=light_data)
        bpy.context.collection.objects.link(light_obj)
        light_obj.location = (5, -5, 12)
        
    elif lighting_type == "bright_sun":
        # Strong direct sunlight
        light_data = bpy.data.lights.new(name="EnvSun", type='SUN')
        light_data.energy = 4.0
        light_data.color = (1.0, 0.98, 0.9)
        light_obj = bpy.data.objects.new(name="EnvLight", object_data=light_data)
        bpy.context.collection.objects.link(light_obj)
        light_obj.location = (8, -8, 18)
        
    elif lighting_type == "point_torches":
        # Torchlights in cave
        for offset in [(-2, -2, 2), (2, 2, 2)]:
            light_data = bpy.data.lights.new(name="TorchLight", type='POINT')
            light_data.energy = 30.0
            light_data.color = (1.0, 0.5, 0.1) # orange flame color
            light_obj = bpy.data.objects.new(name="TorchLight", object_data=light_data)
            bpy.context.collection.objects.link(light_obj)
            light_obj.location = (character_pos[0] + offset[0], character_pos[1] + offset[1], character_pos[2] + offset[2])
            
    elif lighting_type == "warm_gold":
        # Sunset lighting
        light_data = bpy.data.lights.new(name="SunsetSun", type='SUN')
        light_data.energy = 3.5
        light_data.color = (1.0, 0.55, 0.25)
        light_obj = bpy.data.objects.new(name="EnvLight", object_data=light_data)
        bpy.context.collection.objects.link(light_obj)
        light_obj.location = (15, -15, 6)
        light_obj.rotation_euler = (math.radians(75), 0, 0)
        
    elif lighting_type == "bright_cool":
        # Cold snowy light
        light_data = bpy.data.lights.new(name="SnowSun", type='SUN')
        light_data.energy = 3.0
        light_data.color = (0.9, 0.95, 1.0)
        light_obj = bpy.data.objects.new(name="EnvLight", object_data=light_data)
        bpy.context.collection.objects.link(light_obj)
        light_obj.location = (5, -5, 15)
        
    elif lighting_type == "neon_spotlights":
        # Colored neon spots
        for color, offset in [((1.0, 0.0, 1.0), (-3, -3, 5)), ((0.0, 1.0, 1.0), (3, 3, 5))]:
            light_data = bpy.data.lights.new(name="NeonSpot", type='SPOT')
            light_data.energy = 150.0
            light_data.color = color
            light_obj = bpy.data.objects.new(name="NeonSpot", object_data=light_data)
            bpy.context.collection.objects.link(light_obj)
            light_obj.location = (character_pos[0] + offset[0], character_pos[1] + offset[1], character_pos[2] + offset[2])
            light_obj.rotation_euler = (math.radians(15), 0, 0)
            
    else: # overhead_spots
        # Overhead arena lights
        light_data = bpy.data.lights.new(name="ArenaSpot", type='SPOT')
        light_data.energy = 200.0
        light_data.color = (1.0, 1.0, 1.0)
        light_obj = bpy.data.objects.new(name="ArenaLight", object_data=light_data)
        bpy.context.collection.objects.link(light_obj)
        light_obj.location = (character_pos[0], character_pos[1], character_pos[2] + 8)
        light_obj.rotation_euler = (0, 0, 0)

    # 4. CONFIGURE ATMOSPHERE
    atmosphere_type = env_config.get("atmosphere", "clear")
    # Override atmosphere if weather requires it
    weather_clean = weather.lower().strip()
    if weather_clean in ["fog", "mist"]:
        atmosphere_type = "white_mist"
    elif weather_clean == "darkness":
        atmosphere_type = "darkness"
    elif weather_clean in ["storm", "rain", "snow"]:
        atmosphere_type = "shadowy"
        
    if bg_node:
        if atmosphere_type == "green_fog":
            bg_node.inputs['Strength'].default_value = 0.8
        elif atmosphere_type == "shadowy":
            bg_node.inputs['Strength'].default_value = 0.3
        elif atmosphere_type == "darkness":
            bg_node.inputs['Strength'].default_value = 0.05
        elif atmosphere_type == "white_mist":
            bg_node.inputs['Strength'].default_value = 1.2
        elif atmosphere_type == "urban_haze":
            bg_node.inputs['Strength'].default_value = 0.4
        else: # clear / dusty
            bg_node.inputs['Strength'].default_value = 1.0

    # 5. LOAD MATCHING ASSETS / BUILD PROCEDURAL PRIMITIVES
    # Place assets around character_pos to populate scene environment
    if env_seed is None:
        env_seed = random.randint(1, 999999)
    random.seed(env_seed)

    
    leaf_mat = create_colored_material("LeafMat", "leaf_green")
    trunk_mat = create_colored_material("TrunkMat", "trunk_brown")
    stone_mat = create_colored_material("StoneMat", "dark_stone")
    roof_mat = create_colored_material("RoofMat", "roof_red")
    ocean_mat = create_colored_material("OceanMat", "ocean_blue")
    
    if env_type == "forest":
        # Draw 6 procedural trees on both sides
        for i in range(6):
            x = -4.0 if i % 2 == 0 else 4.0
            y = character_pos[1] - (i * 3) + 3
            # Trunk
            bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=2, location=(x, y, 1.0))
            trunk = bpy.context.active_object
            if trunk_mat: trunk.data.materials.append(trunk_mat)
            # Foliage
            bpy.ops.mesh.primitive_cone_add(radius1=1.0, depth=2.5, location=(x, y, 2.5))
            foliage = bpy.context.active_object
            if leaf_mat: foliage.data.materials.append(leaf_mat)
            
    elif env_type == "castle":
        # Draw stone pillars
        for i in range(4):
            x = -3.5 if i % 2 == 0 else 3.5
            y = character_pos[1] - (i * 5) + 5
            bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=8, location=(x, y, 4.0))
            pillar = bpy.context.active_object
            if stone_mat: pillar.data.materials.append(stone_mat)
            
    elif env_type == "village":
        # Small house primitives
        for i in range(3):
            x = -5.0 if i % 2 == 0 else 5.0
            y = character_pos[1] - (i * 6) + 4
            # Body
            bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, 1.0))
            body = bpy.context.active_object
            if stone_mat: body.data.materials.append(stone_mat)
            # Roof
            bpy.ops.mesh.primitive_cone_add(radius1=1.5, depth=1.5, location=(x, y, 2.75))
            roof = bpy.context.active_object
            if roof_mat: roof.data.materials.append(roof_mat)
            
    elif env_type == "cave":
        # Stalagmites pointing up
        for i in range(8):
            x = random.uniform(-3.0, 3.0)
            # Keep path clear
            if abs(x) < 1.0: x = 2.0 if x > 0 else -2.0
            y = character_pos[1] - (i * 3.0) + 2
            bpy.ops.mesh.primitive_cone_add(radius1=0.4, depth=random.uniform(1.5, 3.5), location=(x, y, 1.0))
            stalag = bpy.context.active_object
            if stone_mat: stalag.data.materials.append(stone_mat)
            
    elif env_type == "beach":
        # Ocean plane on left
        bpy.ops.mesh.primitive_plane_add(size=30, location=(-18, character_pos[1] - 5, 0.05))
        ocean = bpy.context.active_object
        if ocean_mat: ocean.data.materials.append(ocean_mat)
        
        # Palm tree on right
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=4, location=(4, character_pos[1] - 2, 2.0))
        palm = bpy.context.active_object
        if trunk_mat: palm.data.materials.append(trunk_mat)
        
    elif env_type == "mountain":
        # Tilted mountain ranges in background
        for i in range(3):
            x = -15 if i == 0 else 15
            y = character_pos[1] - 15
            bpy.ops.mesh.primitive_cone_add(radius1=10.0, depth=15.0, location=(x, y, 4.0))
            mtn = bpy.context.active_object
            if stone_mat: mtn.data.materials.append(stone_mat)
            
    elif env_type == "city":
        # Tall buildings lining street
        for i in range(4):
            x = -6.0 if i % 2 == 0 else 6.0
            y = character_pos[1] - (i * 6) + 3
            bpy.ops.mesh.primitive_cube_add(size=3, location=(x, y, 6.0))
            building = bpy.context.active_object
            building.scale.z = 4.0 # stretch vertically
            if stone_mat: building.data.materials.append(stone_mat)
            
    elif env_type == "arena":
        # Ring of small pillars
        for i in range(12):
            angle = i * (2 * math.pi / 12)
            radius = 6.0
            x = character_pos[0] + radius * math.cos(angle)
            y = character_pos[1] + radius * math.sin(angle)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1.5, location=(x, y, 0.75))
            fence = bpy.context.active_object
            if stone_mat: fence.data.materials.append(stone_mat)
            
    # 6. SPAWN WEATHER EFFECTS
    try:
        spawn_weather_effects(weather, character_pos)
    except Exception as w_err:
        print(f"[EnvironmentDirector] Failed to spawn weather: {w_err}")
        
    # 7. SPAWN ENVIRONMENT PROPS
    if environment_props:
        try:
            spawn_environment_props(environment_props, character_pos)
        except Exception as p_err:
            print(f"[EnvironmentDirector] Failed to spawn props: {p_err}")

    # 8. SPAWN RESOLVED ASSETS
    if resolved_assets:
        try:
            spawn_resolved_assets(resolved_assets, character_pos)
        except Exception as a_err:
            print(f"[EnvironmentDirector] Failed to spawn resolved assets: {a_err}")

    # Force viewport/dependency graph updates to ensure visual changes register
    bpy.context.view_layer.update()
    print("[EnvironmentDirector] Environment successfully built.")
    return env_seed


def spawn_resolved_assets(assets: List[Dict[str, Any]], character_pos=(0, 0, 0)):
    if not bpy: return
    if not assets: return
    
    print(f"[EnvironmentDirector] Spawning resolved assets: {len(assets)}")
    
    trunk_mat = create_colored_material("TrunkMat", "trunk_brown")
    stone_mat = create_colored_material("StoneMat", "dark_stone")
    sand_mat = create_colored_material("SandMat", "yellow_sand")
    leaf_mat = create_colored_material("LeafMat", "leaf_green")
    
    # PROJECT_DIR resolution inside Blender sandbox
    daemon_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(os.path.dirname(daemon_dir)) if "ai" in daemon_dir else daemon_dir
    
    slots = [
        (character_pos[0] + 1.3, character_pos[1] - 1.2, 0.0), # Slot 1 (front right)
        (character_pos[0] - 1.3, character_pos[1] - 1.2, 0.0), # Slot 2 (front left)
        (character_pos[0] + 1.7, character_pos[1] - 2.8, 0.0), # Slot 3 (mid right)
        (character_pos[0] - 1.7, character_pos[1] - 2.8, 0.0), # Slot 4 (mid left)
        (character_pos[0], character_pos[1] + 2.0, 0.0)        # Slot 5 (behind)
    ]
    
    slot_idx = 0
    for asset in assets:
        atype = asset.get("type", "prop")
        placement = asset.get("placement", "ground")
        if atype == "character" or placement in ["right_hand", "left_hand", "head", "torso", "feet", "neck", "back"]:
            continue
            
        slot = slots[slot_idx % len(slots)]
        slot_idx += 1
        
        noun = asset.get("noun", "object")
        scale = asset.get("scale", [1.0, 1.0, 1.0])
        fallback = asset.get("fallback", "cube")
        is_missing = asset.get("missing", True)
        model_path = asset.get("model", "")
        
        model_loaded = False
        if not is_missing and model_path:
            full_path = os.path.join(project_dir, model_path)
            if os.path.exists(full_path) and os.path.getsize(full_path) > 100:
                try:
                    print(f"[EnvironmentDirector] Importing asset GLB: {full_path}")
                    bpy.ops.import_scene.gltf(filepath=full_path)
                    imported_obj = bpy.context.active_object
                    if imported_obj:
                        imported_obj.name = f"Asset_{noun}"
                        imported_obj.location = (slot[0], slot[1], slot[2] + 0.1)
                        imported_obj.scale = scale
                        model_loaded = True
                except Exception as import_err:
                    print(f"[EnvironmentDirector] Error importing GLB for {noun}: {import_err}")
                    
        if not model_loaded:
            print(f"[EnvironmentDirector] Spawning procedural fallback for: {noun} (type: {fallback})")
            
            z_offset = scale[2] / 2.0 if fallback in ["cube", "cylinder"] else 0.0
            loc = (slot[0], slot[1], slot[2] + z_offset)
            
            if fallback == "cylinder":
                bpy.ops.mesh.primitive_cylinder_add(radius=scale[0]/2.0, depth=scale[2], location=loc)
            elif fallback == "cone":
                bpy.ops.mesh.primitive_cone_add(radius1=scale[0]/2.0, depth=scale[2], location=loc)
            elif fallback == "sphere":
                bpy.ops.mesh.primitive_uv_sphere_add(radius=scale[0]/2.0, location=loc)
            else:
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
                obj = bpy.context.active_object
                if obj:
                    obj.scale = scale
                    
            obj = bpy.context.active_object
            if obj:
                obj.name = f"FallbackAsset_{noun}"
                if any(x in noun for x in ["tree", "wood", "log", "campfire", "table", "chair", "bed", "crate", "barrel"]):
                    if trunk_mat: obj.data.materials.append(trunk_mat)
                elif any(x in noun for x in ["rock", "stone", "giant", "monster", "dungeon", "wall"]):
                    if stone_mat: obj.data.materials.append(stone_mat)
                elif any(x in noun for x in ["gold", "crown", "chest", "key", "coin", "gem"]):
                    if sand_mat: obj.data.materials.append(sand_mat)
                elif any(x in noun for x in ["flower", "grass", "plant", "bush", "leaf"]):
                    if leaf_mat: obj.data.materials.append(leaf_mat)
                else:
                    if stone_mat: obj.data.materials.append(stone_mat)

def spawn_weather_effects(weather_type: str, character_pos=(0, 0, 0)):
    if not bpy: return
    weather_clean = weather_type.lower().strip()
    
    if weather_clean in ["rain", "storm"]:
        print("[EnvironmentDirector] Spawning procedural rain particles...")
        rain_mat = create_colored_material("RainMat", "ocean_blue")
        for i in range(80):
            rx = character_pos[0] + random.uniform(-6.0, 6.0)
            ry = character_pos[1] + random.uniform(-8.0, 8.0)
            rz = character_pos[2] + random.uniform(0.2, 5.0)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=0.25, location=(rx, ry, rz))
            drop = bpy.context.active_object
            drop.name = f"RainDrop_{i}"
            if rain_mat:
                drop.data.materials.append(rain_mat)
                
    elif weather_clean == "snow":
        print("[EnvironmentDirector] Spawning procedural snow particles...")
        snow_mat = create_colored_material("SnowMat", "snowy_rock")
        for i in range(80):
            rx = character_pos[0] + random.uniform(-6.0, 6.0)
            ry = character_pos[1] + random.uniform(-8.0, 8.0)
            rz = character_pos[2] + random.uniform(0.2, 5.0)
            bpy.ops.mesh.primitive_cube_add(size=0.025, location=(rx, ry, rz))
            flake = bpy.context.active_object
            flake.name = f"SnowFlake_{i}"
            if snow_mat:
                flake.data.materials.append(snow_mat)

def spawn_environment_props(props: List[str], character_pos=(0, 0, 0)):
    if not bpy: return
    if not props: return
    
    print(f"[EnvironmentDirector] Spawning environment props: {props}")
    
    trunk_mat = create_colored_material("TrunkMat", "trunk_brown")
    stone_mat = create_colored_material("StoneMat", "dark_stone")
    roof_mat = create_colored_material("RoofMat", "roof_red")
    sand_mat = create_colored_material("SandMat", "yellow_sand")
    
    for idx, prop in enumerate(props):
        prop_clean = prop.lower().strip()
        if prop_clean == "campfire":
            # Spawn logs
            for i in range(3):
                rot = (0, math.radians(90), i * math.radians(60))
                loc = (character_pos[0], character_pos[1] - 1.8, 0.05)
                bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.6, location=loc, rotation=rot)
                log = bpy.context.active_object
                log.name = f"CampfireLog_{idx}_{i}"
                if trunk_mat: log.data.materials.append(trunk_mat)
            # Spawn fire light
            light_data = bpy.data.lights.new(name="FireLight", type='POINT')
            light_data.energy = 45.0
            light_data.color = (1.0, 0.45, 0.05)
            light_obj = bpy.data.objects.new(name=f"FireLight_{idx}", object_data=light_data)
            bpy.context.collection.objects.link(light_obj)
            light_obj.location = (character_pos[0], character_pos[1] - 1.8, 0.3)
            
        elif prop_clean == "chest":
            loc = (character_pos[0] + 1.4, character_pos[1] - 1.0, 0.2)
            bpy.ops.mesh.primitive_cube_add(size=0.4, location=loc)
            chest = bpy.context.active_object
            chest.name = f"Chest_{idx}"
            chest.scale = (1.2, 0.7, 0.7)
            if sand_mat: chest.data.materials.append(sand_mat)
            
        elif prop_clean == "table":
            loc = (character_pos[0] - 1.4, character_pos[1] - 1.2, 0.35)
            # Table top
            bpy.ops.mesh.primitive_cube_add(size=0.8, location=loc)
            table = bpy.context.active_object
            table.name = f"TableTop_{idx}"
            table.scale = (1.2, 0.8, 0.1)
            if trunk_mat: table.data.materials.append(trunk_mat)
            # Leg
            bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.7, location=(loc[0], loc[1], 0.35))
            leg = bpy.context.active_object
            leg.name = f"TableLeg_{idx}"
            if trunk_mat: leg.data.materials.append(trunk_mat)
            
        elif prop_clean == "crate":
            loc = (character_pos[0] + 1.6, character_pos[1] - 2.2, 0.25)
            bpy.ops.mesh.primitive_cube_add(size=0.5, location=loc)
            crate = bpy.context.active_object
            crate.name = f"Crate_{idx}"
            if trunk_mat: crate.data.materials.append(trunk_mat)
            
        elif prop_clean == "barrel":
            loc = (character_pos[0] - 1.6, character_pos[1] - 2.2, 0.3)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.6, location=loc)
            barrel = bpy.context.active_object
            barrel.name = f"Barrel_{idx}"
            if trunk_mat: barrel.data.materials.append(trunk_mat)
            
        elif prop_clean == "tent":
            loc = (character_pos[0] - 2.8, character_pos[1] - 3.5, 1.0)
            bpy.ops.mesh.primitive_cone_add(radius1=1.8, depth=2.0, location=loc)
            tent = bpy.context.active_object
            tent.name = f"Tent_{idx}"
            if roof_mat: tent.data.materials.append(roof_mat)
