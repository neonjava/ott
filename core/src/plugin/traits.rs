// core/src/plugin/traits.rs
use crate::graph::movie_graph::GraphNode;

#[derive(Debug)]
pub enum PluginError {
    ExecutionFailed(String),
}

pub trait ModelBackendPlugin: Send + Sync {
    fn name(&self) -> &'static str;
    fn render_shot(&self, shot: &GraphNode) -> Result<String, PluginError>;
}
