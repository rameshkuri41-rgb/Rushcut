"""
script_gen_long.py — long-form + sleeping history mode
Generates 5s to 2.5h scripts

Modes:
- short: 3-5 scenes, punchy
- standard: 6-20 scenes, educational (like channel.farm 8-12 min)
- sleep: 30-150 scenes, calm, repetitive, low-stim, for 30min-2.5h sleeping history videos

Sleeping history style: slow, boring in a good way, no cliffhangers, facts, dates, calm narrative, "boring history for sleep"
"""
import os
import json
import random
from typing import List

TEMPLATE_SHORT = [
    "Have you ever wondered {topic}? Let's break it down in seconds.",
    "The core idea: {fact1}. Simple but powerful.",
    "Why it matters: {fact2}. Now you know."
]

TEMPLATE_STANDARD_FACTS = [
    "{topic} is fascinating because it changes how we think about {related}.",
    "At its core, {fact1}. This principle appears everywhere from daily life to big history.",
    "Consider this: {fact2}. The numbers behind it are surprising.",
    "What most people miss is {fact3}. Once you see it, you can't unsee it.",
    "The history is wild — {fact4}. It started as a small idea.",
    "Today, {fact5}. And the implications are just beginning.",
    "So next time you think about {topic}, remember: small rules compound into big outcomes."
]

SLEEPING_HISTORY_TOPICS = {
    "boring history": "calm, slow, factual, no excitement",
    "why we sleep": "gentle science",
    "ancient rome daily life": "quiet, routine-focused",
    "history of bread": "soothing, methodical",
}

SLEEPING_TEMPLATES = [
    "In the quiet hours of {era}, people would {routine}. It was a simple time, with {detail}.",
    "Historians note that {fact1}. This continued for centuries, largely unchanged.",
    "The process of {process} was slow and methodical. First, {step1}. Then, {step2}. It took hours.",
    "By {time_period}, {fact2}. Life moved at a different pace. There was no rush.",
    "Consider the {object}. Made of {material}, it was used daily for {purpose}. Every household had one.",
    "As night fell, {night_routine}. The {sound} would drift through the village, and people would {calm_action}.",
    "What is often forgotten is {obscure_fact}. It seems small now, but it shaped daily life.",
    "The {season} brought {seasonal_change}. People adapted by {adaptation}. It was expected, year after year.",
    "Records from {year} show {record}. Nothing dramatic happened that day, which was, in itself, a kind of peace.",
    "And so, {topic} continued, quiet and steady, much like the {metaphor} that {does_what} in the background of history."
]

def _template_facts(topic: str, n: int) -> List[dict]:
    facts = [
        f"{topic} compounds over time — small inputs become huge outputs",
        f"most people underestimate how {topic} works because they think linearly",
        f"the math behind {topic} is just exponential growth, but intuition fails",
        f"it was first described in detail by merchants and mathematicians centuries ago",
        f"today, understanding {topic} is the difference between stress and freedom",
        f"the key is consistency, not intensity — boring works better than brilliant",
        f"{topic} shows up in investing, learning, health, and relationships",
        f"historical examples of {topic} go back to ancient Babylon and compound interest tablets",
        f"modern studies show people who grasp {topic} make better long-term decisions",
        f"in a world of instant results, {topic} rewards patience quietly"
    ]
    random.shuffle(facts)
    return facts[:n+2]

def _sleep_facts(topic: str, n: int) -> List[dict]:
    # generate calm, repetitive facts
    eras = ["the 14th century", "ancient Mesopotamia", "medieval England", "the early 1800s", "the quiet years of the 1920s"]
    routines = ["grind grain by hand", "mend clothes by firelight", "sweep the hearth", "fetch water from the well", "prepare the evening stew"]
    details = ["the smell of woodsmoke", "the sound of a distant bell", "the cool stone floor", "the soft light of oil lamps"]
    facts = []
    for i in range(n):
        era = random.choice(eras)
        routine = random.choice(routines)
        detail = random.choice(details)
        fact = random.choice(SLEEPING_TEMPLATES).format(
            topic=topic,
            era=era,
            routine=routine,
            detail=detail,
            fact1=f"in {era}, {routine} was done every day without much thought",
            fact2=f"people in {era} spent most of their time on simple tasks",
            process=routine,
            step1="they would gather what was needed",
            step2="they would work slowly, with care",
            object="wooden bowl",
            material="oak",
            purpose=routine,
            time_period=era,
            night_routine="families would sit quietly",
            sound="wind",
            calm_action="fall asleep early",
            obscure_fact=f"the average person owned only a few items",
            season="winter",
            seasonal_change="longer nights",
            adaptation="staying indoors and telling stories",
            year="1347",
            record="a list of grain stores and not much else",
            metaphor="river",
            does_what="flows without hurry"
        )
        facts.append(fact)
    return facts

def generate_script_long(topic: str, n_scenes: int = 10, mode: str = "standard") -> List[dict]:
    """
    mode: short, standard, sleep, ultra (for 2.5h)
    n_scenes: 1 to 200
    Returns scenes with text calibrated for duration
    """
    mode = mode.lower()
    
    # try Groq first for standard/sleep
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key and mode in ("standard", "sleep"):
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            
            if mode == "sleep":
                prompt = f"""Write a boring, calm, sleep-inducing history script about '{topic}'.
Style: extremely calm, slow, monotonous in a soothing way, no excitement, no cliffhangers, no questions. Factual, repetitive, low-stim. Like "boring history for sleep" YouTube.
Produce exactly {n_scenes} scenes. Each scene 2-3 long sentences, 60-90 words, calm tone.
Return JSON: {{"scenes": [{{"text": "...", "image_prompt": "calm, dark, muted, boring history illustration, ..."}}]}}
Topic: {topic}
"""
            else:
                prompt = f"""Write an educational YouTube script about '{topic}' in {n_scenes} scenes.
Each scene 2-3 sentences, 40-60 words, clear, engaging.
Return JSON: {{"scenes": [{{"text": "...", "image_prompt": "..."}}]}}
"""
            
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7 if mode != "sleep" else 0.3,
                max_tokens=4000 if n_scenes <= 20 else 8000
            )
            content = resp.choices[0].message.content
            # extract json
            import re
            m = re.search(r'\{.*\}', content, re.S)
            if m:
                data = json.loads(m.group(0))
                scenes = []
                for i, s in enumerate(data.get("scenes", [])[:n_scenes], 1):
                    scenes.append({"id": i, "text": s.get("text",""), "image_prompt": s.get("image_prompt", f"{topic} scene {i}")})
                if len(scenes) >= max(2, n_scenes//2):
                    return scenes
        except Exception as e:
            print(f"[script_gen] Groq failed, fallback: {e}")

    # fallback templates
    if mode == "short":
        texts = [t.format(topic=topic, fact1=f"{topic} is about time", fact2=f"{topic} rewards patience") for t in TEMPLATE_SHORT[:n_scenes]]
        facts = texts
    elif mode == "sleep":
        facts = _sleep_facts(topic, n_scenes)
    else: # standard
        base_facts = _template_facts(topic, n_scenes)
        facts = base_facts[:n_scenes]
        # pad if needed
        while len(facts) < n_scenes:
            facts.extend(base_facts[:n_scenes-len(facts)])

    scenes = []
    for i, fact in enumerate(facts[:n_scenes], 1):
        # for sleep, image prompt is dark, muted
        if mode == "sleep":
            img_prompt = f"boring history, calm, dark muted, {topic}, minimal, sleep, night, oil lamp, vintage illustration, low saturation --ar 16:9"
        else:
            img_prompt = f"{topic}, scene {i}/{n_scenes}, {fact[:60]}, cinematic documentary"
        
        scenes.append({"id": i, "text": fact, "image_prompt": img_prompt})
    
    return scenes

def calculate_duration(n_scenes: int, mode: str, wpm: int = 145) -> float:
    """Estimate total duration in seconds"""
    if mode == "short":
        words_per_scene = 25
    elif mode == "sleep":
        words_per_scene = 75  # slower speech
        wpm = 110  # slower for sleep
    else:
        words_per_scene = 55
    
    total_words = n_scenes * words_per_scene
    minutes = total_words / wpm
    return minutes * 60

if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "history of bread"
    mode = sys.argv[2] if len(sys.argv) > 2 else "sleep"
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    scenes = generate_script_long(topic, n, mode)
    print(f"Mode {mode}, {len(scenes)} scenes, est {calculate_duration(len(scenes), mode)/60:.1f} min")
    for s in scenes[:3]:
        print(s["id"], s["text"][:100])
