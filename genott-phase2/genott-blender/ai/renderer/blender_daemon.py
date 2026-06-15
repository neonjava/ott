import bpy
import sys
import os
import json
import time
import shutil
import subprocess
import math
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 5005
CHARACTER_FILE = "PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender/assets/characters/humanoid.glb"

def init_blender_env():
    print("[BlenderDaemon] Initializing persistent environment...")
    
    # 1. Clear scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 2. Setup GPU
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.cycles.samples = 1
    bpy.context.scene.render.resolution_x = 64
    bpy.context.scene.render.resolution_y = 64
    bpy.context.scene.render.fps = 12
    
    # 3. Import Character
    if os.path.exists(CHARACTER_FILE):
        bpy.ops.import_scene.gltf(filepath=CHARACTER_FILE)
    
    # 4. Setup Lighting
    light_data = bpy.data.lights.new(name="SunLight", type='SUN')
    light_data.energy = 3.0
    light_obj = bpy.data.objects.new(name="SunLight", object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = (5, -5, 10)
    
    # 5. Setup World
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    tree = world.node_tree
    for node in tree.nodes:
        tree.nodes.remove(node)
    bg_node = tree.nodes.new(type="ShaderNodeBackground")
    out_node = tree.nodes.new(type="ShaderNodeOutputWorld")
    bg_node.inputs['Color'].default_value = (0.5, 0.6, 0.7, 1.0)
    tree.links.new(bg_node.outputs['Background'], out_node.inputs['Surface'])
    
    print("[BlenderDaemon] Initialization complete.")

class RenderHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')

    def do_POST(self):
        if self.path == '/render':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                payload = json.loads(post_data)
                
                output_path = payload.get("output_path")
                action_name = payload.get("action", "idle")
                duration = payload.get("duration", 2.0)
                
                print(f"\\n[BlenderDaemon] Received job: {action_name} for {duration}s -> {output_path}")
                
                t_start = time.time()
                
                # Find armature
                armature = None
                for obj in bpy.context.scene.objects:
                    if obj.type == 'ARMATURE':
                        armature = obj
                        break
                        
                if armature and not armature.animation_data:
                    armature.animation_data_create()
                    
                # Assign action
                mapped_action = f"CharacterArmature|{action_name.capitalize()}"
                if "run" in action_name: mapped_action = "CharacterArmature|Run"
                elif "walk" in action_name: mapped_action = "CharacterArmature|Walk"
                elif "jump" in action_name: mapped_action = "CharacterArmature|Jump_Idle"
                elif "attack" in action_name: mapped_action = "CharacterArmature|Sword_Slash"
                elif "wave" in action_name: mapped_action = "CharacterArmature|Wave"
                
                selected_action = bpy.data.actions.get(mapped_action)
                if not selected_action:
                    selected_action = bpy.data.actions.get("CharacterArmature|Idle")
                    
                if armature and selected_action:
                    armature.animation_data.action = selected_action
                    
                # Frame range
                fps = 12
                if selected_action:
                    f_start = int(selected_action.frame_range[0])
                    f_end = int(selected_action.frame_range[1])
                else:
                    f_start = 1
                    f_end = int(duration * fps)
                    
                bpy.context.scene.frame_start = f_start
                bpy.context.scene.frame_end = f_end
                
                # Camera framing
                camera = None
                for obj in bpy.context.scene.objects:
                    if obj.type == 'CAMERA':
                        camera = obj
                        break
                if not camera:
                    cam_data = bpy.data.cameras.new("Camera")
                    camera = bpy.data.objects.new("Camera", cam_data)
                    bpy.context.collection.objects.link(camera)
                
                bpy.context.scene.camera = camera
                camera.location = (0, -4, 1.5)
                camera.rotation_euler = (math.radians(80), 0, 0)
                if armature:
                    camera.location = (armature.location.x, armature.location.y - 4, armature.location.z + 1.5)
                
                # Render
                import tempfile
                render_dir = tempfile.mkdtemp(prefix="blender_daemon_")
                bpy.context.scene.render.image_settings.file_format = 'PNG'
                bpy.context.scene.render.image_settings.color_mode = 'RGBA'
                bpy.context.scene.render.filepath = os.path.join(render_dir, "frame_")
                
                t_render_start = time.time()
                bpy.ops.render.render(animation=True)
                t_render_end = time.time()
                
                # FFmpeg
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                ffmpeg_cmd = [
                    "ffmpeg", "-y", "-framerate", str(fps),
                    "-i", os.path.join(render_dir, "frame_%04d.png"),
                    "-c:v", "h264_nvenc", "-pix_fmt", "yuv420p", "-preset", "fast", "-b:v", "2M",
                    output_path
                ]
                t_ffmpeg_start = time.time()
                try:
                    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except:
                    ffmpeg_cmd_sw = ["ffmpeg", "-y", "-framerate", str(fps), "-i", os.path.join(render_dir, "frame_%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", output_path]
                    subprocess.run(ffmpeg_cmd_sw, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                t_ffmpeg_end = time.time()
                
                # Thumb
                first_frame_src = os.path.join(render_dir, f"frame_{str(f_start).zfill(4)}.png")
                storyboard_out = output_path.replace(".mp4", "_thumb.png")
                if os.path.exists(first_frame_src):
                    shutil.copy(first_frame_src, storyboard_out)
                    
                shutil.rmtree(render_dir, ignore_errors=True)
                
                response = {
                    "status": "success",
                    "output_path": output_path,
                    "timings": {
                        "render_time": t_render_end - t_render_start,
                        "ffmpeg_time": t_ffmpeg_end - t_ffmpeg_start,
                        "total_time": time.time() - t_start
                    }
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                import traceback
                print("[BlenderDaemon] EXCEPTION IN HANDLER:")
                traceback.print_exc()
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "error": str(e)}).encode())

if __name__ == "__main__":
    init_blender_env()
    server = HTTPServer(('127.0.0.1', PORT), RenderHandler)
    print(f"[BlenderDaemon] Listening on port {PORT}...")
    server.serve_forever()
