"""
pipeline_long.py — 5s to 2.5h pipeline

Supports:
- 1 scene = 5s short
- 150 scenes = 2.5h sleeping history

Modes:
- short: 5-60s
- standard: 1-15 min (channel.farm)
- sleep: 30min-2.5h (boring history for sleep)
- ultra: 2.5h max

Run:
  python pipeline_long.py "history of bread" --mode sleep --n 60 --out sleep_bread_1h

Env:
  GROQ_API_KEY optional
  R2 vars for upload (handled in server)
"""
import argparse
import os
import sys
import time
from pathlib import Path

from script_gen_long import generate_script_long, calculate_duration
from voice_long import synthesize_long
from visuals import get_image
from assemble_long import build_scene_clip_long, concat_scenes_batched, add_background_pad_long

BASE = Path(__file__).parent

def run_long(topic: str, n_scenes: int = 10, mode: str = "standard", out_name: str = None, progress_cb=None):
    """
    progress_cb: function(msg: str, data: dict)
    """
    if out_name is None:
        out_name = f"rushcut_{int(time.time())}"
    
    work = BASE / "output" / out_name
    scenes_dir = work / "scenes"
    captions_dir = work / "captions"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    captions_dir.mkdir(parents=True, exist_ok=True)
    
    def log(msg, data=None):
        print(msg)
        if progress_cb:
            progress_cb(msg, data or {})
    
    log(f"== Rushcut LONG :: '{topic}' mode={mode} n={n_scenes} ==")
    est = calculate_duration(n_scenes, mode)
    log(f"[est] {est/60:.1f} min, {est:.0f}s total")
    
    log(f"[1/4] Script... {mode}")
    scenes = generate_script_long(topic, n_scenes, mode)
    log(f"   {len(scenes)} scenes generated")
    
    scene_clips = []
    total_duration = 0.0
    
    for s in scenes:
        sid = s["id"]
        log(f"[2/4] Scene {sid}/{len(scenes)}: voice + visual...", {"scene": sid, "total": len(scenes)})
        
        voice_path = str(scenes_dir / f"voice_{sid}.mp3")
        image_path = str(scenes_dir / f"image_{sid}.png")
        caption_path = str(captions_dir / f"caption_{sid}.txt")
        clip_path = str(scenes_dir / f"clip_{sid}.mp4")
        
        # voice
        duration = synthesize_long(s["text"], voice_path, mode)
        log(f"   voice {duration:.1f}s ({mode})")
        
        # visual (reuse same image every 3 scenes for sleep to save time/API calls)
        if mode == "sleep" and sid % 3 == 0:
            # reuse previous image
            prev_img = str(scenes_dir / f"image_{sid-1}.png")
            if Path(prev_img).exists():
                import shutil
                shutil.copy(prev_img, image_path)
            else:
                get_image(s["text"], topic, sid, len(scenes), image_path)
        else:
            get_image(s["text"], topic, sid, len(scenes), image_path)
        
        log(f"   visual → {Path(image_path).name}")
        
        # render
        log(f"[3/4] Scene {sid}: rendering ({duration:.1f}s)... mode={mode}")
        build_scene_clip_long(image_path, voice_path, s["text"], duration, caption_path, clip_path, mode)
        scene_clips.append(clip_path)
        total_duration += duration
        log(f"   clip done, total {total_duration/60:.1f} min", {"scene": sid, "total": len(scenes), "duration": total_duration})
    
    log(f"[4/4] Concatenating {len(scene_clips)} clips → {total_duration/60:.1f} min total, batched...")
    joined_path = str(work / "joined.mp4")
    concat_scenes_batched(scene_clips, str(work), joined_path, batch_size=20)
    
    final_path = str(work / "rushcut_final.mp4")
    log(f"   Adding background pad ({mode})...")
    add_background_pad_long(joined_path, final_path, total_duration, mode)
    
    log(f"Done. {len(scenes)} scenes, {total_duration/60:.1f} min ({total_duration:.0f}s), saved to {final_path}")
    
    # cleanup intermediate? keep for debugging but remove joined
    try:
        Path(joined_path).unlink(missing_ok=True)
    except:
        pass
    
    return final_path, total_duration

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rushcut long-form pipeline 5s-2.5h")
    parser.add_argument("topic", help="Topic")
    parser.add_argument("--n", type=int, default=10, help="Number of scenes 1-200")
    parser.add_argument("--mode", default="standard", choices=["short","standard","sleep","ultra"], help="Mode")
    parser.add_argument("--out", default=None, help="Output folder name")
    args = parser.parse_args()
    
    # validate n for 2.5h max
    if args.mode in ("sleep","ultra") and args.n > 200:
        print("Max 200 scenes for sleep/ultra (2.5h)")
        args.n = 200
    if args.mode == "short" and args.n > 10:
        args.n = 10
    
    final, dur = run_long(args.topic, args.n, args.mode, args.out)
    print(f"\nFinal: {final} {dur/60:.1f} min")
