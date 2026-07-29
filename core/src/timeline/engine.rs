// core/src/timeline/engine.rs
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

pub type ClipId = String;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum RenderStatus {
    Pending,
    Rendering,
    Cached,
    Outdated,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum TrackType {
    Video,
    Audio,
    Scene,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Clip {
    pub id: ClipId,
    pub name: String,
    pub start_frame: u32,
    pub duration_frames: u32,
    pub prompt: String,
    pub character_ids: Vec<String>,
    pub status: RenderStatus,
    pub video_path: Option<String>,
    pub hash: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Track {
    pub id: String,
    pub name: String,
    pub track_type: TrackType,
    pub clips: Vec<Clip>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Timeline {
    pub id: String,
    pub fps: u32,
    pub tracks: HashMap<String, Track>,
}

impl Timeline {
    pub fn new(fps: u32) -> Self {
        let mut timeline = Self {
            id: Uuid::new_v4().to_string(),
            fps,
            tracks: HashMap::new(),
        };

        timeline.tracks.insert(
            "video_main".to_string(),
            Track {
                id: "video_main".to_string(),
                name: "Main Video Track".to_string(),
                track_type: TrackType::Video,
                clips: Vec::new(),
            },
        );

        timeline
    }

    pub fn add_clip(
        &mut self,
        track_id: &str,
        name: &str,
        duration_frames: u32,
        prompt: &str,
        char_ids: Vec<String>,
    ) -> Result<ClipId, &'static str> {
        if let Some(track) = self.tracks.get_mut(track_id) {
            let clip_id = Uuid::new_v4().to_string();
            let start_frame = track.clips.iter().map(|c| c.start_frame + c.duration_frames).max().unwrap_or(0);
            let hash = format!("{:x}", md5::compute(format!("{}:{}:{}", prompt, duration_frames, char_ids.join(","))));

            let clip = Clip {
                id: clip_id.clone(),
                name: name.to_string(),
                start_frame,
                duration_frames,
                prompt: prompt.to_string(),
                character_ids: char_ids,
                status: RenderStatus::Pending,
                video_path: None,
                hash,
            };

            track.clips.push(clip);
            Ok(clip_id)
        } else {
            Err("Track not found")
        }
    }

    pub fn ripple_delete(&mut self, track_id: &str, clip_id: &str) -> bool {
        if let Some(track) = self.tracks.get_mut(track_id) {
            if let Some(pos) = track.clips.iter().position(|c| c.id == clip_id) {
                let deleted = track.clips.remove(pos);
                let duration = deleted.duration_frames;
                for clip in track.clips.iter_mut().skip(pos) {
                    clip.start_frame -= duration;
                }
                return true;
            }
        }
        false
    }

    pub fn split_clip(&mut self, track_id: &str, clip_id: &str, split_offset_frames: u32) -> Result<(ClipId, ClipId), &'static str> {
        if let Some(track) = self.tracks.get_mut(track_id) {
            if let Some(pos) = track.clips.iter().position(|c| c.id == clip_id) {
                let clip = &mut track.clips[pos];
                if split_offset_frames >= clip.duration_frames || split_offset_frames == 0 {
                    return Err("Invalid split offset");
                }

                let orig_duration = clip.duration_frames;
                clip.duration_frames = split_offset_frames;

                let new_clip_id = Uuid::new_v4().to_string();
                let second_clip = Clip {
                    id: new_clip_id.clone(),
                    name: format!("{} Part 2", clip.name),
                    start_frame: clip.start_frame + split_offset_frames,
                    duration_frames: orig_duration - split_offset_frames,
                    prompt: clip.prompt.clone(),
                    character_ids: clip.character_ids.clone(),
                    status: RenderStatus::Pending,
                    video_path: None,
                    hash: clip.hash.clone(),
                };

                let first_id = clip.id.clone();
                track.clips.insert(pos + 1, second_clip);
                return Ok((first_id, new_clip_id));
            }
        }
        Err("Clip not found")
    }

    pub fn total_duration_frames(&self) -> u32 {
        self.tracks
            .values()
            .flat_map(|t| t.clips.iter())
            .map(|c| c.start_frame + c.duration_frames)
            .max()
            .unwrap_or(0)
    }

    pub fn mark_character_modified(&mut self, character_id: &str) -> Vec<ClipId> {
        let mut outdated = Vec::new();
        for track in self.tracks.values_mut() {
            for clip in &mut track.clips {
                if clip.character_ids.contains(&character_id.to_string()) {
                    clip.status = RenderStatus::Outdated;
                    outdated.push(clip.id.clone());
                }
            }
        }
        outdated
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ripple_delete_and_split() {
        let mut timeline = Timeline::new(16);
        let clip1 = timeline.add_clip("video_main", "Shot 1", 100, "Prompt 1", vec![]).unwrap();
        let _clip2 = timeline.add_clip("video_main", "Shot 2", 100, "Prompt 2", vec![]).unwrap();

        assert_eq!(timeline.total_duration_frames(), 200);

        let (_part1, _part2) = timeline.split_clip("video_main", &clip1, 40).unwrap();
        assert_eq!(timeline.tracks["video_main"].clips.len(), 3);

        let deleted = timeline.ripple_delete("video_main", &clip1);
        assert!(deleted);
        assert_eq!(timeline.total_duration_frames(), 160);
    }
}
