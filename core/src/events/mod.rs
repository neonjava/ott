// core/src/events/mod.rs
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EngineEvent {
    MovieImported { project_id: String, video_path: String },
    FrameExtracted { frame_id: String, timestamp: f64 },
    SceneDetected { scene_id: String, start_frame: u32, end_frame: u32 },
    CharacterUpdated { character_id: String, parameter: String, new_value: String },
    SceneModified { scene_id: String },
    TimelineChanged { timeline_id: String },
    JobCompleted { job_id: String, output_path: String },
    WorkerFailed { worker_id: String, reason: String },
    MovieExported { export_path: String },
}

pub type EventCallback = Box<dyn Fn(&EngineEvent) + Send + Sync>;

pub struct EventBus {
    listeners: Vec<EventCallback>,
}

impl Default for EventBus {
    fn default() -> Self {
        Self::new()
    }
}

impl EventBus {
    pub fn new() -> Self {
        Self { listeners: Vec::new() }
    }

    pub fn subscribe<F>(&mut self, callback: F)
    where
        F: Fn(&EngineEvent) + Send + Sync + 'static,
    {
        self.listeners.push(Box::new(callback));
    }

    pub fn publish(&self, event: &EngineEvent) {
        for listener in &self.listeners {
            listener(event);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicBool, Ordering};
    use std::sync::Arc;

    #[test]
    fn test_event_bus_publish_subscribe() {
        let mut bus = EventBus::new();
        let received = Arc::new(AtomicBool::new(false));
        let r_clone = received.clone();

        bus.subscribe(move |event| {
            if let EngineEvent::MovieImported { .. } = event {
                r_clone.store(true, Ordering::SeqCst);
            }
        });

        bus.publish(&EngineEvent::MovieImported {
            project_id: "p1".to_string(),
            video_path: "video.mp4".to_string(),
        });

        assert!(received.load(Ordering::SeqCst));
    }
}
