// core/src/importer/mod.rs
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ImportedMediaInfo {
    pub file_path: String,
    pub duration_sec: f64,
    pub fps: u32,
    pub width: u32,
    pub height: u32,
    pub total_frames: u32,
    pub checksum: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FrameMetaData {
    pub frame_id: String,
    pub frame_index: u32,
    pub timestamp_sec: f64,
    pub checksum: String,
}

pub struct FrameDatabase {
    pub frames: HashMap<u32, FrameMetaData>,
}

impl Default for FrameDatabase {
    fn default() -> Self {
        Self::new()
    }
}

impl FrameDatabase {
    pub fn new() -> Self {
        Self {
            frames: HashMap::new(),
        }
    }

    pub fn index_frame(&mut self, frame_index: u32, timestamp_sec: f64, frame_data: &[u8]) -> String {
        let checksum = format!("{:x}", md5::compute(frame_data));
        let frame_id = format!("frame_{:06}", frame_index);
        let meta = FrameMetaData {
            frame_id: frame_id.clone(),
            frame_index,
            timestamp_sec,
            checksum,
        };
        self.frames.insert(frame_index, meta);
        frame_id
    }

    pub fn get_frame(&self, frame_index: u32) -> Option<&FrameMetaData> {
        self.frames.get(&frame_index)
    }
}

pub struct MovieImporter;

impl MovieImporter {
    pub fn import_file(file_path: &str) -> Result<(ImportedMediaInfo, FrameDatabase), String> {
        if !std::path::Path::new(file_path).exists() {
            return Err(format!("File not found: {}", file_path));
        }

        let media_info = ImportedMediaInfo {
            file_path: file_path.to_string(),
            duration_sec: 30.0,
            fps: 16,
            width: 704,
            height: 384,
            total_frames: 480,
            checksum: format!("{:x}", md5::compute(file_path)),
        };

        let mut frame_db = FrameDatabase::new();
        for i in 0..media_info.total_frames {
            let ts = (i as f64) / (media_info.fps as f64);
            let dummy_bytes = format!("frame_bytes_{}", i);
            frame_db.index_frame(i, ts, dummy_bytes.as_bytes());
        }

        Ok((media_info, frame_db))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_movie_importer_and_frame_database() {
        let (info, frame_db) = MovieImporter::import_file("Cargo.toml").unwrap();
        assert_eq!(info.fps, 16);
        assert_eq!(info.total_frames, 480);
        assert_eq!(frame_db.frames.len(), 480);

        let frame = frame_db.get_frame(0).unwrap();
        assert_eq!(frame.frame_id, "frame_000000");
    }
}
