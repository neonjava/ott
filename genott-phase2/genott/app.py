import os
import json
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from database import init_db, save_project, get_all_projects, get_project, delete_project

load_dotenv()

app = Flask(__name__)
CORS(app)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-sonnet-4-6"


# ── PAGES ──

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/project/<int:project_id>")
def project_page(project_id):
    return render_template("index.html")


# ── API: GENERATE ──

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    script = data.get("script", "").strip()
    genre  = data.get("genre", "sci-fi thriller")
    style  = data.get("style", "cinematic")
    count  = int(data.get("count", 5))

    if not script:
        return jsonify({"error": "Script is required."}), 400

    # We now call the local Ollama instance chat API
    OLLAMA_URL = "http://localhost:11434/api/chat"
    OLLAMA_MODEL = "llama3.2"

    system_prompt = """You are a professional film script supervisor and AI cinematography director for a Generative OTT platform. Your job is to break a story into cinematic scenes and produce structured data for AI video generation.

Return ONLY valid JSON. Use this exact format:
{
  "title": "Short film title (4-6 words)",
  "scenes": [
    {
      "title": "Scene title (5 words max)",
      "type": "Interior or Exterior",
      "setting": "Specific location description",
      "mood": "Single mood word",
      "characters": "Main characters present",
      "duration": "Estimated screen time e.g. 2 min",
      "description": "Vivid 2-3 sentence cinematic description of what happens and what the camera sees. Be specific about visuals — lighting, camera angles, action, expressions.",
      "video_prompt": "A detailed, ready-to-use AI video generation prompt for this scene. Include: the action, setting, lighting style, camera movement, visual aesthetic, mood, and technical specs (e.g. 4K, cinematic, film grain)."
    }
  ]
}"""

    user_prompt = f"""Break this story into exactly {count} cinematic scenes for a {genre} film with {style} visual style.

Story:
{script}

Return exactly {count} scenes in the JSON format specified."""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "format": "json",
                "stream": False
            },
            timeout=120,
        )

        resp_data = response.json()

        if "error" in resp_data:
            raise Exception(resp_data["error"])

        raw = resp_data.get("message", {}).get("content", "{}")
        print(f"\n[OLLAMA RAW RESPONSE]: {raw}\n")
        parsed = json.loads(raw)
        print(f"\n[OLLAMA PARSED OBJ]: {parsed}\n")

        # Handle both {"scenes": [...]} and a direct root array [...]
        scenes_list = []
        if isinstance(parsed, list):
            scenes_list = parsed
        elif isinstance(parsed, dict):
            scenes_list = parsed.get("scenes", [])

        # Ensure video_prompt exists for each scene
        for s in scenes_list:
            if "video_prompt" not in s:
                s["video_prompt"] = f"{s.get('description', '')} | Setting: {s.get('setting', '')} | Mood: {s.get('mood', '')} | {style} | {genre}"

        return jsonify({
            "title": parsed.get("title", "Untitled Film") if isinstance(parsed, dict) else "Untitled Film",
            "scenes": scenes_list,
        })

    except Exception as e:
        print(f"\n[OLLAMA ERROR, FALLING BACK]: {str(e)}\n")
        # Fallback to mock response
        return jsonify({
            "title": "Mock Film Title",
            "scenes": [
                {
                    "title": "The Awakening",
                    "type": "Interior",
                    "setting": "A dimly lit, futuristic laboratory.",
                    "mood": "Tense",
                    "characters": "Dr. Aris",
                    "duration": "1 min",
                    "description": "Dr. Aris stares at the glowing monitor, realizing the anomaly is not a glitch but a signal.",
                    "video_prompt": f"A cinematic tracking shot of a scientist in a futuristic lab. {style} visual style, {genre} genre. 4k, hyper-detailed."
                },
                {
                    "title": "The Chase",
                    "type": "Exterior",
                    "setting": "Rain-soaked neon streets.",
                    "mood": "Action",
                    "characters": "Dr. Aris, Unknown Pursuers",
                    "duration": "2 min",
                    "description": "Aris sprints through the crowded market, looking back as shadowy figures close in.",
                    "video_prompt": f"Fast-paced handheld camera following a person running through rain-soaked cyberpunk streets. {style} visual style, {genre}. Dynamic lighting."
                }
            ]
        })


# ── API: PROJECTS ──

@app.route("/api/projects", methods=["GET"])
def api_get_projects():
    return jsonify(get_all_projects())


@app.route("/api/projects", methods=["POST"])
def api_save_project():
    data = request.get_json()
    title  = data.get("title", "Untitled Film")
    script = data.get("script", "")
    genre  = data.get("genre", "")
    style  = data.get("style", "")
    scenes = data.get("scenes", [])

    if not script or not scenes:
        return jsonify({"error": "script and scenes are required."}), 400

    project_id = save_project(title, script, genre, style, scenes)
    return jsonify({"id": project_id, "message": "Project saved."}), 201


@app.route("/api/projects/<int:project_id>", methods=["GET"])
def api_get_project(project_id):
    project = get_project(project_id)
    if not project:
        return jsonify({"error": "Project not found."}), 404
    return jsonify(project)


@app.route("/api/projects/<int:project_id>", methods=["DELETE"])
def api_delete_project(project_id):
    delete_project(project_id)
    return jsonify({"message": "Deleted."})


# ── API: VIDEO GENERATION ──

@app.route("/api/gpu-status", methods=["GET"])
def gpu_status():
    """Check if GPU and video pipeline are available."""
    try:
        from video_generator import get_pipeline_info
        return jsonify(get_pipeline_info())
    except ImportError:
        return jsonify({
            "loaded": False,
            "error": "video_generator module not available. Install torch and diffusers.",
            "cuda_available": False,
        })
    except Exception as e:
        return jsonify({"loaded": False, "error": str(e)})


@app.route("/api/generate-video", methods=["POST"])
def generate_video_route():
    """Generate a video clip from a scene's video_prompt."""
    data = request.get_json()
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "prompt is required."}), 400

    num_frames = int(data.get("num_frames", 16))
    width = int(data.get("width", 512))
    height = int(data.get("height", 320))
    steps = int(data.get("steps", 25))
    generation_id = data.get("generation_id")

    try:
        from video_generator import generate_video
        result = generate_video(
            prompt=prompt,
            num_frames=num_frames,
            width=width,
            height=height,
            num_steps=steps,
            generation_id=generation_id,
        )
        return jsonify(result)

    except ImportError:
        return jsonify({
            "error": "Video generation not available. Install torch and diffusers first."
        }), 503
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Video generation failed: {str(e)}"}), 500


@app.route("/api/video-progress/<generation_id>", methods=["GET"])
def video_progress_route(generation_id):
    """Retrieve generation logs/steps in real-time."""
    try:
        from video_generator import get_generation_logs
        logs = get_generation_logs(generation_id)
        return jsonify({"logs": logs})
    except Exception as e:
        return jsonify({"logs": [], "error": str(e)})


@app.route("/api/generate-avatar-script", methods=["POST"])
def generate_avatar_script():
    data = request.get_json()
    avatar = data.get("avatar", "tony_stark")

    avatar_prompts = {
        "tony_stark": "Tony Stark (Iron Man) in his high-tech workshop, glowing chest arc reactor, adjusting holographic designs, cinematic lighting, 4k",
        "thor": "Thor (God of Thunder) standing on a cliff with dark storm clouds, holding glowing Mjolnir, lightning reflecting in his eyes, cinematic, 4k",
        "hulk": "Hulk (Green Giant) in a ruined urban street, green skin, massive muscles, breathing heavily, angry expressions, grit realism, 4k"
    }

    avatar_name = {
        "tony_stark": "Tony Stark / Iron Man",
        "thor": "Thor Odinson",
        "hulk": "The Incredible Hulk"
    }.get(avatar, "Tony Stark / Iron Man")

    OLLAMA_URL = "http://localhost:11434/api/chat"
    OLLAMA_MODEL = "llama3.2"

    system_prompt = """You are a professional cinematic storyteller. Generate a short 30-second storyboard script.
Return ONLY valid JSON. Format:
{
  "title": "Story Title",
  "scenes": [
    {
      "title": "Scene Name",
      "dialogue": "Short dialogue or internal monologue (1-2 sentences)",
      "description": "Cinematic visual description of the character performing an action.",
      "video_prompt": "A highly detailed text-to-video generation prompt describing the character, action, lighting, and camera movement. Focus heavily on character consistency."
    }
  ]
}"""

    user_prompt = f"""Write a short story breakdown consisting of exactly 10 short scenes (each representing 2 seconds of footage) for the avatar: {avatar_name}.
The visual style is cinematic action. Make sure each scene's video_prompt starts EXACTLY with: '{avatar_prompts.get(avatar, avatar_prompts["tony_stark"])}'.
You must keep the character's physical appearance, clothing, hair, facial features, and background scene details completely identical across all scenes to ensure strict temporal visual consistency. Keep dialogues dramatic and matching their personality."""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "format": "json",
                "stream": False
            },
            timeout=120,
        )
        resp_data = response.json()
        raw = resp_data.get("message", {}).get("content", "{}")
        parsed = json.loads(raw)
        return jsonify(parsed)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-avatar-video", methods=["POST"])
def generate_avatar_video_route():
    data = request.get_json()
    scenes = data.get("scenes", [])
    avatar = data.get("avatar", "tony_stark")
    generation_id = data.get("generation_id", "avatar_gen")

    if not scenes:
        return jsonify({"error": "No scenes provided"}), 400

    from video_generator import generate_video, concatenate_videos, generate_speech, add_audio_to_video, VIDEO_DIR, generation_logs
    import time
    import uuid
    import torch
    import random

    # Map avatar to edge-tts voice
    voice_map = {
        "tony_stark": "en-US-ChristopherNeural",  # Deep intelligent American male
        "thor": "en-GB-RyanNeural",                # Strong British male
        "hulk": "en-US-GuyNeural"                  # Deep husky American male
    }
    selected_voice = voice_map.get(avatar, "en-US-ChristopherNeural")

    # Generate a single shared random seed for the entire sequence to keepcomposition and character face consistent
    shared_seed = random.randint(1, 10000000)

    def update_log(msg):
        if generation_id not in generation_logs:
            generation_logs[generation_id] = []
        generation_logs[generation_id].append(f"[{time.strftime('%H:%M:%S')}] {msg}")
        print(f"[AvatarGen Log] {generation_id}: {msg}")

    temp_paths = []
    garbage_files = []

    try:
        for idx, scene in enumerate(scenes):
            update_log(f"Rendering segment {idx+1}/{len(scenes)}: {scene.get('title', 'Scene')}...")
            prompt = scene.get("video_prompt", "").strip()
            dialogue = scene.get("dialogue", "").strip()
            
            # 1. Render Video segment (2 seconds, 16 frames @ 8fps, using shared seed)
            res = generate_video(
                prompt=prompt,
                num_frames=16,
                width=512,
                height=320,
                num_steps=20,
                seed=shared_seed,
                generation_id=f"{generation_id}_part_{idx}"
            )
            raw_video_path = res["path"]
            garbage_files.append(raw_video_path)

            # Clear CUDA Cache to free VRAM for next segment
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # 2. Render Dialogue Audio segment using Edge TTS
            if dialogue:
                update_log(f"Synthesizing speech voiceover for beat {idx+1} using {selected_voice}...")
                audio_filename = f"speech_temp_{str(uuid.uuid4())[:8]}.mp3"
                audio_path = os.path.join(VIDEO_DIR, audio_filename)
                generate_speech(dialogue, audio_path, voice=selected_voice)
                garbage_files.append(audio_path)

                # 3. Merge Video + Audio into a single segment
                update_log(f"Stitching audio track into segment {idx+1}...")
                mixed_filename = f"mixed_temp_{str(uuid.uuid4())[:8]}.mp4"
                mixed_path = os.path.join(VIDEO_DIR, mixed_filename)
                add_audio_to_video(raw_video_path, audio_path, mixed_path)
                
                temp_paths.append(mixed_path)
                garbage_files.append(mixed_path)
            else:
                # Fallback to raw video if dialogue is empty
                temp_paths.append(raw_video_path)

        update_log("Compiling final cut: stitching all audio-video segments together...")
        final_filename = f"avatar_final_{str(uuid.uuid4())[:8]}.mp4"
        final_filepath = os.path.join(VIDEO_DIR, final_filename)

        concatenate_videos(temp_paths, final_filepath)

        # Cleanup all temporary segment and audio files
        for path in garbage_files:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

        update_log("Success! Final 30-second avatar clip with audio/narration is ready.")

        return jsonify({
            "url": f"/static/videos/{final_filename}",
            "filename": final_filename,
            "duration_sec": 30.0
        })
    except Exception as e:
        # Cleanup all temporary files on failure
        for path in garbage_files:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
        update_log(f"ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ── RUN ──

if __name__ == "__main__":
    init_db()

    # Create static/videos directory
    os.makedirs(os.path.join(os.path.dirname(__file__), "static", "videos"), exist_ok=True)

    print("\n[GenOTT] Running at http://localhost:5000\n")
    app.run(debug=True, port=5000)
