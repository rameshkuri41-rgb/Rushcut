"""
Rushcut — script generation.

Two modes, both $0:
1. TEMPLATE MODE (default, always works, no signup): rule-based scene
   structure. Lower ceiling than an LLM but zero dependency, zero cost,
   zero rate limit.
2. LLM MODE (better quality, still free): if a GROQ_API_KEY environment
   variable is set, scenes are written by a free-tier Groq model instead.
   Groq's free tier needs a signup but no card and no payment ever —
   get a key at https://console.groq.com/keys
   This sandbox can't reach api.groq.com (network egress is locked down
   here), so this path is untested in this environment, but it's the
   real code you'd run on your own server / Vercel deployment.
"""
import os
import random
import textwrap

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


def _llm_script(topic: str, n_scenes: int) -> list[dict]:
    """Try Groq's free tier (Llama 3.1) for real script generation."""
    import json
    import re
    import urllib.request

    prompt = f"""Write a {n_scenes}-scene voiceover script for a faceless
long-form YouTube video on: "{topic}"

Rules:
- Scene 1 is a hook, under 3 sentences, no throat-clearing.
- Middle scenes each cover ONE concrete, specific fact or idea (a number,
  a mechanism, a named example) — not a restatement of the topic in
  different words. Specificity here matters because each scene's image
  is generated from its text.
- Final scene is a short close (no "like and subscribe" filler).
- Return ONLY this JSON object, nothing else, no markdown fences:
  {{"scenes": ["scene 1 text", "scene 2 text", ...]}}"""

    body = json.dumps({
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "response_format": {"type": "json_object"},
    }).encode()

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())
    content = data["choices"][0]["message"]["content"]

    try:
        parsed = json.loads(content)
        lines = parsed["scenes"]
    except (json.JSONDecodeError, KeyError, TypeError):
        # model wrapped it in prose/markdown fences — pull the array out
        match = re.search(r"\[.*\]", content, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse Groq response as scenes: {content[:200]}")
        lines = json.loads(match.group(0))

    return [{"id": i + 1, "text": t.strip()} for i, t in enumerate(lines)]


# ---- template mode -------------------------------------------------------

_HOOKS = [
    "Here's something about {topic} almost nobody explains right.",
    "{topic} sounds simple. It isn't — and that's exactly why it works.",
    "If you've ever wondered how {topic} actually works, this is it, start to finish.",
]

_BEATS = [
    "The first thing to understand about {topic} is where it actually comes from — not the version people repeat, the real one.",
    "Most explanations of {topic} skip the part that matters: why it happens at all, not just that it does.",
    "Here's the mechanism behind {topic}, laid out simply, without the jargon that usually gets in the way.",
    "There's a common mistake people make with {topic} — and once you see it, you can't unsee it.",
    "The numbers behind {topic} tell a clearer story than the headlines do.",
    "This is the part of {topic} that changes how you should actually think about it.",
]

_CLOSES = [
    "So that's {topic} — not the simplified version, the real one.",
    "That's the full picture of {topic}, and now you know more than most people ever will.",
    "And that's how {topic} really works, once you strip away the noise.",
]


def _template_script(topic: str, n_scenes: int) -> list[dict]:
    scenes = [random.choice(_HOOKS).format(topic=topic)]
    body_pool = random.sample(_BEATS, k=min(len(_BEATS), n_scenes - 2))
    scenes += [b.format(topic=topic) for b in body_pool]
    while len(scenes) < n_scenes - 1:
        scenes.append(random.choice(_BEATS).format(topic=topic))
    scenes.append(random.choice(_CLOSES).format(topic=topic))
    return [{"id": i + 1, "text": textwrap.fill(t, 90)} for i, t in enumerate(scenes)]


def generate_script(topic: str, n_scenes: int = 6) -> list[dict]:
    if GROQ_API_KEY:
        try:
            return _llm_script(topic, n_scenes)
        except Exception as e:
            print(f"[script_gen] LLM mode failed ({e}), falling back to template mode.")
    return _template_script(topic, n_scenes)


if __name__ == "__main__":
    for s in generate_script("compound interest", 6):
        print(s["id"], "-", s["text"])
