
import re
import time
import logging
import traceback

from mentor_mind.utils.ai_helper   import call_ai
from mentor_mind.utils.json_helper import safe_parse_json, safe_int

log = logging.getLogger("MentorMind")


class CoordinatorAgent:
    """
    AI Study Tutor coordinator.
    Sirf study-related kaam karta hai.
    Casual messages ko politely redirect karta hai.
    """

    ROUTER_PROMPT = """You are a router for an AI STUDY TUTOR (not a general chatbot).
Return ONLY JSON no markdown:
{"intent":"...","agents":["TEACHER"],"topic":"...","days":null,"subtopic":null,"quiz_count":null,"is_study_related":true}

Rules:
TEACHER   = explain, teach, what is, how does (study topics only)
PLANNER   = plan, schedule, days, divide into days
MEMORY    = progress, today, done, status
TESTER    = quiz, test, mcq, practice questions
SCHEDULER = remind, daily brief
RAG       = my notes, document, uploaded, from notes

If the message is casual conversation (hi, hello, thanks, ok, bye, how are you)
and NOT a study/learning request, set is_study_related=false and agents=[].

days must be integer or null. quiz_count must be integer or null."""

    # Casual / greeting phrases — never need an agent
    CASUAL_PATTERNS = [
        r"^\s*(hi|hello|hey|hii+|salam|assalam.*)\s*[!.]*\s*$",
        r"^\s*(thanks?|thank you|shukriya|ok+|okay)\s*[!.]*\s*$",
        r"^\s*(bye|goodbye|see you|good ?night)\s*[!.]*\s*$",
        r"^\s*(how are you|whats up|what\'s up)\s*\??\s*$",
        r"^\s*(yes|no|yeah|nah|sure|cool|nice)\s*[!.]*\s*$",
    ]

    KEYWORDS = {
        "TEACHER"  : ["teach","explain","what is","what are","how does","describe","define"],
        "PLANNER"  : ["plan","schedule","days","week","roadmap","divide","create a plan"],
        "MEMORY"   : ["progress","done","today","status","complete","history"],
        "TESTER"   : ["quiz","test","question","mcq","exam","practice"],
        "SCHEDULER": ["remind","reminder","daily","what should i study"],
        "RAG"      : ["my notes","document","pdf","uploaded","from notes","my document"],
    }

    def __init__(self, memory):
        self.memory = memory
        from mentor_mind.agents.teacher_agent   import TeacherAgent
        from mentor_mind.agents.planner_agent   import PlannerAgent
        from mentor_mind.agents.memory_agent    import MemoryAgent
        from mentor_mind.agents.tester_agent    import TesterAgent
        from mentor_mind.agents.scheduler_agent import SchedulerAgent

        self.teacher   = TeacherAgent(memory)
        self.planner   = PlannerAgent(memory)
        self.mem_agent = MemoryAgent(memory)
        self.tester    = TesterAgent(memory)
        self.scheduler = SchedulerAgent(memory)

        # RAG optional
        self.rag_agent = None
        try:
            from mentor_mind.rag.rag_engine import RAGEngine
            from mentor_mind.rag.rag_agent  import RAGAgent
            rag_engine     = RAGEngine()
            self.rag_agent = RAGAgent(memory, rag_engine)
        except Exception as e:
            log.warning("RAG not available: " + str(e))

        log.info("CoordinatorAgent ready — study tutor mode")

    def _is_casual_message(self, msg: str) -> bool:
        """Check karo kya yeh sirf casual greeting hai."""
        ml = msg.lower().strip()
        for pattern in self.CASUAL_PATTERNS:
            if re.match(pattern, ml):
                return True
        # Bohat chota message bina kisi study keyword ke
        if len(ml.split()) <= 2:
            has_study_kw = any(
                kw in ml for kws in self.KEYWORDS.values() for kw in kws
            )
            if not has_study_kw:
                return True
        return False

    def _fallback(self, msg: str) -> dict:
        ml     = msg.lower()
        agents = [a for a, kws in self.KEYWORDS.items() if any(k in ml for k in kws)]

        if not agents:
            # Koi study keyword nahi mila
            return {
                "intent"          : "off_topic",
                "agents"          : [],
                "topic"           : "",
                "days"            : None,
                "subtopic"        : None,
                "quiz_count"      : 3,
                "is_study_related": False
            }

        stop  = {"teach","explain","plan","quiz","me","about","what","is","how","a",
                  "the","create","for","in","days","day","you","i","want"}
        words = [w for w in ml.split() if w not in stop]
        topic = " ".join(words[:4]).title() or "General"
        dm    = re.search(r"(\d+)\s*day", ml)
        qm    = re.search(r"(\d+)\s*(question|quiz|mcq)", ml)

        return {
            "intent"          : "keyword",
            "agents"          : agents,
            "topic"           : topic,
            "days"            : int(dm.group(1)) if dm else None,
            "subtopic"        : None,
            "quiz_count"      : int(qm.group(1)) if qm else 3,
            "is_study_related": True
        }

    def _route(self, msg: str) -> dict:
        # Casual message — skip AI call, direct response
        if self._is_casual_message(msg):
            return {
                "intent"          : "casual",
                "agents"          : [],
                "topic"           : "",
                "days"            : None,
                "subtopic"        : None,
                "quiz_count"      : 3,
                "is_study_related": False
            }

        try:
            raw   = call_ai(self.ROUTER_PROMPT, msg, max_tokens=150)
            route = safe_parse_json(raw)
            if route and "agents" in route:
                return route
        except Exception as e:
            log.error("Routing error: " + str(e))

        return self._fallback(msg)

    def handle(self, msg: str, session_id: str = "default") -> dict:
        log.info("Request: " + msg[:60])
        t0    = time.time()
        route = self._route(msg)

        is_study_related = route.get("is_study_related", True)
        agents = route.get("agents", [])
        if isinstance(agents, str):
            agents = [agents]

        topic = route.get("topic") or ""
        if isinstance(topic, list):
            topic = topic[0] if topic else ""

        days = route.get("days")
        if isinstance(days, list):
            days = days[0] if days else None
        if days is not None:
            try: days = int(days)
            except: days = None

        sub = route.get("subtopic") or ""
        if isinstance(sub, list):
            sub = sub[0] if sub else ""

        qcount = route.get("quiz_count") or 3
        try: qcount = int(qcount)
        except: qcount = 3

        results = {
            "route"      : route,
            "agents_used": []
        }

        # ── OFF-TOPIC HANDLING — no agent called ─────────
        if not is_study_related or not agents:
            results["general"] = (
                "I'm MENTOR MIND AI — a dedicated Study Tutor. "
                "Please ask me a study-related question, like: "
                "'Teach me Python', 'Create a 5-day study plan', "
                "or 'Quiz me on AI'."
            )
            results["route"]["topic"] = ""
            results["final_response"] = results["general"]
            return results

        # ── STUDY-RELATED — route to correct agent ───────
        for agent in agents:
            try:
                if agent == "TEACHER":
                    results["teaching"] = self.teacher.teach(topic, sub)
                    results["agents_used"].append("TEACHER")

                elif agent == "PLANNER":
                    if not days:
                        dm = re.search(r"(\d+)", msg)
                        days = int(dm.group(1)) if dm else 5
                    results["plan"] = self.planner.create_plan(topic, days, session_id)
                    results["agents_used"].append("PLANNER")

                elif agent == "MEMORY":
                    if "today" in msg.lower():
                        results["today"] = self.mem_agent.today_task(topic, session_id)
                    else:
                        results["memory"] = self.mem_agent.get_progress(topic, session_id)
                    results["agents_used"].append("MEMORY")

                elif agent == "TESTER":
                    results["quiz"] = self.tester.generate_quiz(topic, qcount)
                    results["agents_used"].append("TESTER")

                elif agent == "SCHEDULER":
                    results["schedule"] = self.scheduler.get_daily_brief(topic, session_id)
                    results["agents_used"].append("SCHEDULER")

                elif agent == "RAG" and self.rag_agent:
                    results["general"] = self.rag_agent.answer_from_docs(msg, session_id)
                    results["agents_used"].append("RAG")

            except Exception as e:
                log.error(agent + " error: " + str(e))
                traceback.print_exc()
                results[agent.lower() + "_error"] = str(e)

        results["route"]["topic"] = topic or ""
        return results
