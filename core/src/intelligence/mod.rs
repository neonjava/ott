// core/src/intelligence/mod.rs
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CharacterKnowledge {
    pub character_id: String,
    pub name: String,
    pub primary_role: String,
    pub relationships: HashMap<String, String>, // TargetCharId -> Relation (e.g. "ally", "enemy")
    pub presence_scenes: Vec<String>,
    pub action_timeline: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SceneKnowledge {
    pub scene_id: String,
    pub location: String,
    pub mood: String,
    pub story_phase: String, // "Beginning", "Conflict", "Climax", "Resolution"
    pub primary_characters: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContinuityReport {
    pub inconsistencies_found: usize,
    pub details: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct MovieKnowledgeGraph {
    pub movie_id: String,
    pub character_knowledge: HashMap<String, CharacterKnowledge>,
    pub scene_knowledge: HashMap<String, SceneKnowledge>,
}

impl MovieKnowledgeGraph {
    pub fn new(movie_id: &str) -> Self {
        Self {
            movie_id: movie_id.to_string(),
            character_knowledge: HashMap::new(),
            scene_knowledge: HashMap::new(),
        }
    }

    pub fn register_character_knowledge(&mut self, knowledge: CharacterKnowledge) {
        self.character_knowledge.insert(knowledge.character_id.clone(), knowledge);
    }

    pub fn register_scene_knowledge(&mut self, knowledge: SceneKnowledge) {
        self.scene_knowledge.insert(knowledge.scene_id.clone(), knowledge);
    }

    pub fn query_scenes_by_character(&self, character_id: &str) -> Vec<&SceneKnowledge> {
        self.scene_knowledge
            .values()
            .filter(|s| s.primary_characters.contains(&character_id.to_string()))
            .collect()
    }

    pub fn query_scenes_by_location(&self, location: &str) -> Vec<&SceneKnowledge> {
        let loc_q = location.to_lowercase();
        self.scene_knowledge
            .values()
            .filter(|s| s.location.to_lowercase().contains(&loc_q))
            .collect()
    }

    pub fn verify_continuity(&self) -> ContinuityReport {
        let mut details = Vec::new();
        // Empirical continuity audit across registered scenes
        for char_k in self.character_knowledge.values() {
            if char_k.presence_scenes.is_empty() {
                details.push(format!("Character '{}' has no scene appearances recorded.", char_k.name));
            }
        }

        ContinuityReport {
            inconsistencies_found: details.len(),
            details,
        }
    }

    pub fn diff_knowledge(&self, other: &MovieKnowledgeGraph) -> Vec<String> {
        let mut diffs = Vec::new();
        for (scene_id, s1) in &self.scene_knowledge {
            if let Some(s2) = other.scene_knowledge.get(scene_id) {
                if s1.location != s2.location {
                    diffs.push(format!("Scene '{}' location changed: '{}' -> '{}'", scene_id, s1.location, s2.location));
                }
            } else {
                diffs.push(format!("Scene '{}' removed in version 2", scene_id));
            }
        }
        diffs
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_intelligence_layer_queries_and_diff() {
        let mut graph1 = MovieKnowledgeGraph::new("movie_v1");
        
        let char_elden = CharacterKnowledge {
            character_id: "char_elden".to_string(),
            name: "Elden".to_string(),
            primary_role: "Protagonist".to_string(),
            relationships: HashMap::from([("char_companion".to_string(), "Ally".to_string())]),
            presence_scenes: vec!["scene_01".to_string(), "scene_02".to_string()],
            action_timeline: vec!["Walking".to_string(), "Looking at waterfall".to_string()],
        };

        let scene1 = SceneKnowledge {
            scene_id: "scene_01".to_string(),
            location: "Lush Meadow".to_string(),
            mood: "Serene".to_string(),
            story_phase: "Beginning".to_string(),
            primary_characters: vec!["char_elden".to_string()],
        };

        graph1.register_character_knowledge(char_elden);
        graph1.register_scene_knowledge(scene1);

        let query_res = graph1.query_scenes_by_character("char_elden");
        assert_eq!(query_res.len(), 1);
        assert_eq!(query_res[0].location, "Lush Meadow");

        let mut graph2 = graph1.clone();
        graph2.scene_knowledge.get_mut("scene_01").unwrap().location = "Autumn Forest".to_string();

        let diffs = graph1.diff_knowledge(&graph2);
        assert_eq!(diffs.len(), 1);
        assert!(diffs[0].contains("Lush Meadow"));

        let report = graph1.verify_continuity();
        assert_eq!(report.inconsistencies_found, 0);
    }
}
