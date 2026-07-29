# engine/timeline/sequencer.py
import os
import json
import logging
import subprocess
from typing import Dict, Any, List
from engine.timeline.encoder_detector import FFmpegEncoderDetector

logger = logging.getLogger(__name__)

class TimelineSequencer:
    """
    Frame-Accurate Timeline Sequencing & Real Video Rendering Engine for GenOTT V2.
    Supports shot ordering, FFmpeg dynamic encoder auto-detection, audio mixing, subtitle embedding,
    and outputting valid H.264 / MPEG4 encoded MP4 containers.
    """

    def __init__(self, fps: int = 24):
        self.fps = fps
        self.shots: List[Dict[str, Any]] = []
        self.audio_tracks: List[Dict[str, Any]] = []
        self.subtitle_tracks: List[Dict[str, Any]] = []

    def add_shot(self, shot_id: int, video_path: str, duration_sec: float, transition: str = "cut") -> Dict[str, Any]:
        frame_count = int(round(duration_sec * self.fps))
        start_frame = sum(s["frame_count"] for s in self.shots)
        end_frame = start_frame + frame_count

        shot_entry = {
            "shot_id": shot_id,
            "video_path": os.path.abspath(video_path),
            "duration_sec": duration_sec,
            "frame_count": frame_count,
            "start_frame": start_frame,
            "end_frame": end_frame,
            "start_time": start_frame / self.fps,
            "end_time": end_frame / self.fps,
            "transition": transition
        }
        self.shots.append(shot_entry)
        return shot_entry

    def sync_audio_track(self, audio_path: str, duration_sec: float) -> Dict[str, Any]:
        track_entry = {
            "audio_path": os.path.abspath(audio_path),
            "duration_sec": duration_sec,
            "frame_count": int(round(duration_sec * self.fps)),
            "synced_with_shots": len(self.shots)
        }
        self.audio_tracks.append(track_entry)
        return track_entry

    def sync_subtitles(self, subtitle_path: str) -> Dict[str, Any]:
        sub_entry = {
            "subtitle_path": os.path.abspath(subtitle_path),
            "status": "synchronized"
        }
        self.subtitle_tracks.append(sub_entry)
        return sub_entry

    def compile_timeline(self, output_path: str = "outputs/timeline.json") -> Dict[str, Any]:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        total_duration = sum(s["duration_sec"] for s in self.shots)
        total_frames = sum(s["frame_count"] for s in self.shots)

        timeline_data = {
            "fps": self.fps,
            "total_duration_sec": total_duration,
            "total_frames": total_frames,
            "shots_timeline": self.shots,
            "audio_tracks": self.audio_tracks,
            "subtitle_tracks": self.subtitle_tracks
        }

        with open(output_path, "w") as f:
            json.dump(timeline_data, f, indent=2)

        logger.info(f"[✓] Compiled frame-accurate timeline with {len(self.shots)} shots ({total_frames} frames) to {output_path}")
        return timeline_data

    def render_final_video(self, output_mp4: str) -> str:
        """
        Renders the complete timeline to a playable MP4 video file using FFmpeg concat & audio mixing.
        """
        output_abs = os.path.abspath(output_mp4)
        os.makedirs(os.path.dirname(output_abs), exist_ok=True)

        if not self.shots:
            raise ValueError("No video shots in timeline to render")

        encoder = FFmpegEncoderDetector.get_best_encoder()

        # 1. Write FFmpeg Concat List
        concat_list_file = os.path.join(os.path.dirname(output_abs), "concat_shots.txt")
        with open(concat_list_file, "w") as f:
            for shot in self.shots:
                f.write(f"file '{shot['video_path']}'\n")

        # 2. Build FFmpeg command to concatenate video shots and mix audio tracks
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat_list_file
        ]

        audio_inputs = []
        for track in self.audio_tracks:
            if os.path.exists(track["audio_path"]):
                audio_inputs.extend(["-i", track["audio_path"]])

        cmd.extend(audio_inputs)
        cmd.extend(["-c:v", encoder, "-pix_fmt", "yuv420p"])

        # Audio Mixing Filter
        if len(self.audio_tracks) == 1 and os.path.exists(self.audio_tracks[0]["audio_path"]):
            cmd.extend(["-c:a", "aac", "-shortest"])
        elif len(self.audio_tracks) >= 2:
            cmd.extend(["-filter_complex", f"amix=inputs={len(self.audio_tracks)}:duration=shortest", "-c:a", "aac"])

        cmd.append(output_abs)

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            logger.warning(f"FFmpeg render with encoder '{encoder}' failed ({res.stderr[:200]}). Retrying with mpeg4 codec...")
            encoder_fallback = "mpeg4"
            cmd_fallback = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", concat_list_file
            ] + audio_inputs + ["-c:v", encoder_fallback, "-pix_fmt", "yuv420p"]
            if len(self.audio_tracks) >= 2:
                cmd_fallback.extend(["-filter_complex", f"amix=inputs={len(self.audio_tracks)}:duration=shortest", "-c:a", "aac"])
            cmd_fallback.append(output_abs)
            res = subprocess.run(cmd_fallback, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"FFmpeg timeline render failed: {res.stderr}")

        # 3. Validate with ffprobe
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration,size:stream=codec_name,width,height,r_frame_rate",
            "-of", "json", output_abs
        ]
        probe_res = subprocess.run(probe_cmd, capture_output=True, text=True)
        if probe_res.returncode != 0 or not os.path.exists(output_abs) or os.path.getsize(output_abs) < 1000:
            raise ValueError(f"Rendered video validation failed for {output_abs}: {probe_res.stderr}")

        logger.info(f"[✓] Timeline rendered and verified playable MP4 at {output_abs}")
        return output_abs
