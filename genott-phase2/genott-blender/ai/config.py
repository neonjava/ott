# ai/config.py
import os

class Config:
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FACES_DIR = os.path.join(PROJECT_DIR, "frontend", "static", "faces")
    VIDEO_DIR = os.path.join(PROJECT_DIR, "frontend", "static", "videos")
    SADTALKER_DIR = os.path.join(PROJECT_DIR, "SadTalker")
    SADTALKER_CHECKPOINTS = os.path.join(SADTALKER_DIR, "checkpoints")
    PYTHON_VENV = os.path.join(PROJECT_DIR, "venv", "bin", "python3")

    # Switchable provider settings
    LIP_SYNC_PROVIDER = "sadtalker"  # Switch to 'musetalk' or 'liveportrait'
    VIDEO_RENDERER = "blender"     # Switch to 'blender' or 'unreal'
    ENABLE_LIPSYNC = False
    DEBUG_KEEP_INTERMEDIATE = True

    # Configurable Render Profiles: 'development', 'testing', 'preview', 'production', 'ultra'
    RENDER_PROFILE = "testing"  # Switch to 'production' for HD showcase

