# ai/scene_graph.py
from typing import Dict, Any, List, Optional

class SceneGraphNode:
    """
    A single node in the hierarchical scene graph representing characters, props, lights, or cameras.
    """
    def __init__(self, node_id: str, node_type: str, parent: Optional['SceneGraphNode'] = None):
        self.node_id = node_id
        self.node_type = node_type
        self.parent = parent
        self.children: Dict[str, 'SceneGraphNode'] = {}
        self.local_transform = {
            "translation": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0]
        }
        self.attachments: Dict[str, Dict[str, Any]] = {}  # socket_name -> properties

    def add_child(self, child: 'SceneGraphNode'):
        child.parent = self
        self.children[child.node_id] = child

    def remove_child(self, child_id: str):
        if child_id in self.children:
            self.children[child_id].parent = None
            del self.children[child_id]

    def get_world_transform(self) -> Dict[str, List[float]]:
        """Calculates absolute world transform by traversing up the parent hierarchy."""
        if not self.parent:
            return self.local_transform
            
        parent_transform = self.parent.get_world_transform()
        pt = parent_transform["translation"]
        pr = parent_transform["rotation"]
        ps = parent_transform["scale"]
        
        lt = self.local_transform["translation"]
        lr = self.local_transform["rotation"]
        ls = self.local_transform["scale"]
        
        # Simple affine transform representation
        return {
            "translation": [pt[0] + lt[0] * ps[0], pt[1] + lt[1] * ps[1], pt[2] + lt[2] * ps[2]],
            "rotation": [(pr[0] + lr[0]) % 360, (pr[1] + lr[1]) % 360, (pr[2] + lr[2]) % 360],
            "scale": [ps[0] * ls[0], ps[1] * ls[1], ps[2] * ls[2]]
        }

class SceneGraphManager:
    """
    Manages the global scene graph lifecycle and spatial queries.
    """
    def __init__(self):
        self.root = SceneGraphNode("world", "root")

    def find_node(self, node_id: str, current_node: Optional[SceneGraphNode] = None) -> Optional[SceneGraphNode]:
        """Performs a depth-first search to find a node by ID."""
        node = current_node or self.root
        if node.node_id == node_id:
            return node
            
        for child in node.children.values():
            found = self.find_node(node_id, child)
            if found:
                return found
        return None

    def attach_node(self, parent_id: str, child_id: str, socket: str = "root") -> bool:
        """Attaches a target node to a parent node's socket mount."""
        parent_node = self.find_node(parent_id)
        child_node = self.find_node(child_id)
        
        if not parent_node or not child_node:
            return False
            
        # Re-parent
        if child_node.parent:
            child_node.parent.remove_child(child_id)
            
        parent_node.add_child(child_node)
        parent_node.attachments[socket] = {
            "node_id": child_id,
            "attachment_type": "rigid"
        }
        return True

    def serialize_graph(self, node: Optional[SceneGraphNode] = None) -> Dict[str, Any]:
        """Dumps the full node tree into a nested dictionary representation."""
        target = node or self.root
        return {
            "id": target.node_id,
            "type": target.node_type,
            "transform": target.local_transform,
            "world_transform": target.get_world_transform(),
            "attachments": target.attachments,
            "children": [self.serialize_graph(c) for c in target.children.values()]
        }
