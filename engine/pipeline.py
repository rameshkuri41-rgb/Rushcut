#!/usr/bin/env python3
"""
Rushcut engine — $0 pipeline.

    python3 pipeline.py "compound interest"

Topic in -> script -> voice -> visuals -> render -> finished mp4 out.
Every stage tries a free online service first (better quality) and
falls back to a fully offline free tool automatically if the network
isn't there — so this always finishes with a real video file, on any
machine, with no API keys and no spend required.
"""
import os
import sys
import time
import shutil

# lightweight .env loader — no extra dependency needed
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                if _v and _k not in os.environ:
                    os.environ[_k] = _v

from script_gen import generate_script
from voice import synthesize
from visuals import get_image
from assemble import build_scene_clip, concat_scenes, add_background_pad

BASE = os.path.dirname(os.path.abspath(__file__))


def run(topic: str, n_scenes: int = 6, out_name: str | None = None):
    run_id = out_name or f"{int(time.time())}"
    work = os.path.join(BASE, "output", run_id)
    scenes_dir = os.path.join(work, "scenes")
    captions_dir = os.path.join(work, "captions")
    os.makedirs(scenes_dir, exist_ok=True)
    os.makedirs(captions_dir, exist_ok=True)

    print(f"== Rushcut engine :: '{topic}' ==")

    print("[1/4] Script...")
    scenes = generate_script(topic, n_scenes)
    for s in scenes:
        print(f"   scene {s['id']}: {s['text'][:70]}...")

    scene_clips = []
    total_duration = 0.0
    for s in scenes:
        sid = s["id"]
        print(f"[2/4] Scene {sid}: voice + visual...")

        voice_path = os.path.join(scenes_dir, f"voice_{sid}.mp3")
        image_path = os.path.join(scenes_dir, f"image_{sid}.png")
        caption_path = os.path.join(captions_dir, f"caption_{sid}.txt")
        clip_path = os.path.join(scenes_dir, f"clip_{sid}.mp4")

        duration = synthesize(s["text"], voice_path)
        get_image(s["text"], topic, sid, len(scenes), image_path)

        print(f"[3/4] Scene {sid}: rendering ({duration:.1f}s)...")
        build_scene_clip(image_path, voice_path, s["text"], duration, caption_path, clip_path)

        scene_clips.append(clip_path)
        total_duration += duration

    print("[4/4] Concatenating + mixing background bed...")
    concat_list = os.path.join(work, "concat_list.txt")
    joined_path = os.path.join(work, "joined.mp4")
    final_path = os.path.join(work, "rushcut_final.mp4")

    concat_scenes(scene_clips, concat_list, joined_path)
    add_background_pad(joined_path, final_path, total_duration)

    print(f"\nDone. {len(scenes)} scenes, ~{total_duration:.1f}s, saved to:\n  {final_path}")
    return final_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python3 pipeline.py "your topic here" [n_scenes]')
        sys.exit(1)
    topic = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    run(topic, n)
