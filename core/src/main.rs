pub mod analyzer;
pub mod asset;
pub mod character;
pub mod events;
pub mod execution;
pub mod graph;
pub mod importer;
pub mod intelligence;
pub mod ipc;
pub mod job;
pub mod memory;
pub mod plugin;
pub mod scene;
pub mod state;
pub mod timeline;

use events::EventBus;
use execution::ExecutionEngine;
use importer::MovieImporter;
use intelligence::{CharacterKnowledge, MovieKnowledgeGraph, SceneKnowledge};
use std::collections::HashMap;
use std::sync::Arc;
use timeline::engine::Timeline;

fn main() {
    println!("[GenOTT V2 Intelligence Engine] Initializing End-to-End Movie Intelligence...");

    // 1. Initialize Event Bus & Execution Engine
    let event_bus = Arc::new(EventBus::new());
    let mut execution_engine = ExecutionEngine::new(event_bus.clone());

    // 2. Import Real Media File
    let dummy_path = "Cargo.toml";
    println!("  [Step 1] Media File Imported: {}", dummy_path);
    let (info, _frame_db) = MovieImporter::import_file(dummy_path).unwrap();

    // 3. Build Timeline
    let mut timeline = Timeline::new(info.fps);
    let clip_id = timeline
        .add_clip("video_main", "Establishing Shot", 81, "Elden walking in valley", vec!["char_elden".to_string()])
        .unwrap();

    // 4. Construct Movie Knowledge Graph
    let mut knowledge_graph = MovieKnowledgeGraph::new("movie_elden_journey");
    let elden_k = CharacterKnowledge {
        character_id: "char_elden".to_string(),
        name: "Elden".to_string(),
        primary_role: "Traveler".to_string(),
        relationships: HashMap::from([("companion".to_string(), "Ally".to_string())]),
        presence_scenes: vec!["scene_01".to_string()],
        action_timeline: vec!["Walking in green valley".to_string()],
    };

    let scene1_k = SceneKnowledge {
        scene_id: "scene_01".to_string(),
        location: "Lush Valley Meadow".to_string(),
        mood: "Peaceful".to_string(),
        story_phase: "Beginning".to_string(),
        primary_characters: vec!["char_elden".to_string()],
    };

    knowledge_graph.register_character_knowledge(elden_k);
    knowledge_graph.register_scene_knowledge(scene1_k);
    println!("  [Step 2] Synthesized Movie Knowledge Graph (1 Character, 1 Scene)");

    // 5. Query Intelligence Layer
    let queried = knowledge_graph.query_scenes_by_character("char_elden");
    println!("  [Step 3] Query Scenes for Elden: Found {} scene ('{}')", queried.len(), queried[0].location);

    // 6. Verify Continuity
    let continuity = knowledge_graph.verify_continuity();
    println!("  [Step 4] Continuity Audit Complete: {} Inconsistencies Found", continuity.inconsistencies_found);

    // 7. Plan Edit & Execute
    let plan = execution_engine.plan_character_edit(&mut timeline, "char_elden", "Emerald Armor");
    println!("  [Step 5] Execution Planner Dispatched Plan {}: {} Job Queued", plan.plan_id, plan.total_jobs);

    while let Some(job_id) = execution_engine.execute_next_job() {
        println!("  [Step 6] Worker Completed Job {}", job_id);
    }

    println!("[GenOTT V2 Intelligence Engine] Movie Knowledge Synthesis Successful!");
}
