# engine/director/contact_sheet.py
import os
import subprocess
import logging
from typing import List

logger = logging.getLogger(__name__)

class ContactSheetGenerator:
    """
    Contact Sheet Thumbnail Grid Generator for GenOTT V2.
    Extracts representative frames from all generated video shots and builds a grid via FFmpeg.
    """

    @classmethod
    def create_contact_sheet(cls, shot_paths: List[str], output_path: str = "outputs/productions/contact_sheet.jpg") -> str:
        output_abs = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_abs), exist_ok=True)

        if not shot_paths:
            logger.warning("No shot video paths provided for contact sheet generation.")
            return output_abs

        # 1. Extract thumbnail image from first frame of each shot
        thumb_files = []
        for i, shot_p in enumerate(shot_paths):
            if os.path.exists(shot_p):
                thumb_p = os.path.join(os.path.dirname(output_abs), f"thumb_{i+1:02d}.png")
                cmd = ["ffmpeg", "-y", "-i", shot_p, "-vframes", "1", "-s", "320x180", thumb_p]
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0 and os.path.exists(thumb_p):
                    thumb_files.append(thumb_p)

        if not thumb_files:
            logger.warning("Failed to extract thumbnail images for contact sheet.")
            return output_abs

        # 2. Build FFmpeg tile filter layout (4 columns x N rows)
        num_thumbs = len(thumb_files)
        cols = 4
        rows = (num_thumbs + cols - 1) // cols

        input_args = []
        for tf in thumb_files:
            input_args.extend(["-i", tf])

        filter_complex = f"nullsrc=size=1280x{rows * 180} [bg]; "
        filter_complex += "".join([f"[{i}:v] setpts=PTS-STARTPTS [v{i}]; " for i in range(num_thumbs)])
        filter_complex += f"xstack=inputs={num_thumbs}:layout="
        
        layout_parts = []
        for i in range(num_thumbs):
            c = i % cols
            r = i // cols
            layout_parts.append(f"{c*320}_{r*180}")
        filter_complex += "|".join(layout_parts) + " [out]"

        cmd = ["ffmpeg", "-y"] + input_args + ["-filter_complex", filter_complex, "-map", "[out]", "-vframes", "1", output_abs]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            logger.warning(f"FFmpeg contact sheet xstack failed ({res.stderr[:200]}). Falling back to simple frame copy...")
            if thumb_files:
                cmd_fallback = ["ffmpeg", "-y", "-i", thumb_files[0], "-vframes", "1", output_abs]
                subprocess.run(cmd_fallback, capture_output=True, text=True)

        logger.info(f"[✓] Created contact sheet grid ({num_thumbs} shots) at {output_abs}")
        return output_abs
