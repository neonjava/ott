// core/src/plugin/mod.rs
pub mod traits;

use std::collections::HashMap;
use std::sync::Arc;
pub use traits::*;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PluginStatus {
    Loaded,
    Unloaded,
    Error(String),
}

pub struct PluginInstance {
    pub name: String,
    pub version: String,
    pub status: PluginStatus,
    pub plugin: Arc<dyn ModelBackendPlugin>,
}

pub struct PluginManager {
    backends: HashMap<String, PluginInstance>,
}

impl Default for PluginManager {
    fn default() -> Self {
        Self::new()
    }
}

impl PluginManager {
    pub fn new() -> Self {
        Self {
            backends: HashMap::new(),
        }
    }

    pub fn load_plugin(&mut self, plugin: Arc<dyn ModelBackendPlugin>, version: &str) {
        let name = plugin.name().to_string();
        let instance = PluginInstance {
            name: name.clone(),
            version: version.to_string(),
            status: PluginStatus::Loaded,
            plugin,
        };
        self.backends.insert(name, instance);
    }

    pub fn unload_plugin(&mut self, name: &str) -> bool {
        if let Some(instance) = self.backends.get_mut(name) {
            instance.status = PluginStatus::Unloaded;
            true
        } else {
            false
        }
    }

    pub fn get_backend(&self, name: &str) -> Option<Arc<dyn ModelBackendPlugin>> {
        self.backends.get(name).and_then(|inst| {
            if inst.status == PluginStatus::Loaded {
                Some(inst.plugin.clone())
            } else {
                None
            }
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::graph::movie_graph::GraphNode;

    struct DummyLTXBackend;
    impl ModelBackendPlugin for DummyLTXBackend {
        fn name(&self) -> &'static str {
            "ltx_video"
        }
        fn render_shot(&self, _shot: &GraphNode) -> Result<String, PluginError> {
            Ok("ltx_output.mp4".to_string())
        }
    }

    #[test]
    fn test_plugin_lifecycle() {
        let mut manager = PluginManager::new();
        manager.load_plugin(Arc::new(DummyLTXBackend), "0.9.1");

        assert!(manager.get_backend("ltx_video").is_some());

        let unloaded = manager.unload_plugin("ltx_video");
        assert!(unloaded);
        assert!(manager.get_backend("ltx_video").is_none());
    }
}
