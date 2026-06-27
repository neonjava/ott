import os
import uuid
import threading
import subprocess
import shutil
import sys
from flask import Flask, render_template, jsonify, request, send_from_directory

app = Flask(__name__, static_folder='static', template_folder='templates')

# Directory where the final video will be placed for serving
GENERATED_VIDEO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'videos'))
os.makedirs(GENERATED_VIDEO_DIR, exist_ok=True)

# Store running tasks
tasks = {}

def run_pipeline(task_id, source_image, audio_path, checkpoint_dir, result_dir):
    """Run the SadTalker pipeline in a subprocess.
    The generated video (talking head) will be moved to GENERATED_VIDEO_DIR as '<task_id>.mp4'.
    """
    # Build command – use high‑resolution (512 px) and enable GFPGAN enhancer
    inference_path = 'PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott/SadTalker/inference.py'
    cmd = [
        sys.executable, inference_path,
        '--driven_audio', audio_path,
        '--source_image', source_image,
        '--checkpoint_dir', checkpoint_dir,
        '--result_dir', result_dir,
        '--size', '512',
        '--preprocess', 'full',
        '--enhancer', 'gfpgan'
    ]
    # Execute the command
    proc = subprocess.Popen(cmd, cwd=os.path.abspath('..'))
    proc.wait()
    # After completion, move the generated file (assuming one mp4 in result_dir)
    try:
        generated_files = [f for f in os.listdir(result_dir) if f.lower().endswith('.mp4')]
        if generated_files:
            src = os.path.join(result_dir, generated_files[0])
            dst = os.path.join(GENERATED_VIDEO_DIR, f"{task_id}.mp4")
            shutil.move(src, dst)
            # Run GFPGAN enhancement in‑place (high‑res up‑scale)
            try:
                from .gfpgan_enhance import enhance_video_with_gfpgan
                enhance_video_with_gfpgan(dst, dst)
            except Exception as e:
                print(f"[SadTalker] GFPGAN enhancement failed: {e}")
    finally:
        tasks[task_id] = 'done'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Parameters could be extended; for now use fixed paths
    source_image = os.path.abspath('../static/faces/tony_stark.png')
    audio_path = os.path.abspath('../SadTalker/examples/driven_audio/bus_chinese.wav')
    checkpoint_dir = os.path.abspath('../SadTalker/checkpoints')
    result_dir = os.path.abspath('../static/videos/tmp_test')
    os.makedirs(result_dir, exist_ok=True)
    task_id = str(uuid.uuid4())
    tasks[task_id] = 'running'
    thread = threading.Thread(target=run_pipeline, args=(task_id, source_image, audio_path, checkpoint_dir, result_dir))
    thread.start()
    return jsonify({'task_id': task_id})

@app.route('/status/<task_id>')
def status(task_id):
    state = tasks.get(task_id, 'not_found')
    return jsonify({'status': state})

@app.route('/video/<task_id>')
def video(task_id):
    video_path = os.path.join(GENERATED_VIDEO_DIR, f"{task_id}.mp4")
    if os.path.exists(video_path):
        return send_from_directory(GENERATED_VIDEO_DIR, f"{task_id}.mp4")
    return 'Video not ready', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
