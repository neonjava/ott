// core/src/execution/mod.rs
use crate::events::{EngineEvent, EventBus};
use crate::job::JobScheduler;
use crate::timeline::engine::Timeline;
use serde::{Deserialize, Serialize};
use std::sync::Arc;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionPlan {
    pub plan_id: String,
    pub target_character_id: Option<String>,
    pub affected_clip_ids: Vec<String>,
    pub total_jobs: usize,
}

pub struct ExecutionEngine {
    pub event_bus: Arc<EventBus>,
    pub job_scheduler: JobScheduler,
}

impl ExecutionEngine {
    pub fn new(event_bus: Arc<EventBus>) -> Self {
        Self {
            event_bus,
            job_scheduler: JobScheduler::new(),
        }
    }

    pub fn plan_character_edit(
        &mut self,
        timeline: &mut Timeline,
        character_id: &str,
        new_clothing: &str,
    ) -> ExecutionPlan {
        let affected_clips = timeline.mark_character_modified(character_id);

        let plan_id = format!("plan_{}", affected_clips.len());
        let mut job_ids = Vec::new();

        for clip_id in &affected_clips {
            let j_id = self.job_scheduler.submit_job(
                &format!("Re-render clip {}", clip_id),
                100,
                vec![],
            );
            job_ids.push(j_id);
        }

        self.event_bus.publish(&EngineEvent::CharacterUpdated {
            character_id: character_id.to_string(),
            parameter: "clothing".to_string(),
            new_value: new_clothing.to_string(),
        });

        ExecutionPlan {
            plan_id,
            target_character_id: Some(character_id.to_string()),
            affected_clip_ids: affected_clips,
            total_jobs: job_ids.len(),
        }
    }

    pub fn execute_next_job(&mut self) -> Option<String> {
        if let Some(mut job) = self.job_scheduler.pop_next_runnable_job() {
            let j_id = job.id.clone();
            self.job_scheduler.update_progress(&j_id, 100.0);
            self.event_bus.publish(&EngineEvent::JobCompleted {
                job_id: j_id.clone(),
                output_path: format!("outputs/productions/{}.mp4", j_id),
            });
            Some(j_id)
        } else {
            None
        }
    }
}

pub struct MovieExporter;

impl MovieExporter {
    pub fn export_movie(timeline: &Timeline, output_path: &str) -> Result<String, String> {
        let outdated = timeline.get_outdated_clips();
        if !outdated.is_empty() {
            return Err(format!("Cannot export: {} clips are outdated/pending", outdated.len()));
        }

        // Export completed
        Ok(output_path.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_execution_engine_end_to_end() {
        let event_bus = Arc::new(EventBus::new());
        let mut engine = ExecutionEngine::new(event_bus.clone());
        let mut timeline = Timeline::new(16);

        let c_id = timeline
            .add_clip("video_main", "Shot 1", 81, "Hero", vec!["char_elden".to_string()])
            .unwrap();

        let plan = engine.plan_character_edit(&mut timeline, "char_elden", "Leather Armor");
        assert_eq!(plan.affected_clip_ids.len(), 1);
        assert_eq!(plan.affected_clip_ids[0], c_id);

        let executed_job = engine.execute_next_job().unwrap();
        assert!(!executed_job.is_empty());
    }
}
