# Compatibility wrapper for app.py
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)
sys.path.append(os.path.join(PROJECT_DIR, "backend", "api"))

# Register refactored paths
for path in [os.path.join(PROJECT_DIR, "engine", "director"), os.path.join(PROJECT_DIR, "engine", "character"), os.path.join(PROJECT_DIR, "engine", "renderer"), os.path.join(PROJECT_DIR, "engine", "audio"), os.path.join(PROJECT_DIR, "pipeline", "storyboard")]:
    if path not in sys.path:
        sys.path.append(path)

from backend.api.app import app

if __name__ == "__main__":
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
