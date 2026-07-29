// core/src/asset/mod.rs
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum AssetType {
    Character,
    Environment,
    Audio,
    Video,
    Image,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Asset {
    pub id: String,
    pub name: String,
    pub asset_type: AssetType,
    pub file_path: String,
    pub checksum: String,
    pub ref_count: usize,
    pub metadata: HashMap<String, String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct AssetDatabase {
    pub assets: HashMap<String, Asset>,
    pub checksum_index: HashMap<String, String>,
}

impl AssetDatabase {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn register_asset(&mut self, mut asset: Asset) -> String {
        let content_hash = format!("{:x}", md5::compute(format!("{}:{}", asset.name, asset.file_path)));
        asset.checksum = content_hash.clone();

        if let Some(existing_id) = self.checksum_index.get(&content_hash) {
            if let Some(existing_asset) = self.assets.get_mut(existing_id) {
                existing_asset.ref_count += 1;
                return existing_id.clone();
            }
        }

        let asset_id = asset.id.clone();
        asset.ref_count = 1;
        self.checksum_index.insert(content_hash, asset_id.clone());
        self.assets.insert(asset_id.clone(), asset);
        asset_id
    }

    pub fn get_asset(&self, id: &str) -> Option<&Asset> {
        self.assets.get(id)
    }

    pub fn search_assets(&self, query: &str) -> Vec<&Asset> {
        let q = query.to_lowercase();
        self.assets
            .values()
            .filter(|a| a.name.to_lowercase().contains(&q) || a.file_path.to_lowercase().contains(&q))
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_asset_database_checksum_and_deduplication() {
        let mut db = AssetDatabase::new();
        let asset1 = Asset {
            id: "asset_01".to_string(),
            name: "Elden Reference".to_string(),
            asset_type: AssetType::Image,
            file_path: "assets/elden.png".to_string(),
            checksum: String::new(),
            ref_count: 0,
            metadata: HashMap::new(),
        };

        let id1 = db.register_asset(asset1);

        let asset2 = Asset {
            id: "asset_02".to_string(),
            name: "Elden Reference".to_string(),
            asset_type: AssetType::Image,
            file_path: "assets/elden.png".to_string(),
            checksum: String::new(),
            ref_count: 0,
            metadata: HashMap::new(),
        };

        let id2 = db.register_asset(asset2);

        assert_eq!(id1, id2);
        assert_eq!(db.get_asset(&id1).unwrap().ref_count, 2);
    }
}
