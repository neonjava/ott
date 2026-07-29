// core/src/scene/mod.rs
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct EnvironmentSpec {
    pub location: String,
    pub weather: String,
    pub lighting: String,
    pub camera_style: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SceneMetadata {
    pub id: String,
    pub title: String,
    pub environment: EnvironmentSpec,
    pub objects: Vec<String>,
    pub actions: Vec<String>,
    pub dialogue_lines: Vec<String>,
    pub dependencies: Vec<String>,
}

impl SceneMetadata {
    pub fn new(id: &str, title: &str, location: &str, lighting: &str) -> Self {
        Self {
            id: id.to_string(),
            title: title.to_string(),
            environment: EnvironmentSpec {
                location: location.to_string(),
                weather: "Clear".to_string(),
                lighting: lighting.to_string(),
                camera_style: "35mm Cinematic Lens".to_string(),
            },
            objects: Vec::new(),
            actions: Vec::new(),
            dialogue_lines: Vec::new(),
            dependencies: Vec::new(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct SceneRegistry {
    pub scenes: HashMap<String, SceneMetadata>,
}

impl SceneRegistry {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn register_scene(&mut self, scene: SceneMetadata) {
        self.scenes.insert(scene.id.clone(), scene);
    }

    pub fn get_scene(&self, id: &str) -> Option<&SceneMetadata> {
        self.scenes.get(id)
    }

    pub fn diff_scenes(&self, id1: &str, id2: &str) -> Option<Vec<String>> {
        if let (Some(s1), Some(s2)) = (self.scenes.get(id1), self.scenes.get(id2)) {
            let mut diffs = Vec::new();
            if s1.environment.location != s2.environment.location {
                diffs.push(format!("Location: '{}' vs '{}'", s1.environment.location, s2.environment.location));
            }
            if s1.environment.lighting != s2.environment.lighting {
                diffs.push(format!("Lighting: '{}' vs '{}'", s1.environment.lighting, s2.environment.lighting));
            }
            Some(diffs)
        } else {
            None
        }
    }

    pub fn validate_scene(&self, id: &str) -> bool {
        if let Some(scene) = self.scenes.get(id) {
            !scene.title.is_empty() && !scene.environment.location.is_empty()
        } else {
            false
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_scene_registry_diff_and_validation() {
        let mut registry = SceneRegistry::new();
        let s1 = SceneMetadata::new("scene_01", "Morning Meadow", "Valley", "Sunrise");
        let s2 = SceneMetadata::new("scene_02", "Sunset Meadow", "Valley", "Sunset");

        registry.register_scene(s1);
        registry.register_scene(s2);

        let diff = registry.diff_scenes("scene_01", "scene_02").unwrap();
        assert_eq!(diff.len(), 1);
        assert!(diff[0].contains("Lighting"));
        assert!(registry.validate_scene("scene_01"));
    }
}
