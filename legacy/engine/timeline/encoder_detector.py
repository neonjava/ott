# engine/timeline/encoder_detector.py
import subprocess
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class FFmpegEncoderDetector:
    """
    Dynamic FFmpeg Video Encoder Auto-Detector for GenOTT V2.
    Queries FFmpeg at runtime to find and select the highest priority available video encoder.
    """

    PRIORITY_LIST: List[str] = [
        "libx264",
        "h264_nvenc",
        "h264_vaapi",
        "h264_qsv",
        "libopenh264",
        "mpeg4"
    ]

    _cached_encoder: Optional[str] = None

    @classmethod
    def get_best_encoder(cls) -> str:
        if cls._cached_encoder is not None:
            return cls._cached_encoder

        cmd = ["ffmpeg", "-codecs"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        codecs_out = res.stdout if res.returncode == 0 else ""

        available_encoders = []
        for encoder in cls.PRIORITY_LIST:
            if encoder in codecs_out:
                # Test encoder viability via short lavfi dry run
                test_cmd = [
                    "ffmpeg", "-y",
                    "-f", "lavfi", "-i", "nullsrc=s=64x64:d=0.1",
                    "-c:v", encoder,
                    "-f", "null", "-"
                ]
                test_res = subprocess.run(test_cmd, capture_output=True, text=True)
                if test_res.returncode == 0:
                    available_encoders.append(encoder)

        if available_encoders:
            cls._cached_encoder = available_encoders[0]
        else:
            cls._cached_encoder = "mpeg4"

        logger.info(f"[FFmpegEncoderDetector] Auto-detected best video encoder: '{cls._cached_encoder}'")
        return cls._cached_encoder
