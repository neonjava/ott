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

    try:
        from video_generator import generate_video
        result = generate_video(
            prompt=prompt,
            num_frames=num_frames,
            width=width,
            height=height,
            num_steps=steps,
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


# ── RUN ──

if __name__ == "__main__":
    init_db()

    # Create static/videos directory
    os.makedirs(os.path.join(os.path.dirname(__file__), "static", "videos"), exist_ok=True)

    print("\n[GenOTT] Running at http://localhost:5000\n")
    app.run(debug=True, port=5000)
