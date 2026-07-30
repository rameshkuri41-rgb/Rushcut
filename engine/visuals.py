"""
Rushcut — scene visuals. $0, two tiers:

1. Pollinations.ai: free, keyless, no signup image generation over a
   plain HTTPS GET. This is the real "good" free image tier.
2. PIL scene cards: fully offline generated cards in Rushcut's own
   brand style (dark background, acid-green accents, topic text).
   Used automatically if Pollinations can't be reached — guarantees
   the pipeline still produces real, on-brand visuals with zero
   network dependency.
"""
import os
import re
import textwrap
import urllib.request
import urllib.parse

from PIL import Image, ImageDraw, ImageFont

# Words that carry no visual information — spoken narration is full of
# these ("here's something about", "you've", "actually") and they make
# weak image prompts if passed through raw.
_FILLER = re.compile(
    r"\b(here's|here is|something about|almost nobody|explains right|"
    r"sounds simple|isn't|and that's exactly why it works|"
    r"if you've ever wondered how|actually works|this is it|"
    r"start to finish|the first thing to understand about|"
    r"is where it actually comes from|not the version people repeat|"
    r"the real one|most explanations of|skip the part that matters|"
    r"why it happens at all|not just that it does|"
    r"here's the mechanism behind|laid out simply|"
    r"without the jargon that usually gets in the way|"
    r"there's a common mistake people make with|"
    r"and once you see it, you can't unsee it|"
    r"the numbers behind|tell a clearer story than the headlines do|"
    r"this is the part of|that changes how you should actually think about it|"
    r"so that's|not the simplified version|"
    r"that's the full picture of|and now you know more than most people ever will|"
    r"and that's how|really works, once you strip away the noise)\b",
    re.IGNORECASE,
)

STYLE_SUFFIX = "cinematic documentary photo, dark moody studio lighting, photorealistic, no text, no watermark"


def build_visual_prompt(scene_text: str, topic: str) -> str:
    """Turn a spoken narration line into a usable image-generation prompt:
    strip narration filler, keep the concrete subject matter, anchor it
    to the topic, and add a consistent visual style so scenes look like
    one channel instead of six random images."""
    stripped = _FILLER.sub("", scene_text)
    stripped = re.sub(r"\s+", " ", stripped)
    stripped = re.sub(r"\s*[,:;]\s*", " ", stripped)  # leftover punctuation from stripped clauses
    stripped = stripped.strip(" ,.—-:")
    if len(stripped) < 12:  # filler stripped almost everything, e.g. a pure hook line
        stripped = topic
    return f"{stripped}, illustrating {topic}, {STYLE_SUFFIX}"

W, H = 1280, 720
BG = (12, 13, 10)
ACID = (212, 255, 79)
DIM = (138, 141, 124)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def _font(path, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, path), size)


def _try_pollinations(prompt: str, out_path: str) -> bool:
    try:
        q = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{q}?width={W}&height={H}&nologo=true"
        req = urllib.request.Request(url, headers={"User-Agent": "Rushcut/1.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = resp.read()
        with open(out_path, "wb") as f:
            f.write(data)
        img = Image.open(out_path)
        img.verify()
        return True
    except Exception as e:
        print(f"[visuals] Pollinations unavailable ({e}), using offline scene card.")
        return False


def _scene_card(prompt: str, scene_no: int, total: int, out_path: str):
    """Offline fallback: on-brand generated card, no network required."""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # subtle vertical grid lines, echoes the filmstrip motif
    for x in range(0, W, 64):
        draw.line([(x, 0), (x, H)], fill=(20, 22, 16), width=1)

    # frame number / timecode footer
    tc = f"SCENE {scene_no:02d} / {total:02d}"
    draw.text((36, H - 56), tc, font=_font("DejaVuSansMono.ttf", 20), fill=DIM)

    # acid accent bar
    draw.rectangle([(0, H - 8), (W, H)], fill=ACID)

    # wrapped caption, centered
    wrapped = textwrap.fill(prompt, width=34)
    font = _font("DejaVuSans-Bold.ttf", 46)
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=14, align="center")
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.multiline_text(
        ((W - tw) / 2, (H - th) / 2 - 20), wrapped,
        font=font, fill=(243, 241, 231), spacing=14, align="center",
    )

    # corner accent ticks (editing-suite motif)
    for cx, cy in [(30, 30), (W - 30, 30), (30, H - 30), (W - 30, H - 30)]:
        draw.line([(cx - 14, cy), (cx + 14, cy)], fill=ACID, width=2)
        draw.line([(cx, cy - 14), (cx, cy + 14)], fill=ACID, width=2)

    img.save(out_path)


def get_image(scene_text: str, topic: str, scene_no: int, total: int, out_path: str):
    prompt = build_visual_prompt(scene_text, topic)
    print(f"[visuals] scene {scene_no} prompt: {prompt}")
    ok = _try_pollinations(prompt, out_path)
    if not ok:
        # offline card shows the *subject*, not the visual-prompt style tags
        subject = prompt.split(", illustrating")[0]
        _scene_card(subject, scene_no, total, out_path)


if __name__ == "__main__":
    get_image("The first thing to understand about compound interest is where it actually comes from.",
               "compound interest", 1, 6, "/tmp/visual_test.png")
    print("wrote /tmp/visual_test.png")
