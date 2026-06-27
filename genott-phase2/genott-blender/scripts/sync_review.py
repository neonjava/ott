# scripts/sync_review.py
import os
import shutil

def main():
    workspace_dir = "PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender"
    target_dir = os.path.join(workspace_dir, "temp_review")
    
    # Create temp_review directory if it does not exist
    os.makedirs(target_dir, exist_ok=True)
    
    # Files mapping: (source_path, target_filename)
    files_to_sync = [
        (os.path.join(workspace_dir, "AI_HISTORY.md"), "AI_HISTORY.md"),
        (os.path.join(workspace_dir, "docs", "architecture", "ROADMAP_NEXT.md"), "ROADMAP_NEXT.md"),
        (os.path.join(workspace_dir, "PROJECT_GAP_ANALYSIS.md"), "PROJECT_GAP_ANALYSIS.md"),
        (os.path.join(workspace_dir, "MOVIE_REVIEW.md"), "MOVIE_REVIEW.md"),
        (os.path.join(workspace_dir, "docs", "architecture", "BENCHMARK_RESULTS.md"), "BENCHMARK_RESULTS.md"),
        (os.path.join(workspace_dir, "CHANGELOG.md"), "CHANGELOG.md"),
        (os.path.join(workspace_dir, "docs", "architecture", "ARCHITECTURE_DECISIONS.md"), "ARCHITECTURE_DECISIONS.md"),
        (os.path.join(workspace_dir, "docs", "architecture", "VISUAL_REVIEW.md"), "VISUAL_REVIEW.md"),
        (os.path.join(workspace_dir, "README.md"), "README.md"),
        # Get TASK_BOARD from the active conversation artifacts folder
        ("PROJECT_ROOT/.gemini/antigravity-cli/brain/3496fc80-3ea9-4817-8bc4-b4e0e2ff7b60/TASK_BOARD.md", "TASK_BOARD.md")
    ]
    
    print("[SyncReview] Syncing files to temp_review/ ...")
    for src, dst_name in files_to_sync:
        dst = os.path.join(target_dir, dst_name)
        if os.path.exists(src):
            try:
                shutil.copy2(src, dst)
                print(f"  ✓ Copied: {os.path.basename(src)} -> temp_review/{dst_name}")
            except Exception as e:
                print(f"  ✗ Failed to copy {src}: {e}")
        else:
            print(f"  ⚠ Source file not found: {src}")

if __name__ == "__main__":
    main()
