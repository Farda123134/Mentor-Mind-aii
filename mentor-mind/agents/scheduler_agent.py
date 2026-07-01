
import json
import logging
from datetime import datetime
from mentor_mind.utils.ai_helper import call_ai

log = logging.getLogger("MentorMind")

class SchedulerAgent:
    PROMPT = """You are Scheduler Agent.
Write a short daily study reminder with date,
today task, progress status, motivation, one tip.
Max 100 words."""

    def __init__(self, memory):
        self.memory = memory

    def get_daily_brief(self, topic, session_id="default"):
        if topic not in self.memory.study_plans:
            return f"No plan for '{topic}'. Create one first!"
        plan  = self.memory.study_plans[topic]
        start = datetime.fromisoformat(plan.get("start_date", datetime.now().isoformat()))
        day   = (datetime.now() - start).days + 1
        prog  = self.memory.get_progress_summary(topic)
        ctx   = {
            "topic"  : topic,
            "date"   : datetime.now().strftime("%Y-%m-%d"),
            "day"    : day,
            "total"  : plan.get("total_days", 0),
            "task"   : self.memory.get_today_task(topic) or "All done!",
            "done"   : len(prog.get("completed", [])),
            "left"   : len(prog.get("pending", [])),
            "percent": prog.get("percent", 0)
        }
        self.memory.log("SchedulerAgent", "daily_brief", topic)
        return call_ai(self.PROMPT, f"Generate reminder:\n{json.dumps(ctx, indent=2)}", max_tokens=200)
