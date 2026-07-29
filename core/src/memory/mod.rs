// core/src/memory/mod.rs
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct CharacterMemory {
    pub character_states: HashMap<String, HashMap<String, String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct SceneMemory {
    pub scene_states: HashMap<String, HashMap<String, String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ObjectMemory {
    pub object_locations: HashMap<String, String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct MemorySnapshot {
    pub id: String,
    pub timestamp: u64,
    pub character_memory: CharacterMemory,
    pub scene_memory: SceneMemory,
    pub object_memory: ObjectMemory,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct MemoryEngine {
    pub current_snapshot: MemorySnapshot,
    pub snapshots: Vec<MemorySnapshot>,
}

impl MemoryEngine {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn set_character_state(&mut self, char_id: &str, key: &str, value: &str) {
        self.current_snapshot
            .character_memory
            .character_states
            .entry(char_id.to_string())
            .or_default()
            .insert(key.to_string(), value.to_string());
    }

    pub fn get_character_state(&self, char_id: &str, key: &str) -> Option<&String> {
        self.current_snapshot
            .character_memory
            .character_states
            .get(char_id)
            .and_then(|m| m.get(key))
    }

    pub fn take_snapshot(&mut self, timestamp: u64) -> String {
        let snapshot_id = format!("snap_{}", self.snapshots.len() + 1);
        let mut snap = self.current_snapshot.clone();
        snap.id = snapshot_id.clone();
        snap.timestamp = timestamp;
        self.snapshots.push(snap);
        snapshot_id
    }

    pub fn rollback_to_snapshot(&mut self, snapshot_id: &str) -> bool {
        if let Some(snap) = self.snapshots.iter().find(|s| s.id == snapshot_id) {
            self.current_snapshot = snap.clone();
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
    fn test_memory_snapshots_and_rollback() {
        let mut mem = MemoryEngine::new();
        mem.set_character_state("elden", "cloak", "green");
        let snap1 = mem.take_snapshot(100);

        mem.set_character_state("elden", "cloak", "blue");
        assert_eq!(mem.get_character_state("elden", "cloak").unwrap(), "blue");

        let rolled_back = mem.rollback_to_snapshot(&snap1);
        assert!(rolled_back);
        assert_eq!(mem.get_character_state("elden", "cloak").unwrap(), "green");
    }
}
