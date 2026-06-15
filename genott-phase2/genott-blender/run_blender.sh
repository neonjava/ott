#!/bin/bash
# run_blender.sh

# Resolve base directories
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

echo "=========================================================="
echo " Starting GenOTT Blender Character Animation Project"
echo "=========================================================="

# 1. Activate Python virtual environment
if [ -d "venv" ]; then
    echo "[System] Activating python virtual environment..."
    source venv/bin/activate
else
    echo "[ERROR] Virtual environment 'venv' not found! Run setup.sh first."
    exit 1
fi

# 2. Verify Blender executable
if command -v blender &> /dev/null; then
    echo "[System] Found Blender installation: $(blender --version | head -n 1)"
else
    echo "[WARNING] 'blender' CLI binary not found in PATH."
    echo "          The system will execute high-fidelity mock renders using ffmpeg."
fi

# 3. Create required assets folders
echo "[System] Creating assets directory layout..."
mkdir -p ai/assets/characters
mkdir -p ai/assets/animations
mkdir -p ai/assets/environments

# Generate demo mock placeholders if empty
echo "[System] Creating placeholder demo assets..."
touch ai/assets/characters/thor.glb
touch ai/assets/characters/tony_stark.glb
touch ai/assets/characters/hulk.glb

touch ai/assets/animations/fly.fbx
touch ai/assets/animations/land.fbx
touch ai/assets/animations/walk.fbx
touch ai/assets/animations/run.fbx
touch ai/assets/animations/talk.fbx
touch ai/assets/animations/attack.fbx
touch ai/assets/animations/raise_weapon.fbx
touch ai/assets/animations/victory_pose.fbx

touch ai/assets/environments/city.blend
touch ai/assets/environments/battlefield.blend
touch ai/assets/environments/snow_valley.blend

# 4. Start Flask on separate port 5001 to prevent conflicts
echo "[System] Starting Flask Server on http://localhost:5001 ..."
export FLASK_RUN_PORT=5001
python3 app.py
