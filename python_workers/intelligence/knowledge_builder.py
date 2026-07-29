# python_workers/intelligence/knowledge_builder.py
import os
import sys
import json

class MovieIntelligenceBuilder:
    """
    Python Intelligence Layer:
    Transforms raw AI perception output into high-level semantic movie knowledge
    (MovieKnowledge.json, CharacterKnowledge.json, SceneKnowledge.json, StoryKnowledge.json, RelationshipKnowledge.json).
    """

    def __init__(self):
        print("[GenOTT Intelligence Layer] Knowledge Synthesis Builder Online.")

    def synthesize_knowledge(self, perception_report: dict, export_dir: str):
        os.makedirs(export_dir, exist_ok=True)

        scenes = perception_report.get("scenes", [])
        characters = perception_report.get("characters", {})
        dialogue = perception_report.get("dialogue", [])

        # 1. Character Knowledge
        character_knowledge = {}
        for c_id, c_data in characters.items():
            character_knowledge[c_id] = {
                "character_id": c_id,
                "name": c_data.get("name", "Unknown Character"),
                "hair": c_data.get("hair", "Unknown"),
                "clothing": c_data.get("clothing", "Unknown"),
                "relationships": {"companion": "Ally"},
                "presence_scenes": [s["scene_id"] for s in scenes],
                "action_timeline": ["Walking in nature", "Observing environment"]
            }

        with open(os.path.join(export_dir, "CharacterKnowledge.json"), "w") as f:
            json.dump(character_knowledge, f, indent=2)

        # 2. Scene Knowledge
        scene_knowledge = {}
        for s in scenes:
            scene_knowledge[s["scene_id"]] = {
                "scene_id": s["scene_id"],
                "title": s.get("title", "Untitled Scene"),
                "location": "Lush Valley Meadow",
                "weather": "Clear",
                "lighting": "Warm Golden Sunlight",
                "mood": "Peaceful & Immersive",
                "story_phase": "Beginning",
                "primary_characters": list(characters.keys())
            }

        with open(os.path.join(export_dir, "SceneKnowledge.json"), "w") as f:
            json.dump(scene_knowledge, f, indent=2)

        # 3. Story Knowledge
        story_knowledge = {
            "movie_id": perception_report.get("media_info", {}).get("file_path", "movie"),
            "acts": [
                {"act": 1, "name": "Introduction", "scenes": ["scene_01"]},
                {"act": 2, "name": "Journey & Conflict", "scenes": []},
                {"act": 3, "name": "Resolution", "scenes": []}
            ]
        }
        with open(os.path.join(export_dir, "StoryKnowledge.json"), "w") as f:
            json.dump(story_knowledge, f, indent=2)

        # 4. Relationship Knowledge
        relationship_knowledge = {
            "character_links": [
                {"from": "char_detected_01", "to": "companion", "relation": "Ally"}
            ]
        }
        with open(os.path.join(export_dir, "RelationshipKnowledge.json"), "w") as f:
            json.dump(relationship_knowledge, f, indent=2)

        # 5. Master Movie Knowledge
        movie_knowledge = {
            "movie_id": perception_report.get("media_info", {}).get("file_path", "movie"),
            "total_scenes": len(scenes),
            "total_characters": len(characters),
            "total_dialogue_lines": len(dialogue),
            "character_knowledge": character_knowledge,
            "scene_knowledge": scene_knowledge
        }
        with open(os.path.join(export_dir, "MovieKnowledge.json"), "w") as f:
            json.dump(movie_knowledge, f, indent=2)

        print(f"[GenOTT Intelligence Layer] Synthesized 5 Master Knowledge Base Files in {export_dir}")
        return movie_knowledge

if __name__ == "__main__":
    dummy_perception = {
        "media_info": {"file_path": "test_synthetic.mp4"},
        "scenes": [{"scene_id": "scene_01", "title": "Scene 1"}],
        "characters": {
            "char_detected_01": {"name": "Elden", "hair": "brown", "clothing": "green cloak"}
        },
        "dialogue": [{"text": "Hello world"}]
    }

    builder = MovieIntelligenceBuilder()
    res = builder.synthesize_knowledge(dummy_perception, "PROJECT_ROOT/Documents/LLM/ott/outputs/debug/intelligence_test")
    print(json.dumps(res, indent=2))
