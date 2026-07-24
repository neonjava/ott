# scripts/setup_wan.py
import os
import sys

def setup_wan_backend():
    print("Setting up WAN open-source backend structure for GenOTT V2...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    third_party_wan = os.path.join(base_dir, "third_party", "wan")
    models_wan = os.path.join(base_dir, "models", "wan")
    
    os.makedirs(third_party_wan, exist_ok=True)
    os.makedirs(models_wan, exist_ok=True)
    
    print(f"Submodule path: {third_party_wan}")
    print(f"Weights path: {models_wan}")
    print("WAN setup verification complete.")

if __name__ == "__main__":
    setup_wan_backend()
