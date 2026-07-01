
import logging
import traceback
from mentor_mind.utils.ai_helper import call_ai

log = logging.getLogger("MentorMind")


class GeneralAgent:
    """
    Fallback agent — koi bhi sawaal answer kare.
    """
    PROMPT = """You are MENTOR MIND AI — a friendly, helpful assistant.
Answer any question clearly and concisely.
If the topic is study-related, suggest creating a study plan.
Keep response under 300 words."""

    def __init__(self, memory):
        self.memory = memory

    def answer(self, question: str, history=None) -> str:
        """Koi bhi sawaal ka jawab do."""
        try:
            self.memory.log("GeneralAgent", "answer", question[:50])

            # Context banao from history
            context = ""
            if history:
                recent  = history[-4:]
                context = "\nPrevious conversation:\n"
                for msg in recent:
                    role    = "User" if msg.get("role") == "user" else "Assistant"
                    message = msg.get("message", "")[:150]
                    context += f"{role}: {message}\n"

            full_prompt = question + context
            result      = call_ai(self.PROMPT, full_prompt, max_tokens=600)

            # Error check
            if result.startswith("Error:"):
                log.error(f"GeneralAgent got error from call_ai: {result}")
                return f"Sorry, AI service error: {result}"

            return result

        except Exception as e:
            tb = traceback.format_exc()
            log.error(f"GeneralAgent.answer crashed: {e}\n{tb}")
            return f"General Agent error: {str(e)}"

    def answer_with_suggestion(self, question: str, history=None) -> str:
        """Jawab do + study suggestion."""
        try:
            response = self.answer(question, history)

            if response.startswith("Sorry,") or response.startswith("Error"):
                return response

            study_kw = ["learn","explain","what is","how does","teach","understand","study"]
            if any(k in question.lower() for k in study_kw):
                response += (
                    "\n\n💡 Tip: Agar is topic ko deeply seekhna ho, "
                    "poochho: \'Create a study plan for [topic]\'"
                )
            return response

        except Exception as e:
            tb = traceback.format_exc()
            log.error(f"GeneralAgent.answer_with_suggestion crashed: {e}\n{tb}")
            return f"Error: {str(e)}"
