# scripts/sync_review.py
import os
import shutil

def main():
    workspace_dir = "PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender"
    target_dir = os.path.join(workspace_dir, "temp_review")
    
    # Clean target folder first to remove any unneeded files
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir, exist_ok=True)
    
    # 10 Essential handoff documents for ChatGPT reference
    essential_files = [
        (os.path.join(workspace_dir, "AI_HISTORY.md"), "AI_HISTORY.md"),
        (os.path.join(workspace_dir, "docs", "architecture", "ROADMAP_NEXT.md"), "ROADMAP_NEXT.md"),
        (os.path.join(workspace_dir, "PROJECT_GAP_ANALYSIS.md"), "PROJECT_GAP_ANALYSIS.md"),
        (os.path.join(workspace_dir, "MOVIE_REVIEW.md"), "MOVIE_REVIEW.md"),
        (os.path.join(workspace_dir, "docs", "architecture", "BENCHMARK_RESULTS.md"), "BENCHMARK_RESULTS.md"),
        (os.path.join(workspace_dir, "CHANGELOG.md"), "CHANGELOG.md"),
        (os.path.join(workspace_dir, "docs", "architecture", "ARCHITECTURE_DECISIONS.md"), "ARCHITECTURE_DECISIONS.md"),
        (os.path.join(workspace_dir, "docs", "architecture", "VISUAL_REVIEW.md"), "VISUAL_REVIEW.md"),
        (os.path.join(workspace_dir, "README.md"), "README.md"),
        ("PROJECT_ROOT/.gemini/antigravity-cli/brain/3496fc80-3ea9-4817-8bc4-b4e0e2ff7b60/TASK_BOARD.md", "TASK_BOARD.md")
    ]
    
    print(f"[SyncReview] Mirroring ONLY 10 essential documents to: {target_dir}")
    for src, dst_name in essential_files:
        dst = os.path.join(target_dir, dst_name)
        if os.path.exists(src):
            try:
                shutil.copy2(src, dst)
                print(f"  ✓ Mirrored: {dst_name}")
            except Exception as e:
                print(f"  ✗ Failed to copy {dst_name}: {e}")
        else:
            print(f"  ⚠ Source file not found: {src}")

if __name__ == "__main__":
    main()
