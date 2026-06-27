#!/usr/bin/env python3
"""
asset_director.py — Extract story nouns, look up assets, verify existence, and assign fallback primitives.
"""
import os
import json
import re
from typing import Dict, Any, List

def get_registry_path() -> str:
    proj_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(proj_dir, "configs", "asset_registry.json")

class AssetDirector:
    def __init__(self):
        self.registry_path = get_registry_path()
        self.registry = self._load_registry()
        self.project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def _load_registry(self) -> Dict[str, Any]:
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[AssetDirector] Failed to load registry: {e}")
        return {}

    def is_plural_match(self, key: str, word: str) -> bool:
        kw = key.lower()
        w = word.lower()
        if kw == w:
            return True
        if w == kw + "s" or w == kw + "es":
            return True
        if kw == w + "s" or kw == w + "es":
            return True
        if kw.endswith("y") and w == kw[:-1] + "ies":
            return True
        if w.endswith("y") and kw == w[:-1] + "ies":
            return True
        return False

    def extract_nouns(self, text: str) -> List[str]:
        """Extract nouns from text that match registered assets."""
        if not text:
            return []
        
        # Clean text and split to words
        words = re.findall(r'\b[a-zA-Z\s]+\b', text)
        extracted = []
        
        # We also want to support compound nouns like "castle guard"
        # First check multi-word registered keys
        text_lower = text.lower()
        for key in self.registry.keys():
            if " " in key and key in text_lower:
                extracted.append(key)
                # Remove occurrences of compound words to avoid double extraction
                text_lower = text_lower.replace(key, "")
                
        # Split remaining text to single words
        single_words = re.findall(r'\b[a-zA-Z]+\b', text_lower)
        for w in single_words:
            for key in self.registry.keys():
                if " " not in key and self.is_plural_match(key, w):
                    if key not in extracted:
                        extracted.append(key)
                        break
                        
        return extracted

    def resolve_asset(self, noun: str) -> Dict[str, Any]:
        """Lookup asset in registry, detect if missing, and assign fallback."""
        key = noun.lower()
        
        # Exact/plural lookup
        matched_key = None
        for reg_key in self.registry.keys():
            if self.is_plural_match(reg_key, key):
                matched_key = reg_key
                break
                
        if not matched_key:
            # Not in registry: generic fallback
            return {
                "noun": noun,
                "type": "prop",
                "model": "",
                "fallback": "cube",
                "scale": [1.0, 1.0, 1.0],
                "placement": "ground",
                "is_fallback": True,
                "missing": True
            }
            
        entry = self.registry[matched_key]
        model_path = entry.get("model", "")
        full_model_path = os.path.join(self.project_dir, model_path)
        
        # Check if the asset model file exists on disk
        is_missing = not os.path.exists(full_model_path)
        
        return {
            "noun": matched_key,
            "type": entry.get("type", "prop"),
            "model": model_path if not is_missing else "",
            "fallback": entry.get("fallback", "cube"),
            "scale": entry.get("scale", [1.0, 1.0, 1.0]),
            "placement": entry.get("placement", "ground"),
            "is_fallback": is_missing,
            "missing": is_missing
        }

    def get_scene_assets(self, text: str) -> List[Dict[str, Any]]:
        """Extract all nouns from text and resolve their asset definitions."""
        nouns = self.extract_nouns(text)
        return [self.resolve_asset(n) for n in nouns]
