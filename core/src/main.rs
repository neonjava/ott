pub mod analyzer;
pub mod asset;
pub mod character;
pub mod editor;
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

use editor::EditEngine;
use events::EventBus;
use execution::ExecutionEngine;
use importer::MovieImporter;
use intelligence::{CharacterKnowledge, MovieKnowledgeGraph, SceneKnowledge};
use std::collections::HashMap;
use std::sync::Arc;
use timeline::engine::Timeline;

fn main() {
    println!("[GenOTT V2 Edit Engine] Initializing End-to-End Movie Editing & Regeneration System...");

    // 1. Initialize Event Bus & Execution Engine
    let event_bus = Arc::new(EventBus::new());
    let mut execution_engine = ExecutionEngine::new(event_bus.clone());

    // 2. Import Real Media File
    let dummy_path = "Cargo.toml";
    println!("  [Step 1] Media File Imported: {}", dummy_path);
    let (info, _frame_db) = MovieImporter::import_file(dummy_path).unwrap();

    // 3. Build Timeline & Knowledge Graph
    let mut timeline = Timeline::new(info.fps);
    let _clip_id = timeline
        .add_clip("video_main", "Establishing Shot", 81, "Elden walking in valley", vec!["char_elden".to_string()])
        .unwrap();

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

    // 4. Parse Natural Language Edit Instruction
    let nl_input = "Make Elden wear a blue jacket";
    println!("  [Step 2] User Submits Natural Language Edit: '{}'", nl_input);
    let edit_op = EditEngine::parse_natural_language_edit(nl_input).unwrap();

    // 5. Generate Regeneration Plan & Impact Analysis
    let regen_plan = EditEngine::create_regeneration_plan(edit_op.clone(), &timeline, &knowledge_graph);
    println!(
        "  [Step 3] Edit Engine Plan Created: {} Affected Shot(s), Estimated Render Time: {}s (GPU: {}%)",
        regen_plan.impact.affected_shots.len(),
        regen_plan.impact.estimated_render_time_sec,
        regen_plan.impact.estimated_gpu_usage_pct
    );

    // 6. Execute Plan via Worker Jobs
    let plan = execution_engine.plan_character_edit(&mut timeline, "char_elden", "blue jacket");
    println!("  [Step 4] Execution Engine Dispatched Plan {}: {} Job(s) Queued", plan.plan_id, plan.total_jobs);

    while let Some(job_id) = execution_engine.execute_next_job() {
        println!("  [Step 5] Worker Completed Job {}", job_id);
    }

    println!("[GenOTT V2 Edit Engine] End-to-End Editing & Partial Regeneration Successful!");
}
