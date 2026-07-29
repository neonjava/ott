// core/src/state/mod.rs
use crate::graph::movie_graph::MovieGraph;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectSession {
    pub project_id: String,
    pub current_graph: MovieGraph,
    pub history: Vec<MovieGraph>,
    pub history_index: usize,
}

impl ProjectSession {
    pub fn new(movie_title: &str) -> Self {
        let graph = MovieGraph::new(movie_title);
        Self {
            project_id: graph.id.clone(),
            current_graph: graph.clone(),
            history: vec![graph],
            history_index: 0,
        }
    }

    pub fn commit_state(&mut self, new_graph: MovieGraph) {
        self.history.truncate(self.history_index + 1);
        self.history.push(new_graph.clone());
        self.history_index += 1;
        self.current_graph = new_graph;
    }

    pub fn undo(&mut self) -> bool {
        if self.history_index > 0 {
            self.history_index -= 1;
            self.current_graph = self.history[self.history_index].clone();
            true
        } else {
            false
        }
    }

    pub fn redo(&mut self) -> bool {
        if self.history_index + 1 < self.history.len() {
            self.history_index += 1;
            self.current_graph = self.history[self.history_index].clone();
            true
        } else {
            false
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::graph::movie_graph::NodeType;

    #[test]
    fn test_session_undo_redo() {
        let mut session = ProjectSession::new("Test State");
        let mut next_graph = session.current_graph.clone();
        next_graph.add_node("Scene A", NodeType::Scene);

        session.commit_state(next_graph);
        assert_eq!(session.current_graph.nodes.len(), 2);

        assert!(session.undo());
        assert_eq!(session.current_graph.nodes.len(), 1);

        assert!(session.redo());
        assert_eq!(session.current_graph.nodes.len(), 2);
    }
}
