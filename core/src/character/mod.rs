// core/src/character/mod.rs
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

pub type CharacterId = String;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CharacterAsset {
    pub id: CharacterId,
    pub name: String,
    pub hair: String,
    pub clothing: String,
    pub accessories: String,
    pub face_embedding_path: Option<String>,
    pub voice_id: Option<String>,
    pub version: u64,
    pub parameters: HashMap<String, String>,
}

impl CharacterAsset {
    pub fn new(name: &str, hair: &str, clothing: &str) -> Self {
        Self {
            id: format!("char_{}", name.to_lowercase().replace(' ', "_")),
            name: name.to_string(),
            hair: hair.to_string(),
            clothing: clothing.to_string(),
            accessories: String::new(),
            face_embedding_path: None,
            voice_id: None,
            version: 1,
            parameters: HashMap::new(),
        }
    }

    pub fn update_parameter(&mut self, key: &str, value: &str) {
        self.parameters.insert(key.to_string(), value.to_string());
        self.version += 1;
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct CharacterRegistry {
    pub characters: HashMap<CharacterId, CharacterAsset>,
    pub history: HashMap<CharacterId, Vec<CharacterAsset>>,
}

impl CharacterRegistry {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn register_character(&mut self, character: CharacterAsset) {
        let id = character.id.clone();
        self.history.entry(id.clone()).or_default().push(character.clone());
        self.characters.insert(id, character);
    }

    pub fn update_character(&mut self, character: CharacterAsset) -> bool {
        if self.characters.contains_key(&character.id) {
            self.history.entry(character.id.clone()).or_default().push(character.clone());
            self.characters.insert(character.id.clone(), character);
            true
        } else {
            false
        }
    }

    pub fn get_character(&self, id: &str) -> Option<&CharacterAsset> {
        self.characters.get(id)
    }

    pub fn search_characters(&self, query: &str) -> Vec<&CharacterAsset> {
        let q = query.to_lowercase();
        self.characters
            .values()
            .filter(|c| c.name.to_lowercase().contains(&q) || c.clothing.to_lowercase().contains(&q))
            .collect()
    }

    pub fn merge_characters(&mut self, target_id: &str, source_id: &str) -> bool {
        if let (Some(mut target), Some(source)) = (self.characters.get(target_id).cloned(), self.characters.get(source_id).cloned()) {
            for (k, v) in source.parameters {
                target.parameters.entry(k).or_insert(v);
            }
            target.version += 1;
            self.characters.remove(source_id);
            self.update_character(target);
            true
        } else {
            false
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_character_registry_and_merge() {
        let mut registry = CharacterRegistry::new();
        let mut elden = CharacterAsset::new("Elden", "brown hair", "green cloak");
        elden.update_parameter("role", "traveler");
        registry.register_character(elden);

        let mut elden_alt = CharacterAsset::new("Elden Alt", "brown hair", "leather armor");
        elden_alt.id = "char_elden_alt".to_string();
        elden_alt.update_parameter("weapon", "sword");
        registry.register_character(elden_alt);

        assert_eq!(registry.search_characters("cloak").len(), 1);

        let merged = registry.merge_characters("char_elden", "char_elden_alt");
        assert!(merged);

        let updated_elden = registry.get_character("char_elden").unwrap();
        assert_eq!(updated_elden.parameters.get("weapon").unwrap(), "sword");
        assert!(registry.get_character("char_elden_alt").is_none());
    }
}
