# ai/procedural_layout.py
import random
from typing import Dict, Any, List

class ProceduralLayoutSolver:
    """
    Subsystem: Procedural Layout
    Solves spatial arrangement equations for props and furniture in indoor/outdoor environments.
    Resolves relative descriptors (e.g., "on the table", "beside the chair").
    """
    def __init__(self):
        pass

    def arrange_props(self, central_prop: str, auxiliary_props: List[str], layout_type: str = "cluster") -> List[Dict[str, Any]]:
        """Calculates coordinate transforms for auxiliary props relative to a central focal prop."""
        layouts = []
        
        # Central focal point position
        center_x, center_y, center_z = 0.0, 0.0, 0.0
        layouts.append({
            "noun": central_prop,
            "translation": [center_x, center_y, center_z],
            "rotation": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0]
        })
        
        if layout_type == "cluster":
            # Arrange in a circle around the focal prop
            radius = 1.2
            num_props = len(auxiliary_props)
            import math
            for idx, prop in enumerate(auxiliary_props):
                angle = (2 * math.pi / num_props) * idx if num_props > 0 else 0
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                layouts.append({
                    "noun": prop,
                    "translation": [round(x, 3), round(y, 3), center_z],
                    "rotation": [0.0, 0.0, round(math.degrees(angle), 1)],
                    "scale": [1.0, 1.0, 1.0]
                })
        elif layout_type == "stack":
            # Arrange on top of each other (e.g. book on table)
            current_height = 0.8  # Table surface height baseline
            for prop in auxiliary_props:
                layouts.append({
                    "noun": prop,
                    "translation": [center_x, center_y, round(current_height, 3)],
                    "rotation": [0.0, 0.0, float(random.randint(0, 360))],
                    "scale": [1.0, 1.0, 1.0]
                })
                current_height += 0.15  # Increment stack height
                
        return layouts
