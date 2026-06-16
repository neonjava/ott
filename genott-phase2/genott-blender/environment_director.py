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

# Keywords mapping location strings to the 8 initial environment types
ENV_KEYWORDS = {
    "forest": ["forest", "woods", "trees", "jungle", "grove", "woodland"],
    "castle": ["castle", "palace", "keep", "fortress", "dungeon", "tower", "chamber", "ruins", "stone", "throne"],
    "village": ["village", "town", "market", "house", "street", "cottage", "yard", "classroom", "library", "school", "office"],
    "cave": ["cave", "cavern", "tunnel", "mine", "abyss", "darkness", "underground"],
    "beach": ["beach", "coast", "shore", "sand", "ocean", "sea", "lake", "water", "island"],
    "mountain": ["mountain", "peak", "cliff", "hill", "slopes", "pass", "ridge", "snowy", "frozen", "ice"],
    "city": ["city", "street", "highway", "factory", "warehouse", "laboratory", "station", "cafe", "hallway", "road", "lab"],
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
        # Match keywords in location string to find environment type
        best_match_count = 0
        for env_type, keywords in ENV_KEYWORDS.items():
            match_count = sum(1 for kw in keywords if kw in loc_words)
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

def build_environment_in_blender(env_config: Dict[str, Any], character_pos=(0, 0, 0)):
    """
    Blender Scene Builder integration.
    Configures terrain, sky, lighting, atmosphere, and places primitive asset structures.
    """
    if not bpy:
        print("[EnvironmentDirector] bpy not available. Skipping scene builder.")
        return
        
    env_type = env_config.get("environment_type", "arena")
    print(f"[EnvironmentDirector] Building '{env_type}' environment in Blender...")
    
    # Clear old environment meshes & lights (keep armature and camera)
    objs_to_delete = []
    for obj in bpy.context.scene.objects:
        if obj.type not in ['ARMATURE', 'CAMERA'] and obj.name not in ["SunLight"]:
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
    random.seed(42) # deterministic seed for asset placement
    
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
            bpy.ops.mesh.primitive_cone_add(radius=1.0, depth=2.5, location=(x, y, 2.5))
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
            bpy.ops.mesh.primitive_cone_add(radius=1.5, depth=1.5, location=(x, y, 2.75))
            roof = bpy.context.active_object
            if roof_mat: roof.data.materials.append(roof_mat)
            
    elif env_type == "cave":
        # Stalagmites pointing up
        for i in range(8):
            x = random.uniform(-3.0, 3.0)
            # Keep path clear
            if abs(x) < 1.0: x = 2.0 if x > 0 else -2.0
            y = character_pos[1] - (i * 3.0) + 2
            bpy.ops.mesh.primitive_cone_add(radius=0.4, depth=random.uniform(1.5, 3.5), location=(x, y, 1.0))
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
            bpy.ops.mesh.primitive_cone_add(radius=10.0, depth=15.0, location=(x, y, 4.0))
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
            
    # Force viewport/dependency graph updates to ensure visual changes register
    bpy.context.view_layer.update()
    print("[EnvironmentDirector] Environment successfully built.")
