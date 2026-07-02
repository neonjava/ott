# ai/renderer/blender.py
"""
Blender-based video renderer for the movie pipeline.
Invokes Blender CLI with render_script.py to produce real rendered MP4 videos.
"""
import os
import json
import uuid
import subprocess
import requests
import time
from typing import Dict, Any

from models.blender.renderer.base import VideoRenderer
from models.blender.storyboard.models import ScenePlan
from models.blender.renderer.action_mapper import ActionMapper
from models.blender.config import Config

DAEMON_URL = "http://127.0.0.1:5005"

def prewarm_blender_daemon():
    """Run a single-frame dummy render to compile OptiX GPU kernels and initialize Blender cache."""
    print("[BlenderRenderer] Pre-warming BlenderDaemon container and GPU OptiX kernels...")
    payload = {
        "character_name": "humanoid",
        "action": "idle",
        "location": "arena",
        "camera_shot": "wide_shot",
        "duration": 0.1,
        "output_path": "/tmp/blender_daemon_prewarm.mp4",
        "mood": "neutral"
    }
    try:
        resp = requests.post(f"{DAEMON_URL}/render", json=payload, timeout=180)
        if resp.status_code == 200 and resp.json().get("status") == "success":
            print("[BlenderRenderer] BlenderDaemon pre-warmed successfully!")
            if os.path.exists("/tmp/blender_daemon_prewarm.mp4"):
                try: os.remove("/tmp/blender_daemon_prewarm.mp4")
                except: pass
            thumb_path = "/tmp/blender_daemon_prewarm_thumb.png"
            if os.path.exists(thumb_path):
                try: os.remove(thumb_path)
                except: pass
        else:
            print(f"[BlenderRenderer] BlenderDaemon pre-warm returned status: {resp.status_code}, data: {resp.text}")
    except Exception as e:
        print(f"[BlenderRenderer] BlenderDaemon pre-warm failed/timed out: {e}")

def ensure_blender_daemon():
    """Ensure the Blender HTTP daemon is running."""
    try:
        resp = requests.get(f"{DAEMON_URL}/ping", timeout=2)
        if resp.status_code == 200:
            return
    except requests.RequestException:
        pass
        
    print("[BlenderRenderer] Starting BlenderDaemon in background...")
    daemon_script = os.path.join(os.path.dirname(__file__), "blender_daemon.py")
    cmd = ["flatpak", "run", "org.blender.Blender", "-b", "--python", daemon_script]
    log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "blender_daemon.log")
    log_fd = open(log_file, "a")
    subprocess.Popen(cmd, stdout=log_fd, stderr=log_fd)
    
    # Wait for daemon to become ready (up to 120s since Blender initialization takes ~45-65s)
    for _ in range(60):
        time.sleep(2)
        try:
            resp = requests.get(f"{DAEMON_URL}/ping", timeout=2)
            if resp.status_code == 200:
                print("[BlenderRenderer] BlenderDaemon is ready!")
                prewarm_blender_daemon()
                return
        except requests.RequestException:
            pass
            
    raise RuntimeError("Timed out waiting for BlenderDaemon to start.")


# Load character registry from JSON file
def _load_character_registry():
    registry_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "character_registry.json"
    )
    if os.path.exists(registry_path):
        with open(registry_path, "r") as f:
            raw = json.load(f)
        # Convert to internal format: {"name": {"glb": ..., "action_map": ...}}
        registry = {}
        for key, val in raw.items():
            registry[key] = {
                "glb": val.get("model", "humanoid.glb"),
                "action_map": val.get("action_map", {}),
            }
        return registry
    return {"humanoid": {"glb": "humanoid.glb", "action_map": {}}}

CHARACTER_REGISTRY = _load_character_registry()


class BlenderVideoRenderer(VideoRenderer):
    def __init__(self, assets_dir: str = None):
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Use the consolidated assets directory (with real models)
        self.assets_dir = assets_dir or os.path.join(project_dir, "assets")
        self.project_dir = project_dir
        
        # Ensure directories exist
        os.makedirs(os.path.join(self.assets_dir, "characters"), exist_ok=True)
        os.makedirs(os.path.join(self.assets_dir, "animations"), exist_ok=True)

    def _resolve_character(self, character_name: str):
        """Resolve character name to GLB path and action map."""
        key = character_name.lower().replace(" ", "_")
        
        if key in CHARACTER_REGISTRY:
            reg = CHARACTER_REGISTRY[key]
        else:
            # Default to humanoid for unknown characters
            reg = CHARACTER_REGISTRY["humanoid"]
        
        glb_path = os.path.join(self.assets_dir, "characters", reg["glb"])
        return glb_path, reg["action_map"]

    def _resolve_action(self, action_description: str, action_map: dict) -> tuple:
        """Map a storyboard action description to an animation action name.
        Returns (blender_action_name, fbx_path_or_None)."""
        desc_lower = action_description.lower()
        
        # Try exact match first
        if desc_lower in action_map:
            return action_map[desc_lower], None
        
        # Try keyword matching
        action_keywords = [
            ("fly", "fly"), ("flying", "fly"), ("launch", "fly"), ("blast", "fly"),
            ("land", "landing"), ("impact", "landing"), ("descend", "landing"),
            ("walk", "walk"), ("approach", "walk"), ("moving", "walk"),
            ("run", "run"), ("charge", "run"), ("sprint", "run"), ("rushing", "run"),
            ("attack", "attack"), ("fight", "attack"), ("swing", "attack"), ("smash", "attack"),
            ("punch", "punch"), ("hit", "punch"), ("strike", "punch"),
            ("jump", "jump"), ("leap", "jump"), ("leaping", "jump"),
            ("stand", "standing"), ("standing", "standing"), ("guard", "standing"),
            ("talk", "talk"), ("speak", "talk"), ("say", "talk"),
            ("raise", "raise_weapon"), ("summon", "raise_weapon"), ("raising", "raise_weapon"),
            ("wave", "wave"), ("victory", "victory"), ("triumph", "victory"),
            ("roar", "roar"), ("shout", "roar"),
            ("die", "death"), ("dead", "death"), ("fall", "death"),
            ("duck", "duck"), ("dodge", "duck"), ("crouch", "duck"),
        ]
        
        for keyword, action_key in action_keywords:
            if keyword in desc_lower:
                if action_key in action_map:
                    return action_map[action_key], None
        
        # Default to idle
        return action_map.get("idle", action_map.get("standing", list(action_map.values())[0])), None

    def render_scene(self, plan: ScenePlan, seed: int, output_path: str, generation_id: str = None, viseme_timeline: list = None) -> str:
        """Render a scene using BlenderDaemon."""
        # ── Resolve Characters & Placements ──
        plan_characters = getattr(plan, "characters", None)
        if not plan_characters:
            plan_characters = [plan.character_name or "humanoid"]
            
        plan_placements = getattr(plan, "character_placements", None)
        if not plan_placements:
            from spatial_placement_engine import SpatialPlacementEngine
            spatial_engine = SpatialPlacementEngine()
            plan_placements = spatial_engine.calculate_positions(plan_characters)

        characters_payload = []
        for char in plan_characters:
            char_path, action_map = self._resolve_character(char)
            # Verify file exists, fallback to humanoid
            if not os.path.exists(char_path) or os.path.getsize(char_path) < 100:
                char_path, action_map = self._resolve_character("humanoid")
                if not os.path.exists(char_path) or os.path.getsize(char_path) < 100:
                    raise FileNotFoundError(
                        f"Character GLB not found or is a placeholder: {char_path}. "
                        f"Please add a real GLB model to assets/characters/"
                    )

            # Assign action
            if char.lower().replace(" ", "_") == (plan.character_name or "humanoid").lower().replace(" ", "_"):
                char_action = plan.action or "idle"
            else:
                char_action = "idle"

            blender_action, fbx_path = self._resolve_action(char_action, action_map)
            
            char_placement = plan_placements.get(char, {
                "position": [0.0, 0.0, 0.0],
                "rotation": [0.0, 0.0, 0.0]
            })

            char_key = char.lower().replace(" ", "_")
            char_visemes = None
            actual_visemes = viseme_timeline if viseme_timeline is not None else getattr(plan, "viseme_timeline", None)
            
            if isinstance(actual_visemes, dict):
                char_visemes = actual_visemes.get(char_key)
            elif char_key == (plan.character_name or "humanoid").lower().replace(" ", "_"):
                char_visemes = actual_visemes

            characters_payload.append({
                "name": char_key,
                "file": os.path.abspath(char_path),
                "action": blender_action,
                "action_file": fbx_path or "",
                "position": char_placement.get("position", [0.0, 0.0, 0.0]),
                "rotation": char_placement.get("rotation", [0.0, 0.0, 0.0]),
                "viseme_timeline": char_visemes,
                "mood": getattr(plan, "mood", "neutral") if char_key == (plan.character_name or "humanoid").lower().replace(" ", "_") else "neutral"
            })

        # ── Scene Continuity & Character Persistence ──
        state_path = os.path.abspath(os.path.join(self.project_dir, "scene_state.json"))
        # Extract start location of the primary character
        start_location = characters_payload[0]["position"]
        if os.path.exists(state_path):
            with open(state_path, "r") as f:
                state_data = json.load(f)
                # Keep compatibility with single location tracking if state existed
                start_location = state_data.get("end_location", characters_payload[0]["position"])

        # Update/Get Visual Continuity state
        from continuity_engine_v2 import ContinuityEngineV2
        continuity = ContinuityEngineV2(os.path.join(self.project_dir, "continuity_state.json"))
        
        # Build plan dict for continuity engine
        description_str = getattr(plan, "visual_description", "") or getattr(plan, "narration", "") or ""
        plan_dict = {
            "location": plan.location or "environment",
            "character_name": plan.character_name or "humanoid",
            "action": plan.action or "idle",
            "description": description_str
        }
        visual_state = continuity.process_scene(plan_dict, plan.scene_number)

        # Extract and resolve visual assets
        from asset_director import AssetDirector
        asset_director = AssetDirector()
        scene_assets = asset_director.get_scene_assets(description_str)

        camera_timeline = getattr(plan, 'camera_timeline', None)
        if camera_timeline is None:
            from cinematic_sequencer import sequence_scene
            camera_timeline = sequence_scene(plan, start_location, characters_payload[0]['action'], fps=12)
            plan.camera_timeline = camera_timeline


        # Build render payload
        payload = {
            "characters": characters_payload,
            "character_name": (plan.character_name or "humanoid").lower().replace(" ", "_"),
            "action": characters_payload[0]["action"],
            "action_file": characters_payload[0]["action_file"],
            "character_file": characters_payload[0]["file"],
            "location": plan.location or "environment",
            "camera_shot": plan.camera_shot or "cinematic wide",
            "duration": plan.duration or 4.0,
            "output_path": os.path.abspath(output_path),
            "start_location": start_location,
            "state_file_path": state_path,
            "mood": getattr(plan, "mood", "neutral"),
            "assets": scene_assets,

            
            # Advanced Visual Continuity state keys
            "held_item": visual_state.get("held_item"),
            "weather": visual_state.get("weather"),
            "outfits": visual_state.get("outfits"),
            "environment_props": visual_state.get("environment_props"),
            
            # Cinematic Sequencer keyframe timeline
            "camera_timeline": camera_timeline,
            
            # Dialogue viseme timeline
            "viseme_timeline": viseme_timeline,
            
            # Configurable Render Profile
            "render_profile": getattr(Config, "RENDER_PROFILE", "testing")
        }

        # Render Cache Agent: Hash payload configuration to determine if identical render already exists
        import hashlib
        import shutil
        cache_payload = payload.copy()
        cache_payload.pop("output_path", None)
        payload_hash = hashlib.md5(json.dumps(cache_payload, sort_keys=True).encode("utf-8")).hexdigest()
        
        cache_dir = os.path.join(self.project_dir, "static", "videos", "cache")
        os.makedirs(cache_dir, exist_ok=True)
        cached_file_path = os.path.join(cache_dir, f"render_{payload_hash}.mp4")
        
        if os.path.exists(cached_file_path):
            print(f"[BlenderRenderer] Render Cache Hit! Reusing cached video: {cached_file_path}")
            shutil.copy2(cached_file_path, output_path)
            cached_thumb = cached_file_path.replace(".mp4", "_thumb.png")
            output_thumb = output_path.replace(".mp4", "_thumb.png")
            if os.path.exists(cached_thumb):
                shutil.copy2(cached_thumb, output_thumb)
            return

        # Write payload JSON for logging
        payload_path = os.path.abspath(os.path.join(
            self.project_dir, "static", "videos",
            f"payload_{generation_id or 'scene'}_{plan.scene_number}.json"
        ))
        os.makedirs(os.path.dirname(payload_path), exist_ok=True)
        with open(payload_path, "w") as f:
            json.dump(payload, f)
        print(f"[BlenderRenderer] Payload created: {payload_path}")

        # Ensure Daemon is running
        ensure_blender_daemon()

        print(f"[BlenderRenderer] Sending job to BlenderDaemon...")
        
        # Auto-retry logic for network issues to daemon
        max_retries = 3
        attempt = 0
        success = False
        last_error = ""
        
        while attempt < max_retries and not success:
            attempt += 1
            try:
                resp = requests.post(f"{DAEMON_URL}/render", json=payload, timeout=300)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == "success":
                        success = True
                    else:
                        raise RuntimeError(f"Daemon reported error: {data}")
                else:
                    raise RuntimeError(f"Daemon returned HTTP {resp.status_code}")
                    
                # Verify output exists
                if not os.path.exists(output_path):
                    last_error = f"Blender completed but output file missing: {output_path}"
                    print(f"[BlenderRenderer] Attempt {attempt} failed: {last_error}")
                    if attempt < max_retries:
                        time.sleep(2)
                        continue
                    else:
                        raise RuntimeError(last_error)
                        
                success = True
            except requests.exceptions.Timeout:
                last_error = "Blender render timed out after 300s"
                print(f"[BlenderRenderer] Attempt {attempt} failed: {last_error}")
                if attempt < max_retries:
                    continue
                else:
                    raise RuntimeError(last_error)
            except Exception as e:
                last_error = str(e)
                print(f"[BlenderRenderer] Attempt {attempt} failed: {last_error}")
                if attempt < max_retries:
                    time.sleep(2)
                    continue
                else:
                    raise RuntimeError(last_error)

        # Cache the completed render output
        if success and os.path.exists(output_path):
            try:
                shutil.copy2(output_path, cached_file_path)
                output_thumb = output_path.replace(".mp4", "_thumb.png")
                cached_thumb = cached_file_path.replace(".mp4", "_thumb.png")
                if os.path.exists(output_thumb):
                    shutil.copy2(output_thumb, cached_thumb)
                print(f"[BlenderRenderer] Render Cache populated: {cached_file_path}")
            except Exception as cache_err:
                print(f"[BlenderRenderer] Failed to populate render cache: {cache_err}")

        # Cleanup payload
        if not getattr(Config, "DEBUG_KEEP_INTERMEDIATE", False) and os.path.exists(payload_path):
            os.remove(payload_path)

        print(f"[BlenderRenderer] Scene {plan.scene_number} rendered: {output_path} ({os.path.getsize(output_path)} bytes)")
        return output_path
