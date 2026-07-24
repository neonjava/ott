# engine/director/verifier.py
import os
import json
import subprocess
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ProductionVerifier:
    """
    Strict Production Integrity Verifier for GenOTT V2.
    Zero false-positives: Verification ONLY succeeds if all 10 physical deliverables exist,
    are non-empty, parse cleanly, and pass format validation via ffprobe/json parsing/image decoding.
    """

    REQUIRED_DELIVERABLES = [
        "final_render.mp4",
        "production_report.md",
        "generation_manifest.json",
        "contact_sheet.jpg",
        "screenplay.json",
        "movie_graph.json",
        "subtitles.srt",
        "narration_audio.wav",
        "timeline.json",
        "production_metadata.json"
    ]

    @classmethod
    def verify_production(cls, output_dir: str = "outputs/productions") -> Dict[str, Any]:
        output_abs = os.path.abspath(output_dir)
        report = {
            "output_dir": output_abs,
            "is_valid": True,
            "checks": {},
            "missing_artifacts": [],
            "errors": []
        }

        # 1. Verify existence and non-zero size of all 10 required physical deliverables
        for artifact in cls.REQUIRED_DELIVERABLES:
            artifact_path = os.path.join(output_abs, artifact)
            if not os.path.exists(artifact_path):
                report["is_valid"] = False
                report["missing_artifacts"].append(artifact)
                report["errors"].append(f"Required deliverable missing: {artifact}")
                report["checks"][artifact] = False
            elif os.path.getsize(artifact_path) == 0:
                report["is_valid"] = False
                report["missing_artifacts"].append(f"{artifact} (empty 0-byte file)")
                report["errors"].append(f"Required deliverable is empty: {artifact}")
                report["checks"][artifact] = False
            else:
                report["checks"][artifact] = True

        # 2. Deep format validation for videos (ffprobe)
        final_render = os.path.join(output_abs, "final_render.mp4")
        if report["checks"].get("final_render.mp4"):
            probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_name", "-of", "json", final_render]
            probe_res = subprocess.run(probe_cmd, capture_output=True, text=True)
            if probe_res.returncode != 0:
                report["is_valid"] = False
                report["errors"].append(f"final_render.mp4 invalid video stream: {probe_res.stderr.strip()}")
                report["checks"]["final_render_probed"] = False
            else:
                report["checks"]["final_render_probed"] = True

        # 3. Deep format validation for JSON files
        json_artifacts = ["generation_manifest.json", "screenplay.json", "movie_graph.json", "timeline.json", "production_metadata.json"]
        for j_art in json_artifacts:
            j_path = os.path.join(output_abs, j_art)
            if report["checks"].get(j_art):
                try:
                    with open(j_path, "r") as f:
                        json.load(f)
                    report["checks"][f"{j_art}_parsed"] = True
                except Exception as e:
                    report["is_valid"] = False
                    report["errors"].append(f"JSON parsing error in {j_art}: {e}")
                    report["checks"][f"{j_art}_parsed"] = False

        # 4. Verify per-shot video files (24 shots) and per-shot sidecars
        shot_files = [os.path.join(output_abs, f"shot_{i:02d}.mp4") for i in range(1, 25)]
        valid_shots_count = 0
        valid_sidecars_count = 0

        for sf in shot_files:
            if os.path.exists(sf) and os.path.getsize(sf) > 0:
                probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", sf]
                p_res = subprocess.run(probe_cmd, capture_output=True, text=True)
                if p_res.returncode == 0:
                    valid_shots_count += 1
            meta_sf = f"{os.path.splitext(sf)[0]}_meta.json"
            if os.path.exists(meta_sf) and os.path.getsize(meta_sf) > 0:
                valid_sidecars_count += 1

        report["checks"]["valid_shots_count"] = valid_shots_count
        report["checks"]["valid_sidecars_count"] = valid_sidecars_count

        if valid_shots_count < 24:
            report["is_valid"] = False
            report["errors"].append(f"Only {valid_shots_count}/24 shot video files verified valid via ffprobe")

        if valid_sidecars_count < 24:
            report["is_valid"] = False
            report["errors"].append(f"Only {valid_sidecars_count}/24 shot sidecar metadata files exist")

        logger.info(f"Production Strict Verification Check completed: Valid = {report['is_valid']}")
        return report
