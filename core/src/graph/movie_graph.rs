// core/src/graph/movie_graph.rs
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet, VecDeque};
use uuid::Uuid;

pub type NodeId = String;
pub type CharacterId = String;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum NodeType {
    Movie,
    Scene,
    Shot,
    Character,
    Camera,
    Object,
    Environment,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum EdgeType {
    Contains,
    AppearsIn,
    InteractsWith,
    Precedes,
    DependsOn,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GraphEdge {
    pub from: NodeId,
    pub to: NodeId,
    pub edge_type: EdgeType,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GraphNode {
    pub id: NodeId,
    pub name: String,
    pub node_type: NodeType,
    pub properties: HashMap<String, String>,
    pub version: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct MovieGraph {
    pub id: String,
    pub title: String,
    pub version: u64,
    pub nodes: HashMap<NodeId, GraphNode>,
    pub edges: Vec<GraphEdge>,
}

impl MovieGraph {
    pub fn new(title: &str) -> Self {
        let mut graph = Self {
            id: Uuid::new_v4().to_string(),
            title: title.to_string(),
            version: 1,
            nodes: HashMap::new(),
            edges: Vec::new(),
        };

        let root_node = GraphNode {
            id: graph.id.clone(),
            name: title.to_string(),
            node_type: NodeType::Movie,
            properties: HashMap::new(),
            version: 1,
        };
        graph.nodes.insert(graph.id.clone(), root_node);
        graph
    }

    pub fn add_node(&mut self, name: &str, node_type: NodeType) -> NodeId {
        let id = Uuid::new_v4().to_string();
        let node = GraphNode {
            id: id.clone(),
            name: name.to_string(),
            node_type,
            properties: HashMap::new(),
            version: 1,
        };
        self.nodes.insert(id.clone(), node);
        self.version += 1;
        id
    }

    pub fn add_edge(&mut self, from: &str, to: &str, edge_type: EdgeType) -> bool {
        if self.nodes.contains_key(from) && self.nodes.contains_key(to) {
            self.edges.push(GraphEdge {
                from: from.to_string(),
                to: to.to_string(),
                edge_type,
            });
            self.version += 1;
            true
        } else {
            false
        }
    }

    pub fn bfs_traversal(&self, start_id: &str) -> Vec<NodeId> {
        let mut visited = HashSet::new();
        let mut queue = VecDeque::new();
        let mut order = Vec::new();

        if self.nodes.contains_key(start_id) {
            visited.insert(start_id.to_string());
            queue.push_back(start_id.to_string());
        }

        while let Some(current) = queue.pop_front() {
            order.push(current.clone());
            for edge in &self.edges {
                if edge.from == current && !visited.contains(&edge.to) {
                    visited.insert(edge.to.clone());
                    queue.push_back(edge.to.clone());
                }
            }
        }

        order
    }

    pub fn dfs_traversal(&self, start_id: &str) -> Vec<NodeId> {
        let mut visited = HashSet::new();
        let mut order = Vec::new();

        fn dfs(graph: &MovieGraph, current: &str, visited: &mut HashSet<String>, order: &mut Vec<String>) {
            visited.insert(current.to_string());
            order.push(current.to_string());

            for edge in &graph.edges {
                if edge.from == current && !visited.contains(&edge.to) {
                    dfs(graph, &edge.to, visited, order);
                }
            }
        }

        if self.nodes.contains_key(start_id) {
            dfs(self, start_id, &mut visited, &mut order);
        }

        order
    }

    pub fn topological_sort(&self) -> Result<Vec<NodeId>, &'static str> {
        let mut in_degree: HashMap<NodeId, usize> = HashMap::new();
        for node_id in self.nodes.keys() {
            in_degree.insert(node_id.clone(), 0);
        }

        for edge in &self.edges {
            *in_degree.entry(edge.to.clone()).or_insert(0) += 1;
        }

        let mut queue: VecDeque<NodeId> = in_degree
            .iter()
            .filter(|(_, &deg)| deg == 0)
            .map(|(id, _)| id.clone())
            .collect();

        let mut result = Vec::new();

        while let Some(node_id) = queue.pop_front() {
            result.push(node_id.clone());

            for edge in &self.edges {
                if edge.from == node_id {
                    if let Some(deg) = in_degree.get_mut(&edge.to) {
                        *deg -= 1;
                        if *deg == 0 {
                            queue.push_back(edge.to.clone());
                        }
                    }
                }
            }
        }

        if result.len() == self.nodes.len() {
            Ok(result)
        } else {
            Err("Graph contains cycles; topological sort failed")
        }
    }

    pub fn query_nodes_by_type(&self, node_type: NodeType) -> Vec<&GraphNode> {
        self.nodes
            .values()
            .filter(|n| n.node_type == node_type)
            .collect()
    }

    pub fn validate_graph(&self) -> bool {
        for edge in &self.edges {
            if !self.nodes.contains_key(&edge.from) || !self.nodes.contains_key(&edge.to) {
                return false;
            }
        }
        true
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_graph_traversal_and_topological_sort() {
        let mut graph = MovieGraph::new("Action Movie");
        let scene1 = graph.add_node("Scene 1", NodeType::Scene);
        let shot1 = graph.add_node("Shot 1", NodeType::Shot);
        let shot2 = graph.add_node("Shot 2", NodeType::Shot);

        let root_id = graph.id.clone();
        graph.add_edge(&root_id, &scene1, EdgeType::Contains);
        graph.add_edge(&scene1, &shot1, EdgeType::Contains);
        graph.add_edge(&shot1, &shot2, EdgeType::Precedes);

        let bfs = graph.bfs_traversal(&root_id);
        assert_eq!(bfs.len(), 4);

        let topo = graph.topological_sort().unwrap();
        assert_eq!(topo.len(), 4);
        assert!(graph.validate_graph());
    }
}
