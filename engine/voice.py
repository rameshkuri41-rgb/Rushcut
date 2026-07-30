"""
Rushcut — voice synthesis. $0, two tiers:

1. edge-tts: Microsoft Edge's read-aloud voices, exposed as a free,
   keyless Python package. Natural-sounding, no signup, no cost —
   this is the real "good" free voice. Needs open internet.
2. espeak-ng: fully offline, zero network, always works, robotic.
   Used automatically if edge-tts can't reach the network (like in
   this sandbox) — guarantees the pipeline never has a hard dependency
   on connectivity it doesn't have.
"""
import asyncio
import subprocess
import shutil

EDGE_VOICE = "en-US-GuyNeural"


def _try_edge_tts(text: str, out_mp3: str) -> bool:
    try:
        import edge_tts
    except ImportError:
        return False

    async def _run():
        communicate = edge_tts.Communicate(text, EDGE_VOICE)
        await asyncio.wait_for(communicate.save(out_mp3), timeout=15)

    try:
        asyncio.run(_run())
        import os
        return os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 0
    except Exception as e:
        print(f"[voice] edge-tts unavailable ({e}), using offline fallback.")
        return False


def _espeak_fallback(text: str, out_mp3: str):
    """Fully offline: espeak-ng -> wav -> mp3 via ffmpeg."""
    wav_path = out_mp3.replace(".mp3", ".wav")
    subprocess.run(
        ["espeak-ng", "-v", "en-us+m3", "-s", "165", "-p", "35", text, "-w", wav_path],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-i", wav_path, "-ar", "44100", "-ac", "1", out_mp3],
        check=True, capture_output=True,
    )


def synthesize(text: str, out_mp3: str) -> float:
    """Returns clip duration in seconds."""
    ok = _try_edge_tts(text, out_mp3)
    if not ok:
        if not shutil.which("espeak-ng"):
            raise RuntimeError("Neither edge-tts nor espeak-ng is available.")
        _espeak_fallback(text, out_mp3)

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", out_mp3],
        capture_output=True, text=True, check=True,
    )
    return float(probe.stdout.strip())


if __name__ == "__main__":
    d = synthesize("This is a test of the Rushcut voice engine.", "/tmp/voice_test.mp3")
    print("duration:", d)
