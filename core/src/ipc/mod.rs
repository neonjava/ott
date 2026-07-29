// core/src/ipc/mod.rs
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RenderJob {
    pub job_id: String,
    pub shot_id: String,
    pub prompt: String,
    pub duration_sec: f32,
    pub seed: u32,
    pub backend_name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JobProgress {
    pub job_id: String,
    pub progress_pct: f32,
    pub current_frame: u32,
    pub total_frames: u32,
    pub status: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JobResult {
    pub job_id: String,
    pub success: bool,
    pub output_path: Option<String>,
    pub error_message: Option<String>,
}

pub struct PythonWorkerProtocol;

impl PythonWorkerProtocol {
    pub fn serialize_job(job: &RenderJob) -> Result<String, serde_json::Error> {
        serde_json::to_string(job)
    }

    pub fn deserialize_progress(json_str: &str) -> Result<JobProgress, serde_json::Error> {
        serde_json::from_str(json_str)
    }

    pub fn deserialize_result(json_str: &str) -> Result<JobResult, serde_json::Error> {
        serde_json::from_str(json_str)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ipc_protocol_serialization() {
        let job = RenderJob {
            job_id: "job_101".to_string(),
            shot_id: "shot_01".to_string(),
            prompt: "Hero in valley".to_string(),
            duration_sec: 5.0,
            seed: 42,
            backend_name: "ltx".to_string(),
        };

        let json = PythonWorkerProtocol::serialize_job(&job).unwrap();
        assert!(json.contains("job_101"));
        assert!(json.contains("ltx"));
    }
}
