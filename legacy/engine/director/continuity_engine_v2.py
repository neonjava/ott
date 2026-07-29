#!/usr/bin/env python3
"""
continuity_engine_v2.py — Tracks and maintains visual state consistency across consecutive scenes.
"""
import os
import json
from typing import Dict, Any, List

class ContinuityEngineV2:
    def __init__(self, state_file: str = "continuity_state.json"):
        self.state_file = os.path.abspath(state_file)
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ContinuityEngine] Error loading state: {e}")
        
        # Default empty state
        return {
            "scene_index": 0,
            "location": "",
            "weather": "clear",
            "characters": {},  # name -> {"held_item": None, "outfit": []}
            "environment_props": [],  # list of props remaining in the environment
            "held_items": {},  # name -> item
            "outfit_state": {}  # name -> list of items worn
        }

    def save_state(self):
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"[ContinuityEngine] Error saving state: {e}")

    def clear_state(self):
        if os.path.exists(self.state_file):
            try: os.remove(self.state_file)
            except: pass
        self.state = self._load_state()

    def process_scene(self, scene_plan: Dict[str, Any], scene_idx: int) -> Dict[str, Any]:
        """
        Processes a scene plan, updates the visual state continuity, 
        and returns the consolidated visual parameters for rendering.
        """
        # If starting a new movie (scene index 0 or less than previous), reset continuity state
        if scene_idx <= 1:
            self.clear_state()

        location = scene_plan.get("location", "").lower()
        character = scene_plan.get("character_name", "humanoid").lower()
        action = scene_plan.get("action", "").lower()
        description = (scene_plan.get("description", "") or "").lower()
        
        # 1. Location Continuity
        prev_location = self.state.get("location", "")
        location_changed = (location != prev_location and location != "")
        if location and location != prev_location:
            self.state["location"] = location
            # Clear location-specific props if location changed
            if location_changed:
                self.state["environment_props"] = []

        # 2. Weather Continuity
        # First check if weather is explicitly mentioned in the description
        weather_words = ["rain", "storm", "snow", "fog", "mist", "clear", "sunny", "windy", "dusty"]
        detected_weather = None
        for w in weather_words:
            if w in description:
                detected_weather = w
                break
                
        # Only fallback to location weather if location changed or no weather is set
        if not detected_weather and (location_changed or not self.state.get("weather")):
            for w in weather_words:
                if w in location:
                    detected_weather = w
                    break
                
        if detected_weather:
            self.state["weather"] = detected_weather
        elif location_changed:
            # Default weather transitions per environment location type
            if "forest" in location:
                self.state["weather"] = "clear"
            elif "mountain" in location:
                self.state["weather"] = "snow"
            elif "cave" in location:
                self.state["weather"] = "darkness"
            else:
                self.state["weather"] = "clear"

        # 3. Held Items Continuity
        # Check if character is described as acquiring, dropping, or sheathing items
        if character not in self.state["held_items"]:
            self.state["held_items"][character] = None

        # Look for weapon/prop nouns in the description
        item_nouns = ["sword", "shield", "spear", "bow", "axe", "dagger", "hammer", "staff", "wand", "key", "torch", "lantern"]
        detected_item = None
        for item in item_nouns:
            if item in description:
                detected_item = item
                break

        # Actions that change held state
        if "drop" in action or "drops" in description or "lose" in action:
            self.state["held_items"][character] = None
        elif "sheath" in action or "put away" in description:
            self.state["held_items"][character] = None
        elif "draw" in action or "holds" in description or "holding" in description or "grab" in action or "picks up" in description:
            if detected_item:
                self.state["held_items"][character] = detected_item
        elif detected_item and not self.state["held_items"][character]:
            # Auto-equip if mentioned and character has nothing
            self.state["held_items"][character] = detected_item

        # 4. Outfit State Continuity
        if character not in self.state["outfit_state"]:
            self.state["outfit_state"][character] = []

        outfit_items = ["helmet", "armor", "boots", "crown", "amulet", "cloak", "ring"]
        for outfit in outfit_items:
            if outfit in description:
                if any(x in description for x in ["wear", "put on", "equip", "wearing"]):
                    if outfit not in self.state["outfit_state"][character]:
                        self.state["outfit_state"][character].append(outfit)
                elif any(x in description for x in ["remove", "take off", "takes off", "lose", "loses", "shed"]):
                    if outfit in self.state["outfit_state"][character]:
                        self.state["outfit_state"][character].remove(outfit)

        # 5. Scene Props Continuity
        # Maintain environmental props (e.g. campfire, chests, tables)
        env_props = ["campfire", "chest", "table", "chair", "bed", "crate", "barrel", "tent"]
        for prop in env_props:
            if prop in description:
                if "light" in action or "place" in action or "build" in action or "discover" in action or "find" in action:
                    if prop not in self.state["environment_props"]:
                        self.state["environment_props"].append(prop)
                elif "destroy" in action or "burn down" in description:
                    if prop in self.state["environment_props"]:
                        self.state["environment_props"].remove(prop)

        self.state["scene_index"] = scene_idx
        self.save_state()

        return {
            "location": self.state["location"],
            "weather": self.state["weather"],
            "character_name": character,
            "held_item": self.state["held_items"].get(character),
            "outfits": self.state["outfit_state"].get(character, []),
            "environment_props": self.state["environment_props"]
        }
