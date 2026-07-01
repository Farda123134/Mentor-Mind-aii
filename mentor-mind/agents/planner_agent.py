
import re
import json
import logging
from datetime import datetime
from mentor_mind.utils.ai_helper   import call_ai
from mentor_mind.utils.json_helper import safe_parse_json

log = logging.getLogger("MentorMind")

class PlannerAgent:
    PROMPT = """You are a study Planner Agent.
Return ONLY valid JSON no markdown no backticks:
{"topic":"...","total_days":N,"schedule":[{"day":1,"task":"specific task","type":"learn","difficulty":"beginner"}]}
Types: learn/practice/revision/project
Difficulty: beginner/intermediate/advanced
Rules: progress easy to hard, revision every 3-4 days, last day is project."""

    def __init__(self, memory):
        self.memory = memory

    def create_plan(self, topic, days, session_id="default"):
        from mentor_mind.utils.json_helper import safe_int
        days = safe_int(days, 5)
        self.memory.log("PlannerAgent", "create_plan", f"{topic} ({days}d)")
        raw  = call_ai(self.PROMPT, f"Create a {days}-day plan for: {topic}", max_tokens=1500)
        plan = safe_parse_json(raw, fallback={
            "topic"     : topic,
            "total_days": days,
            "schedule"  : [
                {"day": i+1, "task": f"Study {topic} — Day {i+1}",
                 "type": "learn", "difficulty": "beginner"}
                for i in range(days)
            ]
        })
        plan["start_date"] = datetime.now().isoformat()
        self.memory.save_plan(topic, plan)
        return plan
