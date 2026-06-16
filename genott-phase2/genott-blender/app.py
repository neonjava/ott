import os
import json
import uuid
import random
import time
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

from database import init_db, save_project, get_all_projects, get_project, delete_project
from video_generator import load_pipeline, concatenate_videos, add_audio_to_video, get_pipeline_info, score_movie_quality

# Import the new modular architectural library layout
from ai.config import Config
from ai.character.library import CharacterLibrary
from ai.storyboard.planner import ScenePlanner
from ai.voice.generator import VoiceSystem
from ai.lipsync.sadtalker import SadTalkerProvider
from ai.renderer.blender import BlenderVideoRenderer

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Architectures & Services
char_library = CharacterLibrary(faces_dir=Config.FACES_DIR)
scene_planner = ScenePlanner(char_library=char_library)
voice_system = VoiceSystem(output_dir=Config.VIDEO_DIR)

# Always use blender renderer for now
video_renderer = BlenderVideoRenderer()

# Dynamically select lip-sync provider
if Config.LIP_SYNC_PROVIDER == "sadtalker":
    lipsync_provider = SadTalkerProvider(
        python_venv_path=Config.PYTHON_VENV,
        sadtalker_dir=Config.SADTALKER_DIR,
        checkpoints_dir=Config.SADTALKER_CHECKPOINTS
    )
else:
    lipsync_provider = None

# Global execution logs
execution_logs = {}

def update_execution_log(generation_id, msg):
    if generation_id not in execution_logs:
        execution_logs[generation_id] = []
        # Prevent memory leak by keeping only the last 20 generation logs
        if len(execution_logs) > 20:
            oldest_key = list(execution_logs.keys())[0]
            del execution_logs[oldest_key]
    log_str = f"[{time.strftime('%H:%M:%S')}] {msg}"
    execution_logs[generation_id].append(log_str)
    print(f"[Architect Log] {generation_id}: {msg}")


# ── PAGES ──

@app.route("/api/test-render", methods=["POST"])
def api_test_render():
    """Triggers real, sandboxed Flatpak Blender render test pipeline."""
    try:
        from test_render import run_test_render
        output_filename = "blender_test.mp4"
        output_path = os.path.join(Config.VIDEO_DIR, output_filename)
        
        # Executes actual Blender rendering process
        run_test_render(output_path)
        
        return jsonify({
            "status": "success",
            "url": f"/static/videos/{output_filename}",
            "message": "Real Blender animation compiled successfully!"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Blender pipeline execution error: {str(e)}"
        }), 500

@app.route("/api/character-animation-test", methods=["GET", "POST"])
def api_character_animation_test():
    """Triggers and validates real character animation pipeline."""
    try:
        # Run validation in the same virtualenv python for OpenCV compatibility
        import subprocess
        project_dir = os.path.dirname(os.path.abspath(__file__))
        venv_python = os.path.join(project_dir, "venv", "bin", "python3")
        script_path = os.path.join(project_dir, "run_humanoid_validation.py")
        
        print("[App] Running humanoid validation script...")
        result = subprocess.run([venv_python, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Read the generated report
        report_path = os.path.join(project_dir, "character_animation_validation.md")
        report_content = ""
        if os.path.exists(report_path):
            with open(report_path, "r") as f:
                report_content = f.read()
        
        if result.returncode == 0:
            return jsonify({
                "status": "success",
                "message": "Character animation validation completed successfully!",
                "video_url": "/static/videos/character_animation_test.mp4",
                "report": report_content
            })
        else:
            return jsonify({
                "status": "fail",
                "message": "Character animation validation failed.",
                "error": result.stderr or result.stdout,
                "report": report_content
            }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Validation pipeline execution error: {str(e)}"
        }), 500

@app.route("/api/list-assets", methods=["GET"])
def api_list_assets():
    """Returns the list of character models and animation actions."""
    import glob
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(project_dir, "assets")
    
    # Dynamically find character .glb files
    characters = []
    char_dir = os.path.join(assets_dir, "characters")
    if os.path.exists(char_dir):
        characters = [os.path.basename(f) for f in glob.glob(os.path.join(char_dir, "*.glb"))]
    
    return jsonify({
        "Characters": characters,
        "Animations": ["Walk", "Run", "Survey", "Idle", "Attack", "Jump"]
    })

@app.route("/api/render-action", methods=["POST"])
def api_render_action():
    """Renders specific character performing a specific action using the ActionMapper."""
    data = request.get_json() or {}
    character = data.get("character", "fox")
    action = data.get("action", "Walk")
    
    try:
        import subprocess
        project_dir = os.path.dirname(os.path.abspath(__file__))
        venv_python = os.path.join(project_dir, "venv", "bin", "python3")
        script_path = os.path.join(project_dir, "run_render_action.py")
        
        print(f"[App] Rendering action: character={character}, action={action}...")
        result = subprocess.run([
            venv_python, script_path, 
            "--character", character, 
            "--action", action
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            video_filename = f"{action.lower()}_preview.mp4"
            return jsonify({
                "status": "success",
                "video_url": f"/static/videos/{video_filename}"
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Render failed: {result.stderr or result.stdout}"
            }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/project/<int:project_id>")
def project_page(project_id):
    return render_template("index.html")


# ── API: MIGRATED CINEMATIC GENERATOR ──

@app.route("/api/generate-avatar-script", methods=["POST"])
def generate_avatar_script():
    """Converts user prompt script request into structured scene plans."""
    data = request.get_json() or {}
    avatar = data.get("avatar")
    
    if avatar:
        avatar_clean = avatar.lower().replace("_", " ")
        if "hulk" in avatar_clean:
            user_prompt = "A dramatic, high-impact cinematic sequence of the green superhero Hulk leaping into battle, smashing ruins, roaring in anger, and standing victorious."
            avatar_name = "Hulk"
        elif "stark" in avatar_clean or "iron" in avatar_clean:
            user_prompt = "A high-tech cinematic sequence of Tony Stark in the crimson Iron Man armor, launching from a lab, flying through clouds, shooting repulsors, and landing heroically."
            avatar_name = "Tony Stark"
        else:
            user_prompt = "An epic cinematic sequence of Thor wielding the Stormbreaker battleaxe, summoning lightning, fighting villains, and shouting in triumph."
            avatar_name = "Thor"
        scene_count = 6  # 6 scenes of 5 seconds = 30 seconds
    else:
        user_prompt = data.get("prompt", "Thor arrives from the sky and lands on a battlefield").strip()
        scene_count = int(data.get("count", 3))
        avatar_name = "Avatar"

    plans = scene_planner.plan_story(user_prompt, scene_count=scene_count)
    
    # Format plans back to the legacy UI structure JSON
    formatted_scenes = []
    for plan in plans:
        # Override character name if generating for a specific avatar to ensure consistency
        if avatar:
            plan.character_name = avatar_name
        formatted_scenes.append({
            "title": f"Scene {plan.scene_number}: {plan.action}",
            "dialogue": plan.dialogue.text if plan.dialogue else "",
            "description": plan.narration or f"{plan.character_name} performing {plan.action} in {plan.location}",
            "video_prompt": f"{plan.character_name} action: {plan.action}, location: {plan.location}, shot: {plan.camera_shot}",
            # Pass new architectural plan details to frontend
            "location": plan.location,
            "action": plan.action,
            "camera_shot": plan.camera_shot,
            "character_name": plan.character_name
        })

    return jsonify({
        "title": f"{avatar_name} 30-Second Cinematic Storyboard",
        "scenes": formatted_scenes
    })


@app.route("/api/generate-movie", methods=["POST"])
def api_generate_movie():
    """Automated movie generation pipeline (Rule-Based, No LLM)."""
    data = request.get_json() or {}
    character = data.get("character", "humanoid")
    script = data.get("script", "")
    
    if not script:
        return jsonify({"error": "No script provided"}), 400
        
    generation_id = f"movie_{uuid.uuid4().hex[:8]}"
    update_execution_log(generation_id, "Starting automated movie generation...")
    
    # 1. & 2. & 3. Parse script, extract scenes, determine actions
    try:
        scenes = scene_planner.plan_rule_based(script, character)
    except Exception as e:
        return jsonify({"error": f"Scene planning failed: {str(e)}"}), 500
        
    update_execution_log(generation_id, f"Extracted {len(scenes)} scenes.")
    
    # Render scenes
    shared_seed = random.randint(1, 999999)
    temp_video_files = []
    temp_audio_files = []
    storyboard_thumbs = []
    
    try:
        for idx, plan in enumerate(scenes):
            update_execution_log(generation_id, f"Processing Scene {idx+1}: {plan.action}...")
            
            # 4. Voice Generation (Dialogue or Narration)
            voice_file = None
            if plan.dialogue:
                update_execution_log(generation_id, f"Synthesizing dialogue for: {plan.dialogue.speaker}...")
                audio_res = voice_system.synthesize_dialogue(plan.dialogue.text, plan.dialogue.voice_profile)
                voice_file = audio_res["audio_path"]
            elif plan.narration:
                update_execution_log(generation_id, f"Synthesizing narration: {plan.narration[:40]}...")
                audio_res = voice_system.synthesize_narration(plan.narration)
                voice_file = audio_res["audio_path"]
            else:
                update_execution_log(generation_id, f"Synthesizing narration for scene...")
                narration_text = f"The {plan.character_name} prepares to {plan.action}."
                audio_res = voice_system.synthesize_narration(narration_text)
                voice_file = audio_res["audio_path"]
                
            if voice_file:
                temp_audio_files.append(voice_file)
            
            # 6. Render every scene using Blender
            scene_mp4 = os.path.join(Config.VIDEO_DIR, f"scene_{generation_id}_{idx}.mp4")
            video_renderer.render_scene(plan, shared_seed, scene_mp4, generation_id=generation_id)
            temp_video_files.append(scene_mp4)
            
            # Collect storyboard thumbnail
            thumb_path = scene_mp4.replace(".mp4", "_thumb.png")
            if os.path.exists(thumb_path):
                storyboard_thumbs.append(f"/static/videos/scene_{generation_id}_{idx}_thumb.png")
            
            # 5. Apply Lip Sync or Audio Merge
            char_profile = char_library.get_character(plan.character_name)
            if plan.dialogue and getattr(Config, "ENABLE_LIPSYNC", False) and lipsync_provider and char_profile:
                update_execution_log(generation_id, "Applying Lip-Sync engine...")
                lip_synced_mp4 = os.path.join(Config.VIDEO_DIR, f"lipsync_{generation_id}_{idx}.mp4")
                lipsync_provider.run_lipsync(
                    image_path=char_profile.face_reference_img,
                    audio_path=voice_file,
                    output_path=lip_synced_mp4,
                    generation_id=generation_id
                )
                temp_video_files[-1] = lip_synced_mp4
                if os.path.exists(scene_mp4):
                    os.remove(scene_mp4)
            elif voice_file:
                merged_mp4 = os.path.join(Config.VIDEO_DIR, f"final_scene_{generation_id}_{idx}.mp4")
                update_execution_log(generation_id, "Merging dialogue audio...")
                add_audio_to_video(scene_mp4, voice_file, merged_mp4)
                temp_video_files[-1] = merged_mp4
                if os.path.exists(scene_mp4):
                    os.remove(scene_mp4)
            
        # 7. Stitch scenes together
        update_execution_log(generation_id, "Stitching scenes together...")
        final_filename = "final_movie.mp4" # As requested by user
        final_filepath = os.path.join(Config.VIDEO_DIR, final_filename)
        
        from movie_assembler import assemble_movie
        success, result_path_or_err, final_dur = assemble_movie(
            generation_id, Config.VIDEO_DIR, "final_movie.mp4",
            scene_files=temp_video_files
        )
        if not success:
            raise RuntimeError(f"Movie Assembly Failed: {result_path_or_err}")
            
        final_filepath = result_path_or_err
        # Cleanup
        for f in temp_video_files + temp_audio_files:
            if os.path.exists(f):
                os.remove(f)
                
        # 8. Produce final movie
        update_execution_log(generation_id, "Movie compilation finished.")
        # Score final quality
        expected_dur = sum(s.duration for s in scenes)
        quality_metrics = score_movie_quality(final_filepath, expected_dur)
        update_execution_log(generation_id, f"Movie Quality Score: {quality_metrics.get('score')}/100")

        return jsonify({
            "status": "success",
            "movie": f"/static/videos/{os.path.basename(final_filepath)}",
            "duration": final_dur,
            "storyboard": storyboard_thumbs,
            "scenes": [s.__dict__ if hasattr(s, "__dict__") else s for s in scenes],
            "quality": quality_metrics
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Cleanup on failure
        for f in temp_video_files:
            if os.path.exists(f):
                try: os.remove(f)
                except: pass
        return jsonify({"error": str(e)}), 500

@app.route('/api/movie/<generation_id>', methods=['GET'])
def api_get_movie(generation_id):
    """Retrieve a generated movie by its generation ID."""
    filepath = os.path.join(Config.VIDEO_DIR, f"{generation_id}_final_movie.mp4")
    if os.path.exists(filepath):
        from movie_assembler import get_video_info
        info = get_video_info(filepath)
        dur = float(info.get("format", {}).get("duration", 0)) if info else 0.0
        return jsonify({
            "status": "success",
            "movie": f"/static/videos/{generation_id}_final_movie.mp4",
            "duration": dur
        })
    return jsonify({"status": "error", "message": "Movie not found"}), 404

@app.route("/api/generate-avatar-video", methods=["POST"])
def generate_avatar_video_route():
    """Structured Cinematic Pipeline execution route."""
    data = request.get_json() or {}
    scenes_data = data.get("scenes", [])
    generation_id = data.get("generation_id", f"cinematic_{uuid.uuid4().hex[:8]}")

    if not scenes_data:
        return jsonify({"error": "No storyboard scenes provided"}), 400

    update_execution_log(generation_id, "Initiating Cinematic Movie Generation pipeline...")

    # Establish sequence layout seeds to preserve visual composition parameters
    shared_seed = random.randint(1, 999999)
    temp_video_files = []
    temp_audio_files = []

    try:
        for idx, scene in enumerate(scenes_data):
            update_execution_log(generation_id, f"Processing Segment {idx+1}/{len(scenes_data)}...")
            
            # Map raw JSON to plan dataclass
            char_name = scene.get("character_name") or "Thor"
            action = scene.get("action") or "landing"
            location = scene.get("location") or "battlefield"
            camera_shot = scene.get("camera_shot") or "cinematic wide"
            dialogue_text = scene.get("dialogue", "").strip()
            narration_text = scene.get("description", "").strip()

            from ai.storyboard.models import ScenePlan, DialogueLine
            char_profile = char_library.get_character(char_name)
            voice = char_profile.voice_profile if char_profile else "en-GB-RyanNeural"

            plan = ScenePlan(
                scene_number=idx + 1,
                character_name=char_name,
                location=location,
                action=action,
                camera_shot=camera_shot,
                duration=4.0,
                dialogue=DialogueLine(char_name, dialogue_text, voice) if dialogue_text else None,
                narration=narration_text if not dialogue_text else None
            )

            # 1. Voice Synthesis Pipeline
            voice_file = None
            if plan.dialogue:
                update_execution_log(generation_id, f"Synthesizing dialogue speech voiceover for speaker: {plan.character_name}...")
                audio_res = voice_system.synthesize_dialogue(plan.dialogue.text, plan.dialogue.voice_profile)
                voice_file = audio_res["audio_path"]
            elif plan.narration:
                update_execution_log(generation_id, "Synthesizing scene narrator track...")
                audio_res = voice_system.synthesize_narration(plan.narration)
                voice_file = audio_res["audio_path"]

            if voice_file:
                temp_audio_files.append(voice_file)

            # 2. Render Scene Visuals
            scene_raw_mp4 = os.path.join(Config.VIDEO_DIR, f"raw_scene_{generation_id}_{idx}.mp4")
            update_execution_log(generation_id, "Rendering scene visual elements...")
            video_renderer.render_scene(plan, shared_seed, scene_raw_mp4, generation_id=generation_id)
            temp_video_files.append(scene_raw_mp4)

            # 3. Apply Lip Sync if dialogue voice is active AND enabled in config
            if plan.dialogue and getattr(Config, "ENABLE_LIPSYNC", False) and lipsync_provider and char_profile:
                update_execution_log(generation_id, "Applying Lip-Sync engine overlay...")
                lip_synced_mp4 = os.path.join(Config.VIDEO_DIR, f"lipsync_scene_{generation_id}_{idx}.mp4")
                
                # Render lip-sync from facial reference caching
                lipsync_provider.run_lipsync(
                    image_path=char_profile.face_reference_img,
                    audio_path=voice_file,
                    output_path=lip_synced_mp4,
                    generation_id=generation_id
                )
                
                # Replace segment with lip-synced video clip
                temp_video_files[-1] = lip_synced_mp4
                # Remove raw scene segment file only if debug mode is disabled
                if not getattr(Config, "DEBUG_KEEP_INTERMEDIATE", False) and os.path.exists(scene_raw_mp4):
                    os.remove(scene_raw_mp4)
            else:
                # Merge dialogue/narration audio directly with video track using ffmpeg (preserves action scene visual frames)
                if voice_file:
                    merged_mp4 = os.path.join(Config.VIDEO_DIR, f"final_scene_{generation_id}_{idx}.mp4")
                    update_execution_log(generation_id, "Merging dialogue speech directly over action visual track (FFmpeg)...")
                    add_audio_to_video(scene_raw_mp4, voice_file, merged_mp4)
                    temp_video_files[-1] = merged_mp4
                    
                    # Remove raw scene segment file only if debug mode is disabled
                    if not getattr(Config, "DEBUG_KEEP_INTERMEDIATE", False) and os.path.exists(scene_raw_mp4):
                        os.remove(scene_raw_mp4)

        # Stitch all segments together
        update_execution_log(generation_id, "Compiling segments into final movie file cut...")
        final_filename = f"cinematic_{generation_id}.mp4"
        final_filepath = os.path.join(Config.VIDEO_DIR, final_filename)

        concatenate_videos(temp_video_files, final_filepath, transition="fade")

        # Cleanup all temporary segment assets except if explicitly flagged to keep
        if not data.get("keep_segments", False) and not getattr(Config, "DEBUG_KEEP_INTERMEDIATE", False):
            for f in temp_video_files + temp_audio_files:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except Exception:
                        pass
        else:
            update_execution_log(generation_id, "Preserving intermediate scene segments for verification.")

        update_execution_log(generation_id, "Movie compilation finished successfully!")

        return jsonify({
            "url": f"/static/videos/{final_filename}",
            "filename": final_filename,
            "status": "success"
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        update_execution_log(generation_id, f"Pipeline Error: {e}")
        # Cleanup stubs
        if not data.get("keep_segments", False):
            for f in temp_video_files + temp_audio_files:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except Exception:
                        pass
        return jsonify({"error": str(e)}), 500


@app.route("/api/video-progress/<generation_id>", methods=["GET"])
def video_progress_route(generation_id):
    """Retrieve cinematic pipeline build logs."""
    logs = execution_logs.get(generation_id, [])
    return jsonify({"logs": logs})


# Legacy / Boilerplate routing systems preserved...

@app.route("/api/projects", methods=["GET"])
def api_get_projects():
    return jsonify(get_all_projects())

@app.route("/api/projects", methods=["POST"])
def api_save_project():
    data = request.get_json() or {}
    project_id = save_project(data.get("title", "Untitled Film"), data.get("script", ""), data.get("genre", ""), data.get("style", ""), data.get("scenes", []))
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

@app.route("/api/gpu-status", methods=["GET"])
def gpu_status():
    return jsonify(get_pipeline_info())


if __name__ == "__main__":
    init_db()
    os.makedirs(Config.VIDEO_DIR, exist_ok=True)
    port = int(os.environ.get("FLASK_RUN_PORT", 5001))
    app.run(debug=True, port=port)
