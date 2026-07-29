pub mod analyzer;
pub mod asset;
pub mod character;
pub mod events;
pub mod execution;
pub mod graph;
pub mod importer;
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
use std::sync::Arc;
use timeline::engine::Timeline;

fn main() {
    println!("[GenOTT V2 Movie Engine] Initializing End-to-End Pipeline Execution...");

    // 1. Create Event Bus & Execution Engine
    let event_bus = Arc::new(EventBus::new());
    let mut execution_engine = ExecutionEngine::new(event_bus.clone());

    // 2. Import Movie File
    let dummy_path = "Cargo.toml";
    println!("  [Step 1] Importing Movie File: {}", dummy_path);
    let (info, _frame_db) = MovieImporter::import_file(dummy_path).unwrap();
    println!("  [Step 2] Extracted {} Frames ({} FPS, {}x{})", info.total_frames, info.fps, info.width, info.height);

    // 3. Build Timeline & Add Clips
    let mut timeline = Timeline::new(info.fps);
    let clip_id = timeline
        .add_clip("video_main", "Establishing Shot", 81, "Elden walking in valley", vec!["char_elden".to_string()])
        .unwrap();
    println!("  [Step 3] Timeline Constructed. Added Clip: {}", clip_id);

    // 4. Plan Character Modification
    println!("  [Step 4] User Modifies Character Parameter (Clothing -> Emerald Armor)");
    let plan = execution_engine.plan_character_edit(&mut timeline, "char_elden", "Emerald Armor");
    println!("  [Step 5] Execution Planner Created Plan {}: {} Jobs Queued", plan.plan_id, plan.total_jobs);

    // 5. Execute Jobs via Worker Scheduling
    while let Some(job_id) = execution_engine.execute_next_job() {
        println!("  [Step 6] Worker Executed Job {}", job_id);
    }

    println!("[GenOTT V2 Movie Engine] End-to-End Pipeline Execution Successful!");
}
