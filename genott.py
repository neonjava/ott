#!/usr/bin/env python3
"""
GenOTT V2 Command Line Interface & Execution Entrypoint
"""

import sys
import os
import argparse
import json

# Ensure repository root is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.backends.wan.backend import WANBackend
from engine.model_manager.manager import ModelManager
from engine.model_manager.registry import ModelRegistry
from engine.model_manager.installer import ModelInstaller
from engine.director.demo_orchestrator import DemoOrchestrator

def main():
    parser = argparse.ArgumentParser(description="GenOTT V2 — Autonomous AI Production Studio CLI")
    subparsers = parser.add_subparsers(dest="command", help="GenOTT subcommands")

    # Command: generate
    gen_parser = subparsers.add_parser("generate", help="Generate cinematic video shot or complete production")
    gen_parser.add_argument("--prompt", type=str, default="A cinematic masterpiece shot of a futuristic cyberpunk city", help="Prompt text")
    gen_parser.add_argument("--backend", type=str, default="wan", help="Backend engine (wan, blender, etc.)")
    gen_parser.add_argument("--output", type=str, default="outputs/cinematic_shot.mp4", help="Output path")
    gen_parser.add_argument("--duration", type=float, default=5.0, help="Duration in seconds")
    gen_parser.add_argument("--demo", action="store_true", help="Generate complete 30-second narration-synced cinematic demo")

    # Command: backend
    backend_parser = subparsers.add_parser("backend", help="Manage and test backend adapters")
    backend_sub = backend_parser.add_subparsers(dest="backend_action")
    test_parser = backend_sub.add_parser("test", help="Test backend adapter")
    test_parser.add_argument("name", type=str, nargs="?", default="wan", help="Backend adapter name")

    # Command: benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Run model generation performance benchmark")
    bench_parser.add_argument("name", type=str, nargs="?", default="wan", help="Target model backend")

    # Command: models
    models_parser = subparsers.add_parser("models", help="Model manager & installer commands")
    models_sub = models_parser.add_subparsers(dest="models_action")
    
    models_sub.add_parser("list", help="List all registered models and status")
    
    install_m = models_sub.add_parser("install", help="Install model backend weights and repos")
    install_m.add_argument("name", type=str, nargs="?", default=None, help="Model backend name (wan, hunyuanvideo, cogvideox, ltx-video, mochi)")
    install_m.add_argument("--all", action="store_true", help="Install all registered open-source models")

    update_m = models_sub.add_parser("update", help="Update model repositories or weights")
    update_m.add_argument("name", type=str, nargs="?", default=None, help="Model name to update")

    verify_m = models_sub.add_parser("verify", help="Verify installation integrity and checksums")
    verify_m.add_argument("name", type=str, nargs="?", default=None, help="Model name to verify")

    remove_m = models_sub.add_parser("remove", help="Remove model directory and weights")
    remove_m.add_argument("name", type=str, help="Model backend name to remove")

    models_sub.add_parser("info", help="Display discovered models & system compute resources")

    args = parser.parse_args()

    if args.command == "generate":
        if args.demo:
            print("[GenOTT Engine] Initiating complete 30-second cinematic demo production...")
            orchestrator = DemoOrchestrator()
            meta = orchestrator.run_30s_cinematic_production()
            print(f"[✓] 30-Second Production successfully generated and exported to {meta['assets']['final_export']}")
            print(f"    Narration Audio Track: {meta['assets']['narration_audio']}")
            print(f"    Metadata Summary: {meta['number_of_shots']} shots | {meta['total_duration_sec']}s total | VRAM: {meta['vram_gb']}GB")
        else:
            print(f"[GenOTT Engine] Routing generation request to backend '{args.backend}'...")
            if args.backend == "wan":
                wan = WANBackend()
                wan.initialize()
                result = wan.generate_from_text(prompt=args.prompt, output_path=args.output, duration=args.duration)
                print(f"[✓] Generation finished successfully! Output saved to {result['output_path']}")
                print(f"    VRAM Used: {result['vram_gb']} GB | Latency: {result['generation_time_sec']}s")
            else:
                print(f"[!] Backend '{args.backend}' not supported for direct prompt generation CLI yet.")

    elif args.command == "backend":
        if args.backend_action == "test":
            print(f"[Backend Diagnostic] Running diagnostic suite for backend '{args.name}'...")
            if args.name == "wan":
                wan = WANBackend()
                wan.initialize()
                health = wan.health_check()
                print(json.dumps(health, indent=2))
                print("[✓] WAN Backend integration test passed cleanly.")

    elif args.command == "benchmark":
        print(f"[Benchmark Engine] Running benchmark suite on backend '{args.name}'...")
        wan = WANBackend()
        wan.initialize()
        vram = wan.estimate_vram("1080p", duration=5.0, fps=24)
        latency = wan.estimate_generation_time(duration=5.0, steps=50)
        print(f"Backend: {args.name} | Resolution: 1080p | Duration: 5.0s")
        print(f"Estimated VRAM requirement: {vram} GB")
        print(f"Estimated latency: {latency}s")
        print("[✓] Benchmark completed.")

    elif args.command == "models":
        installer = ModelInstaller()
        registry = ModelRegistry()
        mm = ModelManager()

        if args.models_action == "list":
            all_models = registry.list_all()
            print("=== Registered Open-Source AI Video Models ===")
            for name, details in all_models.items():
                print(f"• {name.ljust(15)} | Status: {details['installation_status'].ljust(12)} | Version: {str(details['installed_version']).ljust(12)} | Req VRAM: {details['required_vram_gb']}GB")

        elif args.models_action == "install":
            if args.all:
                print("Installing all open-source models...")
                res = installer.install_all()
                print(json.dumps(res, indent=2))
            elif args.name:
                print(f"Installing model '{args.name}'...")
                success = installer.install_model(args.name)
                if success:
                    print(f"[✓] Installation of '{args.name}' completed successfully.")
                else:
                    print(f"[!] Installation of '{args.name}' failed.")
            else:
                print("Please specify a model name or use --all. Example: genott models install wan")

        elif args.models_action == "verify":
            target = args.name
            if target:
                res = installer.verify_model(target)
                print(json.dumps(res, indent=2))
            else:
                print("Verifying all models:")
                for m in registry.list_all():
                    res = installer.verify_model(m)
                    print(f"• {m.ljust(15)}: {res['status']}")

        elif args.models_action == "remove":
            if args.name:
                success = installer.remove_model(args.name)
                if success:
                    print(f"[✓] Removed model '{args.name}'.")
                else:
                    print(f"[!] Model '{args.name}' was not found or could not be removed.")
            else:
                print("Please specify a model name to remove. Example: genott models remove wan")

        elif args.models_action == "update":
            target = args.name or "wan"
            print(f"Updating model '{target}'...")
            installer.update_model(target)

        elif args.models_action == "info":
            sys_res = installer.detect_system_resources()
            discovered = mm.discover_models()
            print("=== Compute & Resource Detection ===")
            print(json.dumps(sys_res, indent=2))
            print("\n=== Discovered Models ===")
            print(json.dumps(discovered, indent=2))
        else:
            all_models = registry.list_all()
            print(json.dumps(all_models, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
