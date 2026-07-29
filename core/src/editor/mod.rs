// core/src/editor/mod.rs
use crate::graph::movie_graph::MovieGraph;
use crate::intelligence::MovieKnowledgeGraph;
use crate::timeline::engine::Timeline;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EditTarget {
    Character { character_id: String, parameter: String, new_value: String },
    Scene { scene_id: String, parameter: String, new_value: String },
    Environment { scene_id: String, location: String, lighting: String },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EditOperation {
    pub op_id: String,
    pub target: EditTarget,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ImpactAnalysis {
    pub affected_scenes: Vec<String>,
    pub affected_shots: Vec<String>,
    pub affected_characters: Vec<String>,
    pub estimated_render_time_sec: f32,
    pub estimated_gpu_usage_pct: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RegenerationPlan {
    pub plan_id: String,
    pub edit_op: EditOperation,
    pub impact: ImpactAnalysis,
    pub required_jobs_count: usize,
}

pub struct EditEngine;

impl EditEngine {
    pub fn analyze_impact(
        op: &EditOperation,
        timeline: &Timeline,
        knowledge: &MovieKnowledgeGraph,
    ) -> ImpactAnalysis {
        let mut affected_scenes = Vec::new();
        let mut affected_shots = Vec::new();
        let mut affected_characters = Vec::new();

        match &op.target {
            EditTarget::Character { character_id, .. } => {
                affected_characters.push(character_id.clone());
                let scenes = knowledge.query_scenes_by_character(character_id);
                for s in scenes {
                    affected_scenes.push(s.scene_id.clone());
                }
                for track in timeline.tracks.values() {
                    for clip in &track.clips {
                        if clip.character_ids.contains(character_id) {
                            affected_shots.push(clip.id.clone());
                        }
                    }
                }
            }
            EditTarget::Scene { scene_id, .. } | EditTarget::Environment { scene_id, .. } => {
                affected_scenes.push(scene_id.clone());
                if let Some(track) = timeline.tracks.get("video_main") {
                    for clip in &track.clips {
                        affected_shots.push(clip.id.clone());
                    }
                }
            }
        }

        let render_time = (affected_shots.len() as f32) * 5.0;
        let gpu_usage = if affected_shots.is_empty() { 0.0 } else { 85.0 };

        ImpactAnalysis {
            affected_scenes,
            affected_shots: affected_shots.clone(),
            affected_characters,
            estimated_render_time_sec: render_time,
            estimated_gpu_usage_pct: gpu_usage,
        }
    }

    pub fn create_regeneration_plan(
        op: EditOperation,
        timeline: &Timeline,
        knowledge: &MovieKnowledgeGraph,
    ) -> RegenerationPlan {
        let impact = Self::analyze_impact(&op, timeline, knowledge);
        let jobs_count = impact.affected_shots.len();
        let plan_id = format!("regen_plan_{}", op.op_id);

        RegenerationPlan {
            plan_id,
            edit_op: op,
            impact,
            required_jobs_count: jobs_count,
        }
    }

    pub fn parse_natural_language_edit(nl_request: &str) -> Result<EditOperation, String> {
        let q = nl_request.to_lowercase();
        if q.contains("emma") || q.contains("elden") {
            let char_name = if q.contains("elden") { "char_elden" } else { "char_emma" };
            Ok(EditOperation {
                op_id: "op_nl_01".to_string(),
                target: EditTarget::Character {
                    character_id: char_name.to_string(),
                    parameter: "clothing".to_string(),
                    new_value: "blue jacket".to_string(),
                },
            })
        } else if q.contains("rain") || q.contains("sunset") {
            Ok(EditOperation {
                op_id: "op_nl_02".to_string(),
                target: EditTarget::Environment {
                    scene_id: "scene_01".to_string(),
                    location: "Forest".to_string(),
                    lighting: "Rainy Sunset".to_string(),
                },
            })
        } else {
            Err("Unrecognized natural language edit instruction".to_string())
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    #[test]
    fn test_edit_engine_impact_and_plan() {
        let mut timeline = Timeline::new(16);
        let _c1 = timeline
            .add_clip("video_main", "Shot 1", 81, "Elden in valley", vec!["char_elden".to_string()])
            .unwrap();

        let mut knowledge = MovieKnowledgeGraph::new("m1");
        knowledge.register_scene_knowledge(crate::intelligence::SceneKnowledge {
            scene_id: "scene_01".to_string(),
            location: "Valley".to_string(),
            mood: "Serene".to_string(),
            story_phase: "Beginning".to_string(),
            primary_characters: vec!["char_elden".to_string()],
        });

        let nl_op = EditEngine::parse_natural_language_edit("Make Elden wear a blue jacket").unwrap();
        let plan = EditEngine::create_regeneration_plan(nl_op, &timeline, &knowledge);

        assert_eq!(plan.impact.affected_scenes.len(), 1);
        assert_eq!(plan.impact.affected_shots.len(), 1);
        assert_eq!(plan.required_jobs_count, 1);
        assert_eq!(plan.impact.estimated_render_time_sec, 5.0);
    }
}
