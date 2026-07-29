# ai/usd/usd_importer.py
import re
import os
from typing import Dict, Any, List

class USDImporter:
    """
    Subsystem: USD Import Agent
    Parses USDA ASCII files and reconstructs scene graph components (cameras, lights, coordinates).
    """
    def __init__(self):
        pass

    def import_scene(self, usda_path: str) -> Dict[str, Any]:
        """Parses USDA scene definitions to reconstruct scene data dictionaries."""
        if not os.path.exists(usda_path):
            raise FileNotFoundError(f"USDA file not found: {usda_path}")
            
        with open(usda_path, "r") as f:
            content = f.read()
            
        cameras = []
        lights = []
        
        # Parse Cameras
        camera_matches = re.finditer(r'def Camera "([^"]+)"\s*\{([^}]+)\}', content)
        for match in camera_matches:
            cam_name = match.group(1)
            block = match.group(2)
            
            # Extract lens, translate, rotate
            lens_match = re.search(r'float focalLength\s*=\s*([\d\.]+)', block)
            trans_match = re.search(r'double3 xformOp:translate\s*=\s*\(([^)]+)\)', block)
            rot_match = re.search(r'double3 xformOp:rotateXYZ\s*=\s*\(([^)]+)\)', block)
            
            lens = float(lens_match.group(1)) if lens_match else 35.0
            location = [float(x.strip()) for x in trans_match.group(1).split(",")] if trans_match else [0.0, 0.0, 0.0]
            rotation = [float(x.strip()) for x in rot_match.group(1).split(",")] if rot_match else [0.0, 0.0, 0.0]
            
            cameras.append({
                "name": cam_name,
                "location": location,
                "rotation": rotation,
                "lens": lens
            })
            
        # Parse Lights
        light_matches = re.finditer(r'def "([^"]+)" \(\s*prepend apiSchemas = \["DistantLightAPI"\]\s*\)\s*\{([^}]+)\}', content)
        for match in light_matches:
            light_name = match.group(1)
            block = match.group(2)
            
            intensity_match = re.search(r'float inputs:intensity\s*=\s*([\d\.]+)', block)
            color_match = re.search(r'color3f inputs:color\s*=\s*\(([^)]+)\)', block)
            
            intensity = float(intensity_match.group(1)) if intensity_match else 1.0
            color = [float(x.strip()) for x in color_match.group(1).split(",")] if color_match else [1.0, 1.0, 1.0]
            
            lights.append({
                "name": light_name,
                "intensity": intensity,
                "color": color,
                "type": "distant"
            })
            
        return {
            "cameras": cameras,
            "lights": lights
        }
