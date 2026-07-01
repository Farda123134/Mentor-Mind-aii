import json
import logging
import traceback
from mentor_mind.utils.ai_helper import call_ai

log = logging.getLogger("MentorMind")


class MemoryAgent:
    PROMPT = """You are Memory Agent.
Write a short motivating progress report.
Include completed tasks, remaining tasks, percentage, encouragement.
Max 100 words."""

    def __init__(self, memory):
        self.memory = memory

    def get_progress(self, topic="", session_id="default"):
        try:
            # Agar topic specify nahi hua, user ka koi bhi active plan dhundo
            if not topic:
                plans = getattr(self.memory, "study_plans", {})
                if plans:
                    topic = list(plans.keys())[0]
                else:
                    return "You don't have any study plans yet! Try: 'Create a 5-day study plan for Python'"

            s = self.memory.get_progress_summary(topic)
            if not s or not s.get("total"):
                return "No active plan found for '" + topic + "'. Create one first: 'Create a study plan for " + topic + "'"

            self.memory.log("MemoryAgent", "get_progress", topic)
            return call_ai(self.PROMPT, "Progress data:\n" + json.dumps(s, indent=2), max_tokens=200)

        except Exception as e:
            log.error("get_progress error: " + str(e))
            traceback.print_exc()
            return "Could not retrieve progress: " + str(e)

    def today_task(self, topic="", session_id="default"):
        try:
            if not topic:
                plans = getattr(self.memory, "study_plans", {})
                if plans:
                    topic = list(plans.keys())[0]
                else:
                    return "You don't have any study plans yet! Try: 'Create a 5-day study plan for Python'"

            task = self.memory.get_today_task(topic)
            if not task:
                return "No task found for '" + topic + "' today. Create a plan first!"
            self.memory.log("MemoryAgent", "today_task", topic)
            return "Today's task for " + topic + ":\n\n" + task

        except Exception as e:
            log.error("today_task error: " + str(e))
            traceback.print_exc()
            return "Could not retrieve today's task: " + str(e)

    def mark_done(self, topic, task):
        try:
            self.memory.mark_complete(topic, task)
            return "Marked complete: '" + task + "'"
        except Exception as e:
            log.error("mark_done error: " + str(e))
            return "Could not mark task complete: " + str(e)
