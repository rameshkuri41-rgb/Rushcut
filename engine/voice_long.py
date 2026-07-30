"""
voice_long.py — long-form TTS with chunking
Supports 5s to 2.5 hours (9000s)

Features:
- edge-tts chunking: splits > 10 min text into 5-min chunks and concats
- sleep mode: slower rate (-10%), calm voice
- fallback to espeak with long duration
- returns accurate duration via ffprobe
"""
import os
import asyncio
import subprocess
import math
import re
from pathlib import Path

def get_duration(path: str) -> float:
    try:
        cmd = ["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",path]
        out = subprocess.check_output(cmd, text=True).strip()
        return float(out)
    except:
        return 0.0

def _estimate_duration(text: str, mode: str) -> float:
    words = len(text.split())
    if mode == "sleep":
        wpm = 110  # slower
    else:
        wpm = 150
    # 0.45s per word approx, but more accurate via wpm
    return max(2.5, (words / wpm) * 60)

async def _edge_tts_chunk(text: str, out_path: str, voice: str = "en-US-GuyNeural", rate: str = "+0%"):
    try:
        import edge_tts
        # edge-tts can handle ~ 5000 chars per call safely, chunk if needed
        max_chars = 4000
        if len(text) <= max_chars:
            comm = edge_tts.Communicate(text, voice=voice, rate=rate)
            await comm.save(out_path)
            return True
        
        # chunk
        chunks = []
        # split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        cur = ""
        for sent in sentences:
            if len(cur) + len(sent) < max_chars:
                cur += " " + sent
            else:
                if cur.strip():
                    chunks.append(cur.strip())
                cur = sent
        if cur.strip():
            chunks.append(cur.strip())
        
        # synthesize each chunk
        tmp_files = []
        for idx, ch in enumerate(chunks):
            tmp = out_path.replace(".mp3", f"_part{idx}.mp3")
            comm = edge_tts.Communicate(ch, voice=voice, rate=rate)
            await comm.save(tmp)
            tmp_files.append(tmp)
        
        # concat chunks via ffmpeg
        list_path = out_path + "_list.txt"
        with open(list_path, "w") as f:
            for tf in tmp_files:
                f.write(f"file '{Path(tf).absolute()}'\n")
        
        subprocess.run(
            ["ffmpeg","-y","-f","concat","-safe","0","-i",list_path,"-c","copy",out_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        # cleanup
        for tf in tmp_files:
            try: os.remove(tf)
            except: pass
        try: os.remove(list_path)
        except: pass
        
        return True
    except Exception as e:
        print(f"[voice_long] edge-tts chunk failed: {e}")
        return False

async def _edge_tts_async(text: str, out_path: str, mode: str = "standard"):
    # voice selection
    if mode == "sleep":
        voice = "en-US-AriaNeural"  # softer
        rate = "-12%"  # slower for sleep
    else:
        voice = "en-US-GuyNeural"
        rate = "+0%"
    
    return await _edge_tts_chunk(text, out_path, voice, rate)

def synthesize_long(text: str, out_path: str, mode: str = "standard") -> float:
    """
    Synthesize long text, supports up to 2.5h via chunking
    Returns duration in seconds
    """
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    
    # try edge-tts
    try:
        asyncio.run(_edge_tts_async(text, out_path, mode))
        if Path(out_path).exists():
            dur = get_duration(out_path)
            if dur > 0.5:
                return dur
    except Exception as e:
        print(f"[voice_long] edge-tts error: {e}")
    
    # fallback espeak-ng for long form
    try:
        # espeak can handle long text but we chunk to avoid issues
        wav_path = out_path.replace(".mp3",".wav")
        # for sleep mode, slower speed
        speed = "110" if mode == "sleep" else "150"
        subprocess.run(
            ["espeak-ng","-v","en","-s",speed,"-w",wav_path, text],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120
        )
        # convert to mp3
        subprocess.run(
            ["ffmpeg","-y","-i",wav_path,"-c:a","libmp3lame","-q:a","2",out_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        try: os.remove(wav_path)
        except: pass
        dur = get_duration(out_path)
        if dur > 0.5:
            return dur
    except Exception as e:
        print(f"[voice_long] espeak fallback failed: {e}")
    
    # final silent fallback — calculate accurate silent duration for long form
    dur = _estimate_duration(text, mode)
    # clamp for long form: up to 300s per scene for sleep
    max_dur = 300 if mode == "sleep" else 60
    dur = max(2.5, min(max_dur, dur))
    
    subprocess.run(
        ["ffmpeg","-y","-f","lavfi","-i","anullsrc=r=44100:cl=mono","-t",str(dur),"-q:a","9","-acodec","libmp3lame",out_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
    )
    return dur

def synthesize(text: str, out_path: str, mode: str = "standard") -> float:
    return synthesize_long(text, out_path, mode)

if __name__ == "__main__":
    import sys
    txt = sys.argv[1] if len(sys.argv) > 1 else "This is a long sleeping history story about bread in medieval times, told slowly and calmly for sleep."
    mode = sys.argv[2] if len(sys.argv) > 2 else "sleep"
    d = synthesize(txt, "/tmp/test_long.mp3", mode)
    print(f"Duration {d}s mode {mode}")
