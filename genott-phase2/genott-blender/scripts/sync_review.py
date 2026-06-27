# scripts/sync_review.py
import os
import shutil
import glob

def main():
    workspace_dir = "PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender"
    target_dir = os.path.join(workspace_dir, "temp_review")
    
    # Create temp_review directory if it does not exist
    os.makedirs(target_dir, exist_ok=True)
    
    # 1. Grab all .md files in the workspace root
    root_md_files = glob.glob(os.path.join(workspace_dir, "*.md"))
    
    # 2. Grab all .md files in docs/architecture/
    docs_md_files = glob.glob(os.path.join(workspace_dir, "docs", "architecture", "*.md"))
    
    # 3. Reference any external artifacts (e.g. TASK_BOARD if located in artifacts folder)
    artifact_board = "PROJECT_ROOT/.gemini/antigravity-cli/brain/3496fc80-3ea9-4817-8bc4-b4e0e2ff7b60/TASK_BOARD.md"
    
    all_sources = root_md_files + docs_md_files
    if os.path.exists(artifact_board):
        all_sources.append(artifact_board)
        
    print(f"[SyncReview] Scanning and mirroring all Markdown (.md) reports to: {target_dir}")
    for src in all_sources:
        filename = os.path.basename(src)
        dst = os.path.join(target_dir, filename)
        try:
            shutil.copy2(src, dst)
            print(f"  ✓ Mirrored: {filename}")
        except Exception as e:
            print(f"  ✗ Failed to copy {filename}: {e}")

if __name__ == "__main__":
    main()
