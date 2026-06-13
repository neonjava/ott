#!/bin/bash
# run.sh - Start GenOTT & Ollama servers and aggregate logs to project.log

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${PROJECT_DIR}/project.log"

# Clear old log file
echo "=== Starting GenOTT Project: $(date) ===" > "$LOG_FILE"

echo "--------------------------------------------------------"
echo "  Starting GenOTT Project Services"
echo "  All output is redirected to: ${LOG_FILE}"
echo "--------------------------------------------------------"

# 1. Start Ollama if it is not already running
if curl -s http://127.0.0.1:11434/api/tags &>/dev/null; then
    echo "[✓] Ollama is already running." | tee -a "$LOG_FILE"
else
    echo "[*] Starting Ollama server in background..." | tee -a "$LOG_FILE"
    nohup ollama serve >> "$LOG_FILE" 2>&1 &
    
    # Wait for Ollama to spin up
    for i in {1..10}; do
        if curl -s http://127.0.0.1:11434/api/tags &>/dev/null; then
            echo "[✓] Ollama server started successfully." | tee -a "$LOG_FILE"
            break
        fi
        sleep 1
    done
fi

# 2. Start Flask Server
echo "[*] Starting Flask server in background..." | tee -a "$LOG_FILE"
cd "$PROJECT_DIR"
source venv/bin/activate
nohup python3 -u app.py >> "$LOG_FILE" 2>&1 &

echo "[✓] Services started in the background!"
echo ""
echo "To monitor ALL logs in real-time, run this command in your terminal:"
echo "👉 tail -f ${LOG_FILE}"
echo ""
echo "Or visit the app at: http://localhost:5000"
echo "--------------------------------------------------------"
