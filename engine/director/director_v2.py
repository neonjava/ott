#!/usr/bin/env python3
"""
director_v2.py
Upgraded Director AI V2 Engine.
Makes advanced cinematic choices (shots, camera movements, pacing, transitions,
and durations) by considering emotion, interaction type, environment, and scene importance.
"""
from typing import Dict, Any, List

class DirectorV2:
    def __init__(self):
        pass

    def calculate_scene_importance(self, scene: Dict[str, Any], interaction_type: str) -> float:
        """
        Calculates a numerical importance score (0.0 to 1.0) for a scene.
        Scenes with combat, discoveries, or critical emotional shifts are more important.
        """
        score = 0.2 # Base importance
        
        action = scene.get("action", "").lower()
        mood = scene.get("mood", "").lower()

        # Check action importance
        if action in ["attack", "discover", "enter"]:
            score += 0.4
        elif action in ["run", "talk", "help"]:
            score += 0.2

        # Check interaction importance
        if interaction_type in ["fighting", "helping"]:
            score += 0.3
        elif interaction_type in ["speaking", "following"]:
            score += 0.15

        # Check emotional intensity
        if mood in ["angry", "fear", "surprise", "determination"]:
            score += 0.2
        elif mood in ["sad", "hope", "happy"]:
            score += 0.1

        return min(1.0, score)

    def direct_scene(
        self,
        scene: Dict[str, Any],
        interaction_type: str,
        env_config: Dict[str, str],
        prev_scene: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Directs a single scene based on multi-dimensional context.
        """
        directed = scene.copy()
        
        action = scene.get("action", "idle").lower()
        mood = scene.get("mood", "neutral").lower()
        
        env_type = env_config.get("environment_type", "forest")
        atmos = env_config.get("atmosphere", "peaceful")
        weather = env_config.get("weather", "clear")
        lighting = env_config.get("lighting", "sunlight")

        # 1. Calculate Scene Importance
        importance = self.calculate_scene_importance(scene, interaction_type)
        directed["importance_score"] = round(importance, 2)

        # 2. Determine Camera Shot
        camera_shot = "wide_shot"
        if prev_scene is None:
            # First scene: use establishing shot for grand environments
            if env_type in ["castle", "forest", "mountain", "battlefield"]:
                camera_shot = "establishing_shot"
            else:
                camera_shot = "wide_shot"
        else:
            # Context-based mapping
            if interaction_type == "fighting":
                camera_shot = "low_angle" if importance > 0.6 else "medium_shot"
            elif interaction_type == "speaking":
                camera_shot = "close_up" if mood in ("sad", "fear", "angry") else "over_shoulder"
            elif interaction_type == "looking at":
                camera_shot = "close_up"
            elif action == "duck":
                camera_shot = "low_angle"
            elif action == "run":
                camera_shot = "tracking_shot"
            else:
                # Environment or mood defaults
                if env_type == "dungeon" or env_type == "cave":
                    camera_shot = "close_up" if mood == "fear" else "medium_shot"
                elif mood == "hope" or mood == "happy":
                    camera_shot = "wide_shot"
                else:
                    camera_shot = "wide_shot"

        # 3. Determine Camera Movement
        camera_movement = "static"
        if interaction_type == "fighting":
            camera_movement = "orbit"
        elif interaction_type == "following" or action == "run":
            camera_movement = "tracking"
        elif interaction_type == "greeting" or action == "wave":
            camera_movement = "pan"
        elif action == "discover":
            camera_movement = "tilt"
        elif mood == "hope" or env_type == "mountain":
            camera_movement = "zoom"  # slow reveal zoom

        # Adjust for environment constraints
        if weather == "stormy":
            # Stormy weather has high shake / dynamic movements
            directed["shake_amplitude_modifier"] = 1.5
        elif weather == "foggy":
            camera_movement = "static"  # keep it slow and atmospheric

        # 4. Determine Pacing & Durations
        # Pacing: fast, standard, slow
        pacing = "standard"
        duration = 4.0

        if interaction_type == "fighting" or mood == "fear" or action == "run":
            pacing = "fast"
            duration = 3.0
        elif mood in ("sad", "hope") or env_type == "dungeon":
            pacing = "slow"
            duration = 5.5
        
        # Adjust duration based on scene importance
        if importance > 0.7:
            duration += 1.5 # let important scenes breathe
        elif importance < 0.3:
            duration -= 0.5 # keep unimportant scenes moving quickly

        # 5. Determine Transition from previous scene
        transition = "cut"
        if prev_scene:
            prev_loc = prev_scene.get("location", "").lower()
            current_loc = scene.get("location", "").lower()
            
            if prev_loc != current_loc:
                transition = "fade"  # location change fade
            elif mood != prev_scene.get("mood", "neutral") and mood in ("mysterious", "epic", "tense", "fear"):
                transition = "fade"  # emotional atmosphere shift
            elif interaction_type == "fighting" and prev_scene.get("action") != "attack":
                transition = "white"  # flash cut into combat

        directed["camera_shot"] = camera_shot
        directed["camera_movement"] = camera_movement
        directed["pacing"] = pacing
        directed["duration"] = round(duration, 1)
        directed["transition"] = transition

        return directed

    def direct_storyboard(
        self,
        storyboard: Dict[str, Any],
        interactions: List[Dict[str, Any]],
        env_configs: Dict[str, Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Directs a full storyboard with transition mapping, pacing, and camera details.
        """
        scenes = storyboard.get("scenes", [])
        directed_scenes = []
        prev_scene = None

        for idx, scene in enumerate(scenes):
            # Find matching interaction for this scene index
            interaction_type = "none"
            # Event indices or scene numbers correspond to the event idx
            # Match by scene_number or idx
            scene_num = scene.get("scene_number", idx + 1)
            event_id = f"event_{scene_num}"
            
            for inter in interactions:
                if inter.get("event_id") == event_id:
                    interaction_type = inter.get("type", "none")
                    break

            # Find environment configuration
            loc = scene.get("location", "environment")
            env_config = env_configs.get(loc, {
                "environment_type": "forest",
                "atmosphere": "peaceful",
                "weather": "clear",
                "lighting": "sunlight"
            })

            directed = self.direct_scene(scene, interaction_type, env_config, prev_scene)
            directed_scenes.append(directed)
            prev_scene = directed

        # Reconstruct transitions list (transition from scene i to i+1)
        transitions = [s["transition"] for s in directed_scenes[1:]] if len(directed_scenes) > 1 else []

        return {
            "scenes": directed_scenes,
            "transitions": transitions
        }

if __name__ == "__main__":
    import json
    director = DirectorV2()
    
    # Test input
    sample_storyboard = {
        "scenes": [
            {
                "scene_number": 1,
                "character_name": "knight",
                "location": "forest",
                "action": "walk",
                "mood": "sad",
                "speed": "slow"
            },
            {
                "scene_number": 2,
                "character_name": "knight",
                "location": "forest",
                "action": "attack",
                "mood": "angry",
                "speed": "normal"
            }
        ]
    }
    
    sample_interactions = [
        {"event_id": "event_2", "type": "fighting", "source": "knight", "target": "dragon"}
    ]
    
    sample_envs = {
        "forest": {
            "environment_type": "forest",
            "atmosphere": "gloomy",
            "weather": "rainy",
            "lighting": "overcast"
        }
    }

    result = director.direct_storyboard(sample_storyboard, sample_interactions, sample_envs)
    print(json.dumps(result, indent=2))
