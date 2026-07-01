
import json
import logging
from mentor_mind.utils.ai_helper   import call_ai
from mentor_mind.utils.json_helper import safe_parse_json, safe_int

log = logging.getLogger("MentorMind")

class TesterAgent:
    QUIZ_PROMPT = """Return ONLY valid JSON no markdown no backticks.
Schema: {{"topic":"...","questions":[{{"id":1,"question":"...","options":{{"A":"...","B":"...","C":"...","D":"..."}},"answer":"A","explanation":"..."}}]}}
Generate {count} questions about {topic}."""

    EVAL_PROMPT = """Evaluate student MCQ answers.
Give score X/Y, correct answers with praise,
wrong answers with explanation, study tips, verdict.
Max 250 words."""

    def __init__(self, memory):
        self.memory = memory

    def generate_quiz(self, topic, count=3):
        count = safe_int(count, 3)
        self.memory.log("TesterAgent", "generate_quiz", f"{topic} ({count}q)")
        prompt = self.QUIZ_PROMPT.format(topic=topic, count=count)
        raw    = call_ai(prompt, f"Generate {count} MCQs about {topic}", max_tokens=1200)
        return safe_parse_json(raw, fallback={
            "topic": topic,
            "questions": [{
                "id": 1, "question": f"What is {topic}?",
                "options": {"A":"A concept","B":"A tool","C":"A language","D":"A framework"},
                "answer": "A", "explanation": f"{topic} is a fundamental concept."
            }]
        })

    def evaluate(self, quiz, answers):
        self.memory.log("TesterAgent", "evaluate", quiz.get("topic",""))
        results = [
            {"question": q["question"], "user": answers.get(str(q["id"]),""),
             "correct": q["answer"], "ok": answers.get(str(q["id"]),"") == q["answer"],
             "explain": q["explanation"]}
            for q in quiz.get("questions", [])
        ]
        return call_ai(self.EVAL_PROMPT, json.dumps({"topic":quiz["topic"],"results":results}), max_tokens=300)
