
import logging
from mentor_mind.utils.ai_helper import call_ai

log = logging.getLogger("MentorMind")

class TeacherAgent:
    PROMPT = """You are an expert Teacher Agent.
Explain topics clearly with:
OVERVIEW: 2-3 sentence summary
CONCEPTS: bullet list of key ideas
ANALOGY: one simple real-world comparison
STEPS: numbered step-by-step explanation
TAKEAWAY: one sentence summary
Keep response under 400 words."""

    def __init__(self, memory):
        self.memory = memory

    def teach(self, topic, subtopic="", context=""):
        subject = f"{topic} — {subtopic}" if subtopic else topic
        self.memory.log("TeacherAgent", "teach", subject)
        prompt = self.PROMPT
        if context:
            prompt += f"\n\nContext: {context[:300]}"
        return call_ai(prompt, f"Teach me about: {subject}", max_tokens=600)
