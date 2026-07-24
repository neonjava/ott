# scripts/install_wan.py
import sys
import subprocess
import os

def check_and_install():
    print("=== GenOTT Python WAN Environment Validator ===")
    deps = {
        "torch": "PyTorch",
        "flash_attn": "Flash Attention (optional)",
        "xformers": "xFormers (optional)",
        "yaml": "PyYAML"
    }

    for module, name in deps.items():
        try:
            __import__(module)
            print(f"[✓] {name} is installed.")
        except ImportError:
            print(f"[!] {name} is not installed.")

    os.makedirs("third_party/wan", exist_ok=True)
    os.makedirs("models/wan", exist_ok=True)
    print("=== Target directories ready: third_party/wan, models/wan ===")

if __name__ == "__main__":
    check_and_install()
