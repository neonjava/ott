#!/usr/bin/env python3
"""
GenOTT V2 Command Line Interface & Production Studio Entrypoint
"""

import sys
import os
import argparse
import json
import time

# Ensure repository root is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.backends.wan.backend import WANBackend
from engine.backends.plugin_framework import BackendRegistry
from engine.model_manager.manager import ModelManager
from engine.model_manager.registry import ModelRegistry
from engine.model_manager.installer import ModelInstaller
from engine.director.demo_orchestrator import DemoOrchestrator
from engine.director.production_pipeline import RealProductionPipeline
from engine.director.short_film_pipeline import ShortFilmPipeline
from engine.metrics.collector import MetricsCollector

def main():
    parser = argparse.ArgumentParser(description="GenOTT V2 — Autonomous AI Production Studio CLI")
    subparsers = parser.add_subparsers(dest="command", help="GenOTT subcommands")

    # Command: create
    create_parser = subparsers.add_parser("create", help="Create new AI movie production project")
    create_parser.add_argument("--name", type=str, default="New Production", help="Project name")
    create_parser.add_argument("--prompt", type=str, default="A cyberpunk odyssey through neon rain", help="Idea prompt")

    # Command: generate
    gen_parser = subparsers.add_parser("generate", help="Generate cinematic video shot or complete production")
    gen_parser.add_argument("--prompt", type=str, default="A cinematic masterpiece shot of a futuristic cyberpunk city", help="Prompt text")
    gen_parser.add_argument("--backend", type=str, default="wan", help="Backend engine (wan, cogvideox, hunyuanvideo, etc.)")
    gen_parser.add_argument("--output", type=str, default="outputs/cinematic_shot.mp4", help="Output path")
    gen_parser.add_argument("--duration", type=float, default=5.0, help="Duration in seconds")
    gen_parser.add_argument("--demo", action="store_true", help="Generate complete 30-second narration-synced cinematic demo")

    # Command: render / film
    render_parser = subparsers.add_parser("render", help="Render complete 2-minute short film or production from idea prompt")
    render_parser.add_argument("--idea", type=str, default="An epic sci-fi starship voyage across the galaxy", help="Idea prompt")
    render_parser.add_argument("--backend", type=str, default="wan", help="Backend plugin name")
    render_parser.add_argument("--duration", type=float, default=120.0, help="Production duration in seconds (default: 120s / 2min)")
    render_parser.add_argument("--output-dir", type=str, default="outputs/productions", help="Output directory")

    # Command: benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Run model generation performance benchmark")
    bench_parser.add_argument("name", type=str, nargs="?", default="wan", help="Target model backend")

    # Command: doctor
    doctor_parser = subparsers.add_parser("doctor", help="Run diagnostic health check on environment, PyTorch, CUDA, VRAM")

    # Command: demo
    demo_parser = subparsers.add_parser("demo", help="Generate complete 2-minute local AI short film demonstration")

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

    if args.command == "create":
        project_dir = f"movie_projects/{args.name.lower().replace(' ', '_')}"
        os.makedirs(project_dir, exist_ok=True)
        spec = {"name": args.name, "idea_prompt": args.prompt, "created_at": time.time()}
        with open(os.path.join(project_dir, "project.json"), "w") as f:
            json.dump(spec, f, indent=2)
        print(f"[✓] Project '{args.name}' created at {project_dir}")

    elif args.command == "generate":
        if args.demo:
            print("[GenOTT Engine] Initiating complete 30-second cinematic demo production...")
            orchestrator = DemoOrchestrator()
            meta = orchestrator.run_30s_cinematic_production()
            print(f"[✓] 30-Second Production successfully generated and exported to {meta['assets']['final_export']}")
        else:
            print(f"[GenOTT Engine] Routing generation request to backend '{args.backend}'...")
            backend = BackendRegistry.get_backend(args.backend)
            backend.initialize()
            result = backend.generate_text_to_video(prompt=args.prompt, output_path=args.output, duration=args.duration)
            print(f"[✓] Generation finished successfully! Output saved to {result['output_path']}")

    elif args.command == "render" or args.command == "demo":
        idea = getattr(args, "idea", "An epic sci-fi starship voyage across the galaxy")
        output_dir = getattr(args, "output_dir", "outputs/productions")
        backend_name = getattr(args, "backend", "wan")
        
        print(f"[GenOTT Autonomous Studio] Executing 2-Minute AI Short Film Pipeline ({backend_name})...")
        pipeline = ShortFilmPipeline(backend_name=backend_name, output_dir=output_dir)
        metadata = pipeline.produce_2min_short_film(idea_prompt=idea)
        print(f"[✓] 2-Minute AI Short Film Production Complete! Final Export: {metadata['exported_assets']['final_render']}")
        print(f"    Narration Audio Track: {metadata['exported_assets']['narration_audio']}")
        print(f"    Background Music Score: {metadata['exported_assets']['background_music']}")
        print(f"    Total Duration: {metadata['total_duration_sec']}s ({metadata['total_shots']} shots across 6 acts)")

    elif args.command == "doctor":
        installer = ModelInstaller()
        sys_res = installer.detect_system_resources()
        hw = MetricsCollector.get_hardware_info()
        print("=== GenOTT System Diagnostic ===")
        print(json.dumps({**sys_res, **hw}, indent=2))
        print("[✓] Diagnostic check finished.")

    elif args.command == "benchmark":
        name = args.name or "wan"
        backend = BackendRegistry.get_backend(name)
        backend.initialize()
        resources = backend.estimate_resources("1080p", duration=5.0, fps=24)
        print(f"=== Backend Benchmark ({name}) ===")
        print(json.dumps(resources, indent=2))

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
                print("Please specify a model name or use --all. Example: genott models install wan")

        elif args.models_action == "verify":
            target = args.name
            if target:
                res = installer.verify_model(target)
                print(json.dumps(res, indent=2))
            else:
                for m in registry.list_all():
                    res = installer.verify_model(m)
                    print(f"• {m.ljust(15)}: {res['status']}")

        elif args.models_action == "remove":
            if args.name:
                installer.remove_model(args.name)
                print(f"[✓] Removed model '{args.name}'.")

        elif args.models_action == "update":
            target = args.name or "wan"
            installer.update_model(target)

        elif args.models_action == "info":
            sys_res = installer.detect_system_resources()
            discovered = mm.discover_models()
            print(json.dumps({"system": sys_res, "models": discovered}, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
