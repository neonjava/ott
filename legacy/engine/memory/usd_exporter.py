# ai/usd/usd_exporter.py
import os
from typing import Dict, Any, List

class USDExporter:
    """
    Subsystem: USD Export Agent
    Formats local scene nodes, cameras, lights, and character coordinates into Pixar USDA ASCII representations.
    """
    def __init__(self):
        pass

    def export_camera(self, name: str, location: List[float], rotation: List[float], lens: float = 35.0) -> str:
        """Generates USDA ASCII representation for a cinematic camera."""
        usda = f"""
    def Camera "{name}"
    {{
        float2 clippingRange = (0.1, 10000)
        float focalLength = {lens}
        float focusDistance = 5.0
        float horizontalAperture = 36.0
        float verticalAperture = 24.0
        double3 xformOp:translate = {tuple(location)}
        double3 xformOp:rotateXYZ = {tuple(rotation)}
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ"]
    }}
"""
        return usda

    def export_light(self, name: str, light_type: str, intensity: float, color: List[float]) -> str:
        """Generates USDA ASCII representation for key/fill/rim light fixtures."""
        usda = f"""
    def "{name}" (
        prepend apiSchemas = ["DistantLightAPI"]
    )
    {{
        float inputs:intensity = {intensity}
        color3f inputs:color = {tuple(color[:3])}
        token inputs:lightType = "{light_type}"
    }}
"""
        return usda

    def export_scene(self, output_path: str, cameras: List[Dict[str, Any]], lights: List[Dict[str, Any]]) -> str:
        """Assembles USDA blocks into a complete, portable scene graph descriptor file."""
        header = """#usda 1.0
(
    defaultPrim = "World"
    metersPerUnit = 1.0
    upAxis = "Z"
)

def Xform "World"
{"""
        body = ""
        for cam in cameras:
            body += self.export_camera(cam["name"], cam["location"], cam["rotation"], cam.get("lens", 35.0))
        for lt in lights:
            body += self.export_light(lt["name"], lt.get("type", "distant"), lt.get("intensity", 1.0), lt.get("color", [1.0, 1.0, 1.0]))
            
        footer = "\n}\n"
        
        full_usda = header + body + footer
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(full_usda)
            
        print(f"[USDExporter] Exported OpenUSD scene description: {output_path}")
        return full_usda
