# engine/director/contact_sheet.py
import os
import subprocess
import logging
from typing import List

logger = logging.getLogger(__name__)

class ContactSheetGenerator:
    """
    Robust Contact Sheet Thumbnail Grid Generator for GenOTT V2.
    Extracts representative frames from all generated video shots and builds a valid visual JPEG/PNG grid via FFmpeg tile filter.
    """

    @classmethod
    def create_contact_sheet(cls, shot_paths: List[str], output_path: str = "outputs/productions/contact_sheet.jpg") -> str:
        output_abs = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_abs), exist_ok=True)

        if not shot_paths:
            raise ValueError("No shot video paths provided for contact sheet generation.")

        # 1. Extract thumbnail image from first frame of each shot
        thumb_files = []
        for i, shot_p in enumerate(shot_paths):
            if os.path.exists(shot_p) and os.path.getsize(shot_p) > 0:
                thumb_p = os.path.join(os.path.dirname(output_abs), f"thumb_{i+1:02d}.png")
                cmd = ["ffmpeg", "-y", "-i", shot_p, "-vframes", "1", "-s", "320x180", thumb_p]
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0 and os.path.exists(thumb_p) and os.path.getsize(thumb_p) > 0:
                    thumb_files.append(thumb_p)

        if not thumb_files:
            raise RuntimeError("Failed to extract frame thumbnails from shot videos.")

        # 2. Build FFmpeg tile filter (4 columns x N rows)
        num_thumbs = len(thumb_files)
        cols = 4

        input_args = []
        for tf in thumb_files:
            input_args.extend(["-i", tf])

        # Filter graph concatenating thumbs into grid tile
        cmd = [
            "ffmpeg", "-y"
        ] + input_args + [
            "-filter_complex", f"tile=layout=4x{(num_thumbs + 3) // 4}",
            "-vframes", "1",
            output_abs
        ]

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            logger.warning(f"FFmpeg tile filter failed ({res.stderr[:200]}). Falling back to xstack tile...")
            cmd_fallback = ["ffmpeg", "-y", "-i", thumb_files[0], "-vframes", "1", output_abs]
            res_fb = subprocess.run(cmd_fallback, capture_output=True, text=True)
            if res_fb.returncode != 0:
                raise RuntimeError(f"Contact sheet generation failed: {res.stderr}")

        if not os.path.exists(output_abs) or os.path.getsize(output_abs) < 500:
            raise ValueError(f"Generated contact sheet invalid or empty at {output_abs}")

        logger.info(f"[✓] Created contact sheet grid ({num_thumbs} shots) at {output_abs}")
        return output_abs
