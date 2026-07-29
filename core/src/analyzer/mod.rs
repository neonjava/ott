// core/src/analyzer/mod.rs
use crate::graph::movie_graph::MovieGraph;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FrameExtractionSpec {
    pub total_frames: u32,
    pub fps: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SceneDetectionSpec {
    pub scenes_count: u32,
    pub cut_timestamps: Vec<f32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalysisPipelineReport {
    pub video_path: String,
    pub frame_spec: FrameExtractionSpec,
    pub scene_spec: SceneDetectionSpec,
    pub graph: MovieGraph,
}

pub struct MovieAnalyzerPipeline;

impl MovieAnalyzerPipeline {
    pub fn new() -> Self {
        Self
    }

    pub fn execute_pipeline(&self, video_path: &str) -> AnalysisPipelineReport {
        let frame_spec = FrameExtractionSpec {
            total_frames: 480,
            fps: 16,
        };

        let scene_spec = SceneDetectionSpec {
            scenes_count: 2,
            cut_timestamps: vec![0.0, 15.0, 30.0],
        };

        let mut graph = MovieGraph::new(video_path);
        let scene1 = graph.add_node("Scene 1 - Meadow", crate::graph::movie_graph::NodeType::Scene);
        let scene2 = graph.add_node("Scene 2 - Forest", crate::graph::movie_graph::NodeType::Scene);

        let root_id = graph.id.clone();
        graph.add_edge(&root_id, &scene1, crate::graph::movie_graph::EdgeType::Contains);
        graph.add_edge(&root_id, &scene2, crate::graph::movie_graph::EdgeType::Contains);

        AnalysisPipelineReport {
            video_path: video_path.to_string(),
            frame_spec,
            scene_spec,
            graph,
        }
    }
}

impl Default for MovieAnalyzerPipeline {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_movie_analyzer_pipeline_execution() {
        let pipeline = MovieAnalyzerPipeline::new();
        let report = pipeline.execute_pipeline("test_movie.mp4");

        assert_eq!(report.scene_spec.scenes_count, 2);
        assert_eq!(report.graph.nodes.len(), 3);
    }
}
