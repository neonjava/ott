#!/usr/bin/env python3
import os
import shutil
import glob
import subprocess

REPO_DIR = "PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender"
ARCHIVE_BASE = "/run/media/neonjava/neonjava/ott_archive"

# Archive subdirectories
DIRS = {
    "renders": os.path.join(ARCHIVE_BASE, "renders"),
    "movies": os.path.join(ARCHIVE_BASE, "movies"),
    "benchmarks": os.path.join(ARCHIVE_BASE, "benchmarks"),
    "logs": os.path.join(ARCHIVE_BASE, "logs"),
    "reports": os.path.join(ARCHIVE_BASE, "reports"),
    "quarantine": os.path.join(ARCHIVE_BASE, "quarantine")
}

def get_dir_size(path):
    total = 0
    if not os.path.exists(path):
        return 0
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            if not os.path.islink(fp):
                total += os.path.getsize(fp)
    return total

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def main():
    print("=== Storage & Disk Management Utility ===")
    
    # Create directories if missing
    for name, p in DIRS.items():
        os.makedirs(p, exist_ok=True)
        
    initial_repo_size = get_dir_size(REPO_DIR)
    print(f"Initial Repository Size: {format_size(initial_repo_size)}")
    
    moved_files = []
    deleted_files = []
    quarantined_files = []
    
    # 1. Archive finished movies and thumbnails from static/videos/
    video_dir = os.path.join(REPO_DIR, "static", "videos")
    if os.path.exists(video_dir):
        # Movie patterns
        for fpath in glob.glob(os.path.join(video_dir, "*.mp4")):
            fname = os.path.basename(fpath)
            # Skip templates/essentials
            if "walk_preview" in fname or "idle_preview" in fname or "consistency" in fname:
                continue
            
            # Destination path
            dest = os.path.join(DIRS["movies"], fname)
            try:
                shutil.move(fpath, dest)
                moved_files.append((fpath, dest, os.path.getsize(dest)))
            except Exception as e:
                print(f"Error moving {fname}: {e}")
                
        # Thumbnail patterns
        for fpath in glob.glob(os.path.join(video_dir, "*.png")):
            fname = os.path.basename(fpath)
            if "avatar" in fname:
                continue
            dest = os.path.join(DIRS["renders"], fname)
            try:
                shutil.move(fpath, dest)
                moved_files.append((fpath, dest, os.path.getsize(dest)))
            except Exception as e:
                print(f"Error moving {fname}: {e}")
                
    # 2. Cleanup Target: pycache, pyc, tmp files
    for root, dirs, files in os.walk(REPO_DIR):
        # Skip .git, venv
        if ".git" in root or "venv" in root:
            continue
            
        for d in list(dirs):
            if d in ("__pycache__", ".pytest_cache", ".cache"):
                dp = os.path.join(root, d)
                sz = get_dir_size(dp)
                try:
                    shutil.rmtree(dp)
                    deleted_files.append((dp, sz))
                    dirs.remove(d)
                except Exception as e:
                    print(f"Error deleting cache dir {dp}: {e}")
                    
        for f in files:
            fp = os.path.join(root, f)
            sz = os.path.getsize(fp)
            if f.endswith(('.pyc', '.pyo', '.tmp', '.temp')) or f.startswith('tmp_'):
                try:
                    os.remove(fp)
                    deleted_files.append((fp, sz))
                except Exception as e:
                    print(f"Error deleting temp file {fp}: {e}")
                    
    # 3. Check for files larger than 100MB to quarantine if they are untracked
    for root, dirs, files in os.walk(REPO_DIR):
        if ".git" in root or "venv" in root or "SadTalker" in root or "BasicSR" in root:
            continue
        for f in files:
            fp = os.path.join(root, f)
            sz = os.path.getsize(fp)
            if sz > 100 * 1024 * 1024:  # > 100MB
                # Verify if it is tracked by git
                cmd = ["git", "-C", REPO_DIR, "ls-files", "--error-unmatch", fp]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if res.returncode != 0:
                    # Untracked large file - move to quarantine
                    dest = os.path.join(DIRS["quarantine"], f)
                    try:
                        shutil.move(fp, dest)
                        quarantined_files.append((fp, dest, sz))
                        print(f"Quarantined untracked file (>100MB): {f}")
                    except Exception as e:
                        print(f"Error quarantining {f}: {e}")
                        
    final_repo_size = get_dir_size(REPO_DIR)
    archive_size = get_dir_size(ARCHIVE_BASE)
    
    total_recovered = sum(x[2] for x in moved_files) + sum(x[1] for x in deleted_files) + sum(x[2] for x in quarantined_files)
    
    print(f"Final Repository Size: {format_size(final_repo_size)}")
    print(f"Total Recovered Space: {format_size(total_recovered)}")
    
    # Generate STORAGE_REPORT.md
    largest_files = []
    for root, dirs, files in os.walk(REPO_DIR):
        if ".git" in root or "venv" in root:
            continue
        for f in files:
            fp = os.path.join(root, f)
            largest_files.append((fp, os.path.getsize(fp)))
    largest_files.sort(key=lambda x: x[1], reverse=True)
    
    storage_report = f"""# Storage Report

## Repository and Archive Size
| Storage Target | Size |
|----------------|------|
| Repository Directory (`genott-blender`) | {format_size(final_repo_size)} |
| External Archive (`ott_archive`) | {format_size(archive_size)} |
| Space Recovered in this Run | {format_size(total_recovered)} |

## 10 Largest Files in Repository
"""
    for fp, sz in largest_files[:10]:
        rel = os.path.relpath(fp, REPO_DIR)
        storage_report += f"- `{rel}`: {format_size(sz)}\n"
        
    storage_report += """
## Moved/Archived Files
| Original File | Archive Location | Size |
|---------------|------------------|------|
"""
    for orig, dest, sz in moved_files[:15]:
        storage_report += f"| `{os.path.basename(orig)}` | `{os.path.basename(dest)}` | {format_size(sz)} |\n"
    if len(moved_files) > 15:
        storage_report += f"| ... and {len(moved_files) - 15} more files ... | | |\n"
        
    with open("STORAGE_REPORT.md", "w") as f:
        f.write(storage_report)
    print("Saved STORAGE_REPORT.md")
    
    # Generate CLEANUP_REPORT.md
    cleanup_report = f"""# Cleanup Report

## Summary
- **Cache Directories Cleaned**: `__pycache__`, `.pytest_cache`, `.cache`
- **Temporary Files Deleted**: {len(deleted_files)} files
- **Storage Space Recovered**: {format_size(total_recovered)}
- **Quarantined Files (>100MB)**: {len(quarantined_files)} files

## Deleted Files Detail
| File/Directory Path | Size |
|---------------------|------|
"""
    for fp, sz in deleted_files[:15]:
        rel = os.path.relpath(fp, REPO_DIR) if fp.startswith(REPO_DIR) else fp
        cleanup_report += f"| `{rel}` | {format_size(sz)} |\n"
    if len(deleted_files) > 15:
        cleanup_report += f"| ... and {len(deleted_files) - 15} more files ... | |\n"
        
    cleanup_report += """
## Quarantined Files (>100MB)
| File Path | Quarantine Target | Size |
|-----------|-------------------|------|
"""
    for orig, dest, sz in quarantined_files:
        cleanup_report += f"| `{os.path.basename(orig)}` | `{os.path.basename(dest)}` | {format_size(sz)} |\n"
        
    with open("CLEANUP_REPORT.md", "w") as f:
        f.write(cleanup_report)
    print("Saved CLEANUP_REPORT.md")
    
    # Sync reports to Documents/md
    md_dir = "PROJECT_ROOT/Documents/md"
    os.makedirs(md_dir, exist_ok=True)
    with open(os.path.join(md_dir, "STORAGE_REPORT.md"), "w") as f:
        f.write(storage_report)
    with open(os.path.join(md_dir, "CLEANUP_REPORT.md"), "w") as f:
        f.write(cleanup_report)
        
    # Sync to brain artifact directory
    artifact_dir = "PROJECT_ROOT/.gemini/antigravity-cli/brain/3496fc80-3ea9-4817-8bc4-b4e0e2ff7b60"
    with open(os.path.join(artifact_dir, "STORAGE_REPORT.md"), "w") as f:
        f.write(storage_report)
    with open(os.path.join(artifact_dir, "CLEANUP_REPORT.md"), "w") as f:
        f.write(cleanup_report)
        
    print("Storage and cleanup reports successfully generated and synchronized.")

if __name__ == "__main__":
    main()
