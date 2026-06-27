import os

subfolders = [
    "ai/character",
    "ai/lipsync",
    "ai/renderer",
    "ai/storage",
    "ai/storyboard",
    "ai/voice",
]

for f in subfolders:
    os.makedirs(f, exist_ok=True)
    with open(os.path.join(f, "__init__.py"), "w") as init:
        init.write("# init\n")

# Re-exports mapping
exports = {
    "ai/character/library.py": "from engine.character.library import *\n",
    "ai/character/models.py": "from engine.character.models import *\n",
    "ai/lipsync/sadtalker.py": "from engine.character.lipsync.sadtalker import *\n",
    "ai/renderer/diffusers_ai.py": "from engine.renderer.diffusers_ai import *\n",
    "ai/renderer/blender.py": "from engine.renderer.blender import *\n",
    "ai/renderer/unreal.py": "from engine.renderer.unreal import *\n",
    "ai/storage/cache_manager.py": "from engine.cache.storage.cache_manager import *\n",
    "ai/storyboard/planner.py": "from pipeline.storyboard.planner import *\n",
    "ai/voice/generator.py": "from engine.audio.voice.generator import *\n",
}

for filepath, content in exports.items():
    with open(filepath, "w") as f:
        f.write(content)

print("Created all nested ai/ re-export wrappers in genott/.")
