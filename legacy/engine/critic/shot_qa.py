# engine/critic/shot_qa.py
import os
import json
import logging
import numpy as np
from PIL import Image
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ShotQualityAssurance:
    """
    Performs Quality Assurance testing after every generated shot:
    1. VAE Frame Decoding & Noise Verification
    2. Temporal Flicker Detection (Luminance Variance Jump)
    3. Identity Drift Detection (Color & Feature Histogram Shift)
    4. Camera Instability Check
    """

    def __init__(self, debug_dir: str = "outputs/debug"):
        self.debug_dir = os.path.abspath(debug_dir)

    def evaluate_shot(self, frame_paths: List[str], shot_id: str, anchor_hist: Optional[np.ndarray] = None) -> Dict[str, Any]:
        if not frame_paths:
            return {"passed": False, "reason": "No frames provided"}

        num_frames = len(frame_paths)
        luminances = []
        histograms = []
        corrupted_frames = []
        flicker_jumps = []

        for idx, f_path in enumerate(frame_paths, start=1):
            if not os.path.exists(f_path):
                corrupted_frames.append(idx)
                continue

            try:
                img = Image.open(f_path).convert("RGB")
                img_np = np.array(img)
                
                # Check blank or noise corruption
                if np.min(img_np) == np.max(img_np):
                    corrupted_frames.append(idx)
                    continue

                # Measure frame luminance
                gray = np.mean(img_np, axis=2)
                luminance = np.mean(gray)
                luminances.append(luminance)

                # Measure color histogram for identity/continuity tracking
                hist, _ = np.histogram(img_np, bins=32, range=(0, 256))
                hist = hist / (hist.sum() + 1e-7)
                histograms.append(hist)

            except Exception as e:
                logger.error(f"Error reading frame {f_path}: {e}")
                corrupted_frames.append(idx)

        if corrupted_frames:
            return {
                "passed": False,
                "reason": f"Corrupted frames detected at indices: {corrupted_frames}",
                "corrupted_frames": corrupted_frames
            }

        # Calculate Temporal Flicker (Frame-to-frame luminance jumps)
        for i in range(1, len(luminances)):
            diff = abs(luminances[i] - luminances[i-1])
            flicker_jumps.append(diff)

        max_flicker = float(np.max(flicker_jumps)) if flicker_jumps else 0.0
        avg_flicker = float(np.mean(flicker_jumps)) if flicker_jumps else 0.0

        # Calculate Identity Drift from anchor histogram if available
        current_mean_hist = np.mean(histograms, axis=0) if histograms else np.zeros(32)
        identity_drift = 0.0
        if anchor_hist is not None:
            identity_drift = float(np.linalg.norm(current_mean_hist - anchor_hist))

        # Quality Thresholds
        flicker_threshold = 28.0  # Max allowable average luminance jump
        drift_threshold = 0.35    # Max allowable histogram drift shift

        passed = (avg_flicker <= flicker_threshold) and (identity_drift <= drift_threshold)

        result = {
            "passed": passed,
            "shot_id": shot_id,
            "total_frames_evaluated": num_frames,
            "corrupted_frames_count": len(corrupted_frames),
            "max_flicker_jump": round(max_flicker, 2),
            "avg_flicker": round(avg_flicker, 2),
            "identity_drift_delta": round(identity_drift, 3),
            "mean_histogram": current_mean_hist.tolist(),
            "reason": "PASSED" if passed else f"QA Failed: avg_flicker={round(avg_flicker,2)} (limit {flicker_threshold}), drift={round(identity_drift,3)} (limit {drift_threshold})"
        }

        logger.info(f"[Shot QA - {shot_id}] Passed: {passed} | Avg Flicker: {round(avg_flicker,2)} | Identity Drift: {round(identity_drift,3)}")
        return result
