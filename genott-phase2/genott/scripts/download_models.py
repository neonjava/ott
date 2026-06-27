import os
import torch
from diffusers import AnimateDiffPipeline, MotionAdapter

print("=========================================")
print("Pre-downloading AnimateDiff Models...")
print("=========================================")

try:
    print("\n1/2: Downloading Motion Adapter...")
    adapter = MotionAdapter.from_pretrained(
        "guoyww/animatediff-motion-adapter-v1-5-2",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )
    
    print("\n2/2: Downloading AnimateDiff Base Model (epiCRealism)...")
    pipe = AnimateDiffPipeline.from_pretrained(
        "emilianJR/epiCRealism",
        motion_adapter=adapter,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )
    
    print("\n=========================================")
    print("✓ Success! All models downloaded and cached.")
    print("=========================================")
except Exception as e:
    print(f"\n[Error] Download failed: {e}")
    print("You can run this script again to resume downloading.")
