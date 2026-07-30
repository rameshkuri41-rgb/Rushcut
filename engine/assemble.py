"""
Rushcut — assembly. 100% ffmpeg, 100% offline, 100% free — this stage
has no online/offline split because ffmpeg itself is the whole tool
and it never needs the network.
"""
import os
import subprocess
import textwrap

W, H = 1280, 720
FPS = 25


def _write_caption_file(text: str, path: str):
    wrapped = textwrap.fill(text, width=42)
    with open(path, "w") as f:
        f.write(wrapped)


def build_scene_clip(image_path: str, voice_path: str, caption_text: str,
                      duration: float, caption_path: str, out_path: str):
    _write_caption_file(caption_text, caption_path)
    zoom_frames = max(int(duration * FPS), 1)

    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},"
        f"zoompan=z='min(zoom+0.0006,1.12)':d={zoom_frames}:s={W}x{H}:fps={FPS},"
        f"drawtext=textfile='{caption_path}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        f"fontsize=34:fontcolor=white:line_spacing=6:borderw=3:bordercolor=black@0.85:"
        f"x=(w-text_w)/2:y=h-190"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", voice_path,
        "-filter_complex", f"[0:v]{vf}[v]",
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest", "-t", f"{duration:.2f}",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def concat_scenes(scene_paths: list[str], list_file: str, out_path: str):
    with open(list_file, "w") as f:
        for p in scene_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
         "-c", "copy", out_path],
        check=True, capture_output=True,
    )


def add_background_pad(video_path: str, out_path: str, duration: float):
    """Low, unobtrusive generated pad tone mixed under the voice — a
    real (if minimal) music bed with zero licensing risk and zero cost."""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-f", "lavfi", "-i",
        f"sine=frequency=110:duration={duration:.2f},volume=0.05",
        "-filter_complex", "[1:a]afade=t=out:st={:.2f}:d=2[bg];[0:a][bg]amix=inputs=2:duration=first[aout]".format(max(duration - 2, 0)),
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
